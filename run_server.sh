#!/bin/bash

# Reddit Story Video Generator - Server Startup Script
# Run this from the project root: ./run_server.sh

echo "=========================================="
echo "🚀 Reddit Story Video Generator"
echo "=========================================="
echo ""

# Check if we're in the project root
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found!"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo ""
    echo "Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it and add your API keys."
        echo ""
        echo "Run: nano .env"
        echo "or: vim .env"
        echo ""
        exit 1
    else
        echo "❌ Error: .env.example not found!"
        echo ""
        echo "Please create a .env file with:"
        echo "OPENAI_API_KEY=sk-your-key-here"
        echo ""
        exit 1
    fi
fi

# Load environment variables
set -a
source .env
set +a

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env file"
    echo ""
    echo "Please edit .env and add your OpenAI API key:"
    echo "OPENAI_API_KEY=sk-your-key-here"
    echo ""
    exit 1
fi

# Create necessary directories
mkdir -p uploads
mkdir -p outputs
mkdir -p static

echo "✅ Environment configured"
echo "📁 Directories ready"
echo "🔑 API keys loaded"
echo ""
echo "Starting server..."
echo "=========================================="
echo ""

# Run the FastAPI app
python3 app.py

