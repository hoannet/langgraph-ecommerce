# Backend Fix - Import Error

## ❌ Lỗi gặp phải:
```
ImportError: cannot import name 'settings' from 'src.core.config'
```

## ✅ Đã sửa:

### File: `src/database/mongodb.py`

**Trước:**
```python
from src.core.config import settings

# ...
logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
cls.db = cls.client[settings.MONGODB_DB_NAME]
```

**Sau:**
```python
from src.core.config import get_settings

# ...
settings = get_settings()
logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
cls.client = AsyncIOMotorClient(settings.mongodb_url)
cls.db = cls.client[settings.mongodb_db_name]
```

## 🔧 Nguyên nhân:

- `config.py` export function `get_settings()` chứ không phải instance `settings`
- Pydantic field names là lowercase với underscore (`mongodb_url`) chứ không phải uppercase (`MONGODB_URL`)

## ✅ Bây giờ có thể chạy:

```bash
# Start backend
uvicorn src.api.main:app --reload
```

Hoặc:

```bash
make run
```

Backend sẽ khởi động thành công!
