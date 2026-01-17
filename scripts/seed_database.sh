#!/bin/bash
# Script to seed MongoDB with sample data

echo "🌱 Seeding MongoDB with sample products..."
echo ""

# Check if MongoDB is running
if ! docker ps | grep -q mongodb; then
    echo "⚠️  MongoDB is not running!"
    echo "Starting MongoDB with Docker..."
    docker run -d -p 27017:27017 --name mongodb mongo:latest
    sleep 3
fi

echo "✅ MongoDB is running"
echo ""

# Activate virtual environment and run seed script
echo "📦 Running seed script..."
cd "$(dirname "$0")/.."
source venv/bin/activate
python src/database/seed_data.py

echo ""
echo "✅ Done! Database seeded with 12 products"
echo ""
echo "📊 Product categories:"
echo "  - Electronics: 7 products"
echo "  - Books: 3 products"
echo "  - Clothing: 2 products"
echo ""
echo "🔍 To verify, run:"
echo "  python scripts/verify_data.py"
