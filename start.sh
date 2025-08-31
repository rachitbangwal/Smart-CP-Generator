#!/bin/bash

# Smart Charter Party Generator - Startup Script

echo "🚢 Smart Charter Party Generator - Starting..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Try to download spaCy model (if network is available)
echo "🧠 Checking spaCy language model..."
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "⚠️ spaCy model not found. Attempting to download..."
    python -m spacy download en_core_web_sm || echo "⚠️ Could not download spaCy model. NLP features will be limited."
fi

# Start the application
echo "🚀 Starting Smart Charter Party Generator on http://localhost:8000"
echo "📖 API Documentation available at http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"

# Use simple app for now due to SQLAlchemy compatibility issues
python simple_app.py

# Alternative: Use the full application (uncomment when SQLAlchemy issue is resolved)
# python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
