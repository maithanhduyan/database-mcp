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
    from decimal import Decimal
    from datetime import datetime, date
    
    def convert_value(value):
        """Convert non-JSON serializable values"""
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        return value
    
    db = SessionLocal()
    try:
        result = db.execute(text(query), params or {})
        rows = result.fetchall()
        columns = result.keys()
        return [
            {col: convert_value(val) for col, val in zip(columns, row)} 
            for row in rows
        ]
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def execute_command(query: str, params: Optional[dict] = None) -> dict:
    """
    Thực thi các lệnh SQL write operations (INSERT, UPDATE, DELETE, CREATE, ALTER).
    Trả về thông tin về số rows affected và status.
    """
    from sqlalchemy import text
    import re
    
    # Validate SQL command
    query_upper = query.strip().upper()
    
    # Forbidden operations for security
    forbidden_patterns = [
        r'DROP\s+DATABASE',
        r'TRUNCATE\s+DATABASE', 
        r'SHUTDOWN',
        r'EXEC',
        r'EXECUTE',
        r'xp_',
        r'sp_'
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, query_upper):
            raise ValueError(f"Forbidden operation detected: {pattern}")
    
    db = SessionLocal()
    try:
        result = db.execute(text(query), params or {})
        rows_affected = getattr(result, 'rowcount', 0)
        db.commit()
        
        return {
            "status": "success",
            "rows_affected": rows_affected,
            "message": f"Command executed successfully. {rows_affected} rows affected."
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def execute_transaction(queries: list[dict]) -> dict:
    """
    Thực thi nhiều câu lệnh SQL trong một transaction.
    queries: [{"query": "...", "params": {...}}, ...]
    """
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        total_affected = 0
        results = []
        
        for i, query_data in enumerate(queries):
            query = query_data.get("query", "")
            params = query_data.get("params", {})
            
            if not query.strip():
                continue
                
            result = db.execute(text(query), params)
            rows_affected = getattr(result, 'rowcount', 0)
            total_affected += rows_affected
            
            results.append({
                "query_index": i,
                "query": query[:100] + "..." if len(query) > 100 else query,
                "rows_affected": rows_affected
            })
        
        db.commit()
        
        return {
            "status": "success", 
            "total_rows_affected": total_affected,
            "queries_executed": len(results),
            "results": results,
            "message": f"Transaction completed successfully. {total_affected} total rows affected."
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_table_info(table_name: Optional[str] = None) -> dict:
    """
    Lấy thông tin về các bảng trong database.
    Nếu table_name được cung cấp, trả về chi tiết cột của bảng đó.
    """
    from sqlalchemy import text, inspect
    
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        
        if table_name:
            # Thông tin chi tiết về một bảng
            if table_name not in inspector.get_table_names():
                return {"error": f"Table '{table_name}' not found"}
                
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            return {
                "table_name": table_name,
                "columns": columns,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys
            }
        else:
            # Liệt kê tất cả bảng
            tables = inspector.get_table_names()
            return {
                "tables": tables,
                "table_count": len(tables)
            }
    except Exception as e:
        raise e
    finally:
        db.close()


def get_database_info() -> dict:
    """
    Lấy thông tin tổng quan về database hiện tại.
    """
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        # Thông tin database
        db_info = {}
        
        # Lấy database name từ URL
        from app.config import DATABASE_TYPE, DATABASE_URL
        db_info["database_type"] = DATABASE_TYPE
        db_info["database_url"] = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
        
        # Lấy số lượng bảng
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        db_info["table_count"] = len(tables)
        db_info["tables"] = tables
        
        # Thông tin version (tùy database type)
        try:
            if DATABASE_TYPE == "sqlite":
                result = db.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                db_info["version"] = f"SQLite {version}"
            elif DATABASE_TYPE == "postgresql":
                result = db.execute(text("SELECT version()"))
                version = result.scalar()
                if version:
                    db_info["version"] = " ".join(version.split(" ")[0:2])
                else:
                    db_info["version"] = "PostgreSQL Unknown"
            elif DATABASE_TYPE == "mysql":
                result = db.execute(text("SELECT VERSION()"))
                version = result.scalar()
                db_info["version"] = f"MySQL {version}"
        except:
            db_info["version"] = "Unknown"
        
        return db_info
    except Exception as e:
        raise e
    finally:
        db.close()
