#!/bin/bash

# Quick start script for local development

set -e

echo "🚀 Quick Start - GenAI Agent Deployment Backend"
echo ""

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r ../requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please update .env with your actual credentials before running the server!"
    echo ""
    read -p "Press Enter to continue..."
fi

# Check if required environment variables are set
if ! grep -q "OPENAI_API_KEY=your-" .env; then
    echo "✅ Environment configured"
else
    echo "⚠️  Warning: .env still contains placeholder values"
    echo "   Please update .env with your actual credentials"
    echo ""
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the development server, run:"
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "Or use:"
echo "  python3 -m uvicorn main:app --reload --port 8000"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo ""
