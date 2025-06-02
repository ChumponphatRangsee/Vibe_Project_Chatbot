import sys
import os
from app.database import engine, Base
from app import create_app

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = create_app()

# Create all tables
Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
