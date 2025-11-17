# ⚡ Quick Start Guide

Get up and running in under 5 minutes!

## 📋 Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed
- [ ] OpenAI API key

## 🔧 Installation

### Step 1: Install Dependencies

```bash
cd content_gen
pip install -r mediachain/requirements.txt
```

### Step 2: Set Your API Key

**Option A: Environment Variable**
```bash
export OPENAI_API_KEY=sk-your-key-here
```

**Option B: .env File** (Recommended)
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Step 3: Start Server

```bash
./run_server.sh
```

Or:
```bash
python app.py
```

## 🌐 Access the Web Interface

Open your browser to:
```
http://localhost:8000
```

## 🎬 Create Your First Video

### 1. Upload Background Video
- Click the upload area
- Select a video file (MP4, MOV, AVI, or MKV)
- Recommended: Gaming footage, nature scenes, abstract visuals

### 2. Enter Story Topic
Example topics:
```
A story about a man who falls in love with a woman
AITA for refusing to help my friend move?
The day I discovered my hidden talent
```

### 3. Customize (Optional)
- Toggle AI-generated images
- Change caption colors
  - Font color (default: white)
  - Shadow color (default: black)

### 4. Generate
- Click "Generate Video"
- Wait 2-5 minutes
- Download your video!

## 📊 What You'll Get

**Output Video:**
- Format: 9:16 vertical (mobile-optimized)
- Contains:
  - Intro with your question/topic
  - AI-generated narration
  - Word-by-word captions
  - AI images at key moments
- Perfect for TikTok, Instagram Reels, YouTube Shorts

## 🔍 Example Workflow

```
1. Upload: minecraft_gameplay.mp4 (1080p, 2 minutes)
2. Topic: "A story about overcoming fear"
3. Settings: White captions, AI images ON
4. Generate → Wait 3 minutes
5. Download: reddit_story_abc123.mp4 (1080x1920, 45 seconds)
```

## 🚨 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill the process if needed
lsof -ti:8000 | xargs kill -9
```

### API key error
```bash
# Verify your .env file
cat .env

# Should show:
# OPENAI_API_KEY=sk-...
```

### Upload fails
- Check file size (< 500MB recommended)
- Verify file format (must be video)
- Ensure disk space available

### Video generation fails
- Check OpenAI API credits
- Review server logs in terminal
- Try without AI images first

## 💡 Tips

✅ **DO:**
- Use high-quality background videos
- Keep topics clear and concise
- Match caption colors to background
- Test with shorter videos first

❌ **DON'T:**
- Upload extremely large files (> 1GB)
- Use very short background videos (< 30s)
- Close browser during generation
- Refresh the page while processing

## 📈 Next Steps

1. ✅ Create your first video
2. 🎨 Experiment with different backgrounds
3. 🎯 Try various story topics
4. 📱 Share on social media!

## 🆘 Need Help?

**Check the logs:**
The terminal where you ran `./run_server.sh` shows detailed progress and errors.

**Common log messages:**
```
✅ "Video generated successfully" - All good!
❌ "Failed to generate script" - API key issue
❌ "Invalid video format" - Wrong file type
⚠️  "Processing..." - Still working (be patient!)
```

## 🎯 Pro Tips

### Best Background Videos
- **Gaming footage**: Minecraft, Subway Surfers, GTA
- **Nature**: Slow-motion waterfalls, clouds, ocean
- **Abstract**: Color gradients, particle effects
- **POV**: Driving, walking, cooking

### Best Story Topics
- Reddit-style questions (AITA, relationship advice)
- Personal anecdotes
- Moral dilemmas
- Wholesome encounters
- Plot twists

### Optimization
- **For speed**: Disable AI images
- **For quality**: Use 1080p+ backgrounds
- **For engagement**: Start with intriguing questions
- **For virality**: Keep videos under 60 seconds

## 🚀 Ready to Go!

You're all set! Open **http://localhost:8000** and start creating viral content! 🎬

---

**Questions?** Check the full [README.md](README.md) for detailed documentation.

