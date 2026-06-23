"""
Database Seeder — creates a default admin user on first run.
Run with: python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from application.providers.database import SessionLocal
from application.repositories.user_repository import UserRepository
from application.src.models.user_model import UserRole


def seed():
    db = SessionLocal()
    try:
        repo = UserRepository(db)

        # Create admin user if not exists
        if not repo.get_by_username("admin"):
            repo.create_user(username="admin", plain_password="admin123", role=UserRole.admin)
            print("✅  Admin user created  →  username: admin  |  password: admin123")
        else:
            print("ℹ️   Admin user already exists, skipping.")

        # Create a sample operator user
        if not repo.get_by_username("operator"):
            repo.create_user(username="operator", plain_password="operator123", role=UserRole.operator)
            print("✅  Operator user created  →  username: operator  |  password: operator123")
        else:
            print("ℹ️   Operator user already exists, skipping.")

    finally:
        db.close()

    print("\n🚀  Seeding complete. You can now log in at POST /auth/login")


if __name__ == "__main__":
    seed()
