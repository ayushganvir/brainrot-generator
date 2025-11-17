#!/bin/bash

# Verification script for Reddit Story Video Generator setup
# Run this to verify everything is in place

echo "=========================================="
echo "🔍 Verifying Setup"
echo "=========================================="
echo ""

ALL_GOOD=true

# Check if we're in project root
echo "📁 Checking project root..."
if [ ! -f "app.py" ]; then
    echo "   ❌ app.py not found. Are you in the project root?"
    ALL_GOOD=false
else
    echo "   ✅ app.py found"
fi

# Check static folder
echo "📁 Checking static folder..."
if [ ! -d "static" ]; then
    echo "   ❌ static/ folder not found"
    ALL_GOOD=false
elif [ ! -f "static/index.html" ]; then
    echo "   ❌ static/index.html not found"
    ALL_GOOD=false
else
    echo "   ✅ static/index.html found"
fi

# Check mediachain library
echo "📁 Checking mediachain library..."
if [ ! -d "mediachain" ]; then
    echo "   ❌ mediachain/ folder not found"
    ALL_GOOD=false
else
    echo "   ✅ mediachain/ folder found"
fi

# Check core generator
echo "📁 Checking video generator..."
if [ ! -f "mediachain/examples/moviepy_engine/reddit_stories/generate_reddit_story.py" ]; then
    echo "   ❌ RedditStoryGenerator not found"
    ALL_GOOD=false
else
    echo "   ✅ RedditStoryGenerator found"
fi

# Check requirements
echo "📁 Checking requirements..."
if [ ! -f "mediachain/requirements.txt" ]; then
    echo "   ❌ requirements.txt not found"
    ALL_GOOD=false
else
    echo "   ✅ requirements.txt found"
fi

# Check run script
echo "📁 Checking run script..."
if [ ! -f "run_server.sh" ]; then
    echo "   ❌ run_server.sh not found"
    ALL_GOOD=false
elif [ ! -x "run_server.sh" ]; then
    echo "   ⚠️  run_server.sh not executable (fixing...)"
    chmod +x run_server.sh
    echo "   ✅ run_server.sh now executable"
else
    echo "   ✅ run_server.sh found and executable"
fi

# Check documentation
echo "📁 Checking documentation..."
DOC_COUNT=0
[ -f "README.md" ] && ((DOC_COUNT++))
[ -f "QUICKSTART.md" ] && ((DOC_COUNT++))
[ -f "PROJECT_STRUCTURE.md" ] && ((DOC_COUNT++))

if [ $DOC_COUNT -eq 3 ]; then
    echo "   ✅ All documentation files found"
else
    echo "   ⚠️  Some documentation missing ($DOC_COUNT/3 found)"
fi

# Check Python
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION found"
else
    echo "   ❌ Python 3 not found"
    ALL_GOOD=false
fi

# Check pip packages
echo "📦 Checking Python packages..."
if python3 -c "import fastapi" 2>/dev/null; then
    echo "   ✅ fastapi installed"
else
    echo "   ⚠️  fastapi not installed (run: pip install -r mediachain/requirements.txt)"
fi

if python3 -c "import openai" 2>/dev/null; then
    echo "   ✅ openai installed"
else
    echo "   ⚠️  openai not installed (run: pip install -r mediachain/requirements.txt)"
fi

if python3 -c "import moviepy.editor" 2>/dev/null; then
    echo "   ✅ moviepy installed"
else
    echo "   ⚠️  moviepy not installed (run: pip install -r mediachain/requirements.txt)"
fi

# Check FFmpeg
echo "🎬 Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "   ✅ FFmpeg found"
else
    echo "   ⚠️  FFmpeg not found (required for video processing)"
    echo "      Install: brew install ffmpeg (Mac) or apt install ffmpeg (Linux)"
fi

# Check environment variables
echo "🔑 Checking environment..."
if [ -f ".env" ]; then
    echo "   ✅ .env file found"
    if grep -q "OPENAI_API_KEY" .env && ! grep -q "your-key-here" .env && ! grep -q "sk-your" .env; then
        echo "   ✅ OPENAI_API_KEY appears to be set"
    else
        echo "   ⚠️  OPENAI_API_KEY not configured in .env"
    fi
elif [ -n "$OPENAI_API_KEY" ]; then
    echo "   ✅ OPENAI_API_KEY set in environment"
else
    echo "   ⚠️  No .env file and OPENAI_API_KEY not in environment"
    echo "      Create .env with: OPENAI_API_KEY=sk-your-key-here"
fi

# Create directories if needed
echo "📂 Checking/creating directories..."
mkdir -p uploads
mkdir -p outputs
echo "   ✅ uploads/ and outputs/ ready"

# Summary
echo ""
echo "=========================================="
if [ "$ALL_GOOD" = true ]; then
    echo "✅ All critical checks passed!"
    echo ""
    echo "You're ready to start the server:"
    echo "   ./run_server.sh"
    echo ""
    echo "Or directly:"
    echo "   python3 app.py"
    echo ""
    echo "Then open: http://localhost:8000"
else
    echo "⚠️  Some issues found. Please fix them above."
    echo ""
    echo "Common fixes:"
    echo "1. Make sure you're in the project root (/content_gen/)"
    echo "2. Run: pip install -r mediachain/requirements.txt"
    echo "3. Create .env with your OPENAI_API_KEY"
    echo "4. Install FFmpeg if needed"
fi
echo "=========================================="

