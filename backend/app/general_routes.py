import re
from uuid import UUID
from datetime import datetime, timezone
from flask import request, jsonify, Blueprint, current_app
from .database import db
from .models import ChatSession, ChatMessage, FAQIntent, UserInfo
import uuid
import requests

api_routes = Blueprint('api_routes', __name__)
bp = Blueprint('chat', __name__)

# In-memory response storage (replace with DB/Redis in production)
latest_response = {"message": ""}

@bp.route('/chat/response', methods=['POST'])
def receive_response():
    data = request.get_json()
    print("✅ Received from n8n:", data)
    latest_response["message"] = data.get("response", "") or data.get("message", "")

    # Save the bot's response to the database
    try:
        session_id = data.get("sessionId")
        if session_id:
            # Ensure HTML is a string and optionally sanitize/encode if needed
            html_message = str(latest_response["message"])
            save_bot_message(db, session_id, html_message)
    except Exception as e:
        print(f"Error saving bot response: {e}")

    return jsonify({"status": "received", "response": latest_response["message"]}), 200

@bp.route('/chat/latest', methods=['GET'])
def get_latest_response():
    return jsonify(latest_response), 200

def parse_user_info(text):
    parts = [part.strip() for part in text.split(',')]
    if len(parts) == 3:
        name, email, country = parts
        return {"name": name, "email": email, "country": country}
    return None

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def save_user_message(db, session_id, message):
    """Persist a user message to the database."""
    user_message = ChatMessage(
        session_id=session_id,
        sender="user",
        message=message,
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(user_message)
    db.session.commit()

def save_bot_message(db, session_id, message):
    """Persist a bot message to the database."""
    bot_message = ChatMessage(
        session_id=session_id,
        sender="bot",
        message=message,
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(bot_message)
    db.session.commit()

def get_or_create_session(db, session_id, user_id):
    session = db.query(ChatSession).filter_by(session_id=session_id).first()
    if not session:
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            started_at=datetime.now(timezone.utc)
        )
        db.session.add(session)
        db.session.commit()
    return session

def get_or_create_user(db, user_info):
    user = db.query(UserInfo).filter_by(email=user_info["email"]).first()
    if not user:
        user = UserInfo(
            name=user_info["name"],
            email=user_info["email"],
            country=user_info["country"],
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(user)
        db.session.commit()
    return user

@api_routes.route("/api/session", methods=["POST"])
def handle_session():
    try:
        data = request.get_json()
        session_id = data.get("sessionId", "")
        user_id = data.get("userId", "")
        chat_input = data.get("chatInput", "")

        # Handle missing sessionId or userId for new customers
        if not session_id:
            session_id = str(uuid.uuid4())  # Generate a new sessionId
        if not user_id:
            user_id = f"guest_{uuid.uuid4().hex[:8]}"  # Generate a new userId

        if not chat_input:
            return jsonify({"error": "Missing required fields"}), 400

        # Validate session_id
        try:
            session_id = UUID(session_id)
        except ValueError:
            return jsonify({"error": "Invalid session ID format"}), 400

        # Retrieve or create chat session
        session = get_or_create_session(db, session_id, user_id)
        save_user_message(db, session_id, chat_input)

        # Check if user information is already linked to the session
        if session.user_info_id:
            # Forward to n8n webhook
            n8n_url = "http://localhost:5678/webhook-test/returning-user"
            # n8n_url = "http://localhost:5678/webhook/returning-user"
            n8n_response = requests.post(n8n_url, json={
                "chatInput": chat_input,
                "userId": user_id,
                "sessionId": str(session_id)
            })
            bot_data = n8n_response.json()
            if isinstance(bot_data, list) and len(bot_data) > 0:
                bot_response = bot_data[0].get("response", "No response from agent.")
            elif isinstance(bot_data, dict):
                bot_response = bot_data.get("response", "No response from agent.")
            else:
                bot_response = "No response from agent."
            save_bot_message(db, session_id, bot_response)
            return jsonify({"response": bot_response, "nextEndpoint": "/api/session"})

        # Parse and validate user info from input
        user_info = parse_user_info(chat_input)
        if user_info and is_valid_email(user_info["email"]):
            # Look up user by email
            existing_user = db.query(UserInfo).filter_by(email=user_info["email"]).first()
            if not existing_user:
                new_user = UserInfo(
                    name=user_info["name"],
                    email=user_info["email"],
                    country=user_info["country"],
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(new_user)
                db.session.commit()
                user = new_user
            else:
                user = existing_user

            # Link session to user
            session.user_info_id = user.id
            db.session.commit()

            # Respond success
            bot_response = "✅ Thanks! We've saved your information. How can I assist you today?"
            save_bot_message(db, session_id, bot_response)
            return jsonify({
                "response": bot_response,
                "nextEndpoint": "/api/session"
            })

        else:
            # Prompt user to correct format
            bot_response = (
                "👋 Before we continue, please share your **name, email, and country**.\n"
                "Format it like this: `John Smith, john@example.com, Canada`"
            )
            save_bot_message(db, session_id, bot_response)
            return jsonify({"response": bot_response, "sessionId": str(session_id), "userId": user_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_routes.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('sessionId', str(uuid.uuid4()))
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Save user message
    chat_session = ChatSession(
        session_id=session_id,
        message=message,
        sender='user'
    )
    db.session.add(chat_session)
    db.session.commit()
    
    # Forward to n8n webhook
    try:
        response = requests.post(
            current_app.config['N8N_WEBHOOK_URL'],
            json={'message': message, 'sessionId': session_id}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@api_routes.route('/faqs', methods=['GET'])
def get_faqs():
    topic = request.args.get('topic')
    query = FAQIntent.query
    
    if topic:
        query = query.filter(FAQIntent.topic.ilike(f'%{topic}%'))
    
    faqs = query.all()
    return jsonify([faq.to_dict() for faq in faqs])

@api_routes.route('/topics', methods=['GET'])
def get_topics():
    topics = db.session.query(FAQIntent.topic).distinct().all()
    return jsonify([topic[0] for topic in topics])
















