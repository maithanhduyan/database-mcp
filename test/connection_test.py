"""
Test kết nối đồng thời đến SQLite, PostgreSQL, MySQL, tạo bảng users, thực hiện CRUD.
"""

import os
import pytest
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    """
    User model for testing CRUD operations.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

DB_CONFIGS = [
    {
        "name": "sqlite",
        "url": "sqlite:///./test_sqlite.db"
    },
    {
        "name": "postgres",
        "url": os.getenv("POSTGRES_URL", "postgresql+psycopg2://user:password@localhost:5432/testdb")
    },
    {
        "name": "mysql",
        "url": os.getenv("MYSQL_URL", "mysql+pymysql://user:password@localhost:3306/testdb")
    }
]

def setup_db(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def test_crud():
    for config in DB_CONFIGS:
        engine = create_engine(config["url"], echo=True, future=True)
        Session = sessionmaker(bind=engine)
        setup_db(engine)
        session = Session()
        # Create
        user = User(name="Test User", email=f"test_{config['name']}@example.com")
        session.add(user)
        session.commit()
        # Read
        user_db = session.query(User).filter_by(email=f"test_{config['name']}@example.com").first()
        assert user_db is not None
        # Update
        user_db.name = "Updated User"
        session.commit()
        updated = session.query(User).filter_by(name="Updated User").first()
        assert updated is not None
        # Delete
        session.delete(updated)
        session.commit()
        deleted = session.query(User).filter_by(email=f"test_{config['name']}@example.com").first()
        assert deleted is None
        session.close()

if __name__ == "__main__":
    test_crud()
    print("Test CRUD cho 3 database hoàn tất.")
