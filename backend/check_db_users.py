import sys
import os

# Add the parent directory to sys.path to allow importing from 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("NO_USERS_FOUND")
        else:
            for u in users:
                print(f"ID={u.id} | username={u.username} | role={u.role} | active={u.is_active}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
