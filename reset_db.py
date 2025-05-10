from app import create_app, db
from app.init_db import init_db

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    # Create all tables
    db.create_all()
    # Initialize with sample data
    init_db()
    print("Database has been reset successfully!") 