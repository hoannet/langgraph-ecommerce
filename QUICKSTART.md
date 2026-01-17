# Quick Start - E-commerce Backend

## 🚀 Khởi động nhanh trong 3 bước

### Bước 1: Start MongoDB

```bash
# Sử dụng Docker (khuyến nghị)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Kiểm tra đang chạy
docker ps | grep mongodb
```

### Bước 2: Test Connection & Seed Data

```bash
cd /springme/projects/agentic-ai/langgraph-test
source venv/bin/activate

# Test MongoDB connection
python scripts/test_mongodb.py

# Seed database với 12 sample products
python src/database/seed_data.py
```

### Bước 3: Start Backend

```bash
# Trong cùng terminal
uvicorn src.api.main:app --reload
```

## ✅ Verify

```bash
# Test health
curl http://localhost:8000/health

# List products
curl http://localhost:8000/products

# Search laptops
curl "http://localhost:8000/products/search?query=laptop"
```

## 🎯 Test trong Chatbox

Frontend đang chạy tại `http://localhost:3000`

Thử các câu sau:
1. `Show me laptops`
2. `I want product prod_001`
3. `Pay now`

## 🐛 Nếu có lỗi

### MongoDB connection failed
```bash
# Kiểm tra MongoDB đang chạy
docker ps | grep mongo

# Nếu không chạy
docker start mongodb
```

### Module not found
```bash
# Đảm bảo đang trong venv
source venv/bin/activate

# Kiểm tra dependencies
pip list | grep motor
```

### Port 8000 already in use
```bash
# Tìm process
lsof -i :8000

# Kill process
kill -9 <PID>
```

---

**Xem chi tiết**: `docs/mongodb-setup.md`
