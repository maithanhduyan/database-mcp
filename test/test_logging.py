# -*- coding: utf-8 -*-
# File: test_logging.py
"""
Script test để kiểm tra cấu hình logging thống nhất
"""

from app.logger import get_logger, setup_unified_logging
import logging

def test_logging():
    """Test logging configuration"""
    
    # Setup unified logging
    setup_unified_logging()
    
    # Test application logger
    app_logger = get_logger("app.test")
    app_logger.info("Test application logger")
    app_logger.warning("Test warning message")
    app_logger.error("Test error message")
    
    # Test uvicorn-like logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.info("Test uvicorn logger")
    
    # Test SQLAlchemy logger
    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.info("Test SQLAlchemy logger")
    
    # Test root logger
    root_logger = logging.getLogger()
    root_logger.info("Test root logger")
    
    print("Logging test completed. Check app.log and access.log files.")

if __name__ == "__main__":
    test_logging()
