# create_tables.py
from app.database import Base, engine
from app.models import UserInfo  # Ensure this import brings in all models you want created

# Create all tables that haven't been created yet
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")
