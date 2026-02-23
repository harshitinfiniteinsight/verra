#!/bin/bash
# Quick setup script for Verra AI Chatbot

set -e

echo "=== Verra VCU Chatbot Setup ==="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required"
    exit 1
fi
echo "✓ Python $(python3 --version)"

# Check Node
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is required"
    exit 1
fi
echo "✓ Node $(node --version)"

# Setup Backend
echo
echo "=== Backend Setup ==="
cd backend

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Check .env file
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your OPENAI_API_KEY"
fi

# Initialize database
if [ ! -f ../verra.db ]; then
    echo "Initializing database from CSV..."
    python3 init_db.py
else
    echo "Database already exists, skipping initialization"
fi

cd ..

# Setup Frontend
echo
echo "=== Frontend Setup ==="
cd frontend

if [ ! -d node_modules ]; then
    echo "Installing Node dependencies..."
    npm install > /dev/null 2>&1
fi

# Check .env.local
if [ ! -f .env.local ]; then
    echo "Creating .env.local..."
    cp .env.local .env.local 2>/dev/null || echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

cd ..

echo
echo "=== Setup Complete ==="
echo
echo "To start the application:"
echo
echo "1. Terminal 1 (Backend):"
echo "   cd backend && python3 main.py"
echo
echo "2. Terminal 2 (Frontend):"
echo "   cd frontend && npm run dev"
echo
echo "Then open http://localhost:3000 in your browser"
echo
