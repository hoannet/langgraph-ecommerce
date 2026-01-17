# MongoDB Setup Guide

## 📝 Cấu Hình MONGODB_URL

### File .env đã được cập nhật với:

```bash
# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=langgraph_ecommerce
```

## 🚀 Cách Setup MongoDB

### Option 1: Docker (Khuyến nghị)

```bash
# Start MongoDB container
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Check if running
docker ps | grep mongodb

# Stop MongoDB
docker stop mongodb

# Start again
docker start mongodb

# Remove container
docker rm -f mongodb
```

### Option 2: Local Installation (macOS)

```bash
# Install
brew install mongodb-community

# Start service
brew services start mongodb-community

# Stop service
brew services stop mongodb-community

# Check status
brew services list | grep mongodb
```

## ✅ Test Connection

```bash
cd /projects/agentic-ai/langgraph-test
source venv/bin/activate

# Test MongoDB connection
python scripts/test_mongodb.py
```

**Expected Output:**
```
INFO - Testing MongoDB connection...
INFO - Connected to database: langgraph_ecommerce
INFO - Collections: []
INFO - ✅ MongoDB connection successful!
```

## 📊 Seed Database

```bash
# After MongoDB is running
python src/database/seed_data.py
```

**Expected Output:**
```
INFO - Connecting to MongoDB at mongodb://localhost:27017
INFO - MongoDB connection established
INFO - Cleared existing products
INFO - Inserted 12 products
INFO - Created indexes
INFO - ✅ Database seeded successfully!
```

## 🔍 Verify Data

```bash
# Using MongoDB shell (if installed)
mongosh

# Switch to database
use langgraph_ecommerce

# Count products
db.products.countDocuments()
# Should return: 12

# List products
db.products.find().pretty()

# Exit
exit
```

## 🐛 Troubleshooting

### Error: "Connection refused"
```bash
# Check if MongoDB is running
docker ps | grep mongo
# Or
brew services list | grep mongodb

# If not running, start it
docker start mongodb
# Or
brew services start mongodb-community
```

### Error: "Database not found"
```bash
# Seed the database
python src/database/seed_data.py
```

### Error: "Port 27017 already in use"
```bash
# Find process using port
lsof -i :27017

# Kill process
kill -9 <PID>

# Or change MONGODB_URL in .env to different port
MONGODB_URL=mongodb://localhost:27018
```

## 📝 Configuration Details

### Default Settings:
- **Host**: localhost
- **Port**: 27017
- **Database**: langgraph_ecommerce
- **Collections**: products, orders

### Custom Configuration:

If you need to use different settings, update `.env`:

```bash
# Remote MongoDB
MONGODB_URL=mongodb://username:password@host:port

# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net

# Different database name
MONGODB_DB_NAME=my_custom_db
```

## 🎯 Next Steps

1. ✅ MongoDB running
2. ✅ Connection tested
3. ✅ Database seeded
4. ▶️ Start backend: `uvicorn src.api.main:app --reload`
5. ▶️ Test API: `curl http://localhost:8000/products`

---

**Lưu ý**: Đảm bảo MongoDB đang chạy TRƯỚC KHI start backend!
