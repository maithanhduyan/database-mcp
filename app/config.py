# app/config.py
# Configuration file for the application
import os

# JWT Configuration
JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY","your-super-secret-jwt-key-change-in-production")

# MCP API Key for VS Code integration
MCP_API_KEY= os.getenv("MCP_API_KEY", "mcp-api-key-2025-super-secure-token")

# Đọc biến môi trường để chọn database
SQLITE_URL = "sqlite:///./test.db"
POSTGRES_URL = "postgresql+psycopg2://user:password@localhost:5432/testdb"
MYSQL_URL = "mysql+pymysql://user:password@localhost:3306/testdb"

# Lựa chọn database qua biến môi trường DATABASE_TYPE
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")


if DATABASE_TYPE == "postgres":
    DATABASE_URL = os.getenv("POSTGRES_URL", POSTGRES_URL)
elif DATABASE_TYPE == "mysql":
    DATABASE_URL = os.getenv("MYSQL_URL", MYSQL_URL)
else:
    DATABASE_URL = SQLITE_URL
