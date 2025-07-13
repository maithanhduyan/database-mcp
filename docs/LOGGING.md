# Unified Logging Configuration

## Tổng quan

Hệ thống logging thống nhất đã được cấu hình để kết hợp logging của uvicorn và application thành một cấu hình duy nhất.

## Cấu hình

### File logs được tạo:
- `app.log`: Chứa tất cả logs từ application, uvicorn server, SQLAlchemy
- `access.log`: Chứa access logs của HTTP requests

### Logger categories:

1. **Root logger (`""`)**: Logs chung của application
2. **uvicorn**: Logs từ uvicorn server 
3. **uvicorn.error**: Error logs từ uvicorn
4. **uvicorn.access**: Access logs từ HTTP requests (vào access.log)
5. **fastapi**: Logs từ FastAPI framework
6. **sqlalchemy.engine**: Logs từ SQLAlchemy ORM (chỉ vào file)
7. **app**: Application-specific logs

### Formatters:

- **default**: Format chuẩn cho application logs
  ```
  %(asctime)s - %(name)s - %(levelname)s - %(message)s
  ```

- **access**: Format đặc biệt cho access logs
  ```
  %(asctime)s - %(name)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s
  ```

## Sử dụng

### Trong application code:
```python
from app.logger import get_logger

logger = get_logger(__name__)
logger.info("Your message here")
```

### Khởi động server:
```python
from app.logger import setup_unified_logging, UNIFIED_LOGGING_CONFIG

# Setup logging trước khi tạo logger
setup_unified_logging()

# Sử dụng trong uvicorn
uvicorn.run(
    app, 
    host="0.0.0.0", 
    port=8000,
    log_config=UNIFIED_LOGGING_CONFIG,
    access_log=True
)
```

## Lợi ích

1. **Thống nhất**: Tất cả logs sử dụng cùng format và handlers
2. **Tách biệt**: Access logs riêng biệt với application logs
3. **Performance**: SQLAlchemy logs chỉ ghi vào file, không spam console
4. **Flexibility**: Dễ dàng điều chỉnh level và format cho từng component

## Monitoring

- Theo dõi `app.log` để debug application issues
- Theo dõi `access.log` để monitor HTTP traffic
- SQLAlchemy query logs giúp debug database performance

## Example output

### app.log:
```
2025-07-13 18:39:39 - uvicorn.error - INFO - Started server process [12584]
2025-07-13 18:39:39 - app.main - INFO - Application started successfully
2025-07-13 18:39:39 - sqlalchemy.engine.Engine - INFO - BEGIN (implicit)
```

### access.log:
```
2025-07-13 18:39:51 - uvicorn.access - INFO - 127.0.0.1:58734 - "GET /api/ HTTP/1.1" 200 OK
```
