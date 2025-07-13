"""
Module thiết lập kết nối database sử dụng SQLAlchemy.
"""

from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator, Optional
import uuid

from app.config import DATABASE_URL


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

engine = create_engine(DATABASE_URL, echo=True, future=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def init_db() -> None:
    """
    Khởi tạo database và tạo bảng users nếu chưa có.
    """
    Base.metadata.create_all(engine)

def get_db() -> Generator[Session, None, None]:
    """
    Tạo session kết nối database, dùng cho truy vấn.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_query(query: str, params: Optional[dict] = None) -> list[dict]:
    """
    Thực thi truy vấn SELECT SQLAlchemy, trả về dữ liệu dạng list[dict].
    """
    from sqlalchemy import text
    db = SessionLocal()
    try:
        result = db.execute(text(query), params or {})
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
