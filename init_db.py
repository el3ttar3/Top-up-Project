from app import app, supabase
from models import db
from datetime import datetime

def init_supabase():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        # Create a test user
        user_response = supabase.table('users').insert({
            'username': f'test_user_{timestamp}',
            'email': f'test_{timestamp}@example.com',
            'password': 'test_password'
        }).execute()

        if user_response.data:
            print("Successfully created test user")
            # Clean up test data
            user_id = user_response.data[0]['id']
            supabase.table('users').delete().eq('id', user_id).execute()
            print("Successfully cleaned up test data")
            return True
        return False
    except Exception as e:
        print(f"Error initializing Supabase tables: {str(e)}")
        return False

def init_db():
    with app.app_context():
        # Initialize SQLite database
        db.create_all()
        print("Local SQLite database initialized successfully!")
        
        # Initialize Supabase tables
        if init_supabase():
            print("All databases initialized successfully!")
        else:
            print("Warning: Supabase initialization failed!")

if __name__ == "__main__":
    init_db() 