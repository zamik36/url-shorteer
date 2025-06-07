import argparse
import sys
from getpass import getpass
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.postgres import PostgresUserRepository
from app.domain.entities import User
from app.core.auth import get_password_hash

sys.path.append('.')


def main(username: str, password: str):
    print("Initializing DB session...")
    db = SessionLocal()
    repo = PostgresUserRepository(db)
    
    if repo.get_by_username(username):
        print(f"Error: User '{username}' already exists.")
        db.close()
        return

    hashed_password = get_password_hash(password)
    user = User(id=None, username=username, hashed_password=hashed_password)
    repo.add(user)
    print(f"User '{username}' created successfully.")
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new admin user.")
    parser.add_argument("username", type=str, help="The username for the new user.")
    args = parser.parse_args()

    password = getpass("Enter password: ")
    password_confirm = getpass("Confirm password: ")

    if not password:
        print("Error: Password cannot be empty.")
    elif password != password_confirm:
        print("Error: Passwords do not match.")
    else:
        main(username=args.username, password=password)