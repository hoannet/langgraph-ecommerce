# MongoDB Seed Data Guide

## 📦 Sample Products Included

Script `src/database/seed_data.py` chứa **12 sample products**:

### Electronics (7 products)
1. **MacBook Pro 16"** - $2,999.00 (15 in stock)
2. **Dell XPS 15** - $2,199.00 (20 in stock)
3. **ThinkPad X1 Carbon** - $1,599.00 (25 in stock)
4. **iPhone 15 Pro** - $1,199.00 (50 in stock)
5. **Samsung Galaxy S24 Ultra** - $1,299.00 (40 in stock)
6. **Sony WH-1000XM5** - $399.99 (35 in stock)
7. **iPad Pro 12.9"** - $1,299.00 (30 in stock)

### Books (3 products)
8. **Clean Code** - $39.99 (100 in stock)
9. **The Pragmatic Programmer** - $44.99 (80 in stock)
10. **Design Patterns** - $54.99 (60 in stock)

### Clothing (2 products)
11. **Nike Air Max 270** - $149.99 (75 in stock)
12. **Levi's 501 Original Jeans** - $79.99 (120 in stock)

---

## 🚀 Cách Seed Database

### Option 1: Sử dụng Script (Khuyến nghị)

```bash
# Tự động start MongoDB và seed data
./scripts/seed_database.sh
```

### Option 2: Manual

```bash
# 1. Start MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# 2. Activate venv
source venv/bin/activate

# 3. Run seed script
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

---

## ✅ Verify Data

```bash
# Kiểm tra data đã được insert
python scripts/verify_data.py
```

**Expected Output:**
```
📊 Total products: 12

📦 Products by category:
  - Electronics: 7 products
  - Books: 3 products
  - Clothing: 2 products

🔍 Sample products:
  - MacBook Pro 16" ($2999.0) - 15 in stock
  - Dell XPS 15 ($2199.0) - 20 in stock
  - ThinkPad X1 Carbon ($1599.0) - 25 in stock

📋 Total orders: 0

✅ Database verification complete!
```

---

## 🔄 Re-seed Database

Script sẽ **xóa tất cả products cũ** và insert lại:

```bash
python src/database/seed_data.py
```

⚠️ **Warning**: Lệnh này sẽ xóa toàn bộ products hiện có!

---

## 🛠️ Customize Sample Data

Để thêm/sửa products, edit file `src/database/seed_data.py`:

```python
SAMPLE_PRODUCTS = [
    {
        "_id": "prod_013",  # Unique ID
        "name": "Your Product Name",
        "description": "Product description",
        "price": 99.99,
        "category": "Electronics",  # Electronics, Books, Clothing
        "stock": 50,
        "image_url": "https://...",
        "created_at": datetime.now(),
    },
    # Add more products...
]
```

Sau đó chạy lại:
```bash
python src/database/seed_data.py
```

---

## 📊 Database Schema

### Products Collection
```javascript
{
  _id: "prod_001",           // String (unique)
  name: "Product Name",      // String
  description: "...",        // String
  price: 99.99,             // Float
  category: "Electronics",   // String
  stock: 50,                // Integer
  image_url: "https://...", // String (optional)
  created_at: ISODate()     // DateTime
}
```

### Orders Collection
```javascript
{
  _id: "ord_abc123",        // String (unique)
  session_id: "session_1",  // String
  items: [                  // Array
    {
      product_id: "prod_001",
      product_name: "...",
      quantity: 2,
      price: 99.99,
      subtotal: 199.98
    }
  ],
  total: 199.98,           // Float
  status: "pending",       // String (pending, paid, shipped, etc.)
  payment_id: "txn_xyz",   // String (optional)
  created_at: ISODate(),   // DateTime
  updated_at: ISODate()    // DateTime
}
```

---

## 🧪 Test với API

Sau khi seed, test API endpoints:

```bash
# List all products
curl http://localhost:8000/products

# Search laptops
curl "http://localhost:8000/products/search?query=laptop"

# Get specific product
curl http://localhost:8000/products/prod_001

# Search by category
curl "http://localhost:8000/products/search?category=Books"
```

---

## 🎯 Test Flow Hoàn Chỉnh

1. **Seed database**:
   ```bash
   python src/database/seed_data.py
   ```

2. **Start backend**:
   ```bash
   make run
   ```

3. **Test trong chatbox**:
   - "Show me laptops" → Hiển thị 3 laptops
   - "I want product prod_001" → Tạo order
   - "Pay now" → Thanh toán

---

**✅ Database ready to use!**
