from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Attempt to run a basic query
        db.session.execute(text("SELECT 1"))
        print("\n✅ SUCCESS: Your app is connected to the Supabase database!\n")
    except Exception as e:
        print("\n❌ ERROR: Could not connect to the database.")
        print(f"Details: {e}\n")