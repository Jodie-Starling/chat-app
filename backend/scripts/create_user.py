"""
Script to create a new user in the database.
Usage: python create_user.py <username> <password>
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys

# --- Ensure project imports work regardless of execution location ---
here = os.path.dirname(__file__)
parent = os.path.abspath(os.path.join(here, os.pardir))
if parent not in sys.path:
    sys.path.insert(0, parent)

from models import SessionLocal, User, get_password_hash, init_db


def main():
    """Create a new user in the database from CLI arguments."""

    if len(sys.argv) < 3:
        print("Usage: python create_user.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    # Ensure database and tables are initialized
    init_db()

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"User '{username}' already exists")
            return

        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            role="user"
        )
        db.add(user)
        db.commit()
        print(f"✅ Created user '{username}' successfully")

    finally:
        db.close()


if __name__ == "__main__":
    main()