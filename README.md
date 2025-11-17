# 🎬 Reddit Story Video Generator

An AI-powered web application that transforms text stories into engaging vertical videos with narration, captions, AI-generated images, and custom backgrounds. Perfect for creating content for TikTok, Instagram Reels, and YouTube Shorts.

## ✨ Features

- **🎙️ AI Narration**: Converts stories to natural-sounding speech using OpenAI TTS or ElevenLabs
- **🔊 Audio Normalization**: Automatically normalizes volume levels for consistent, professional audio (NEW!)
- **📝 Auto Captions**: Generates synchronized word-by-word captions with customizable styling
- **🖼️ AI Images**: Automatically generates and inserts relevant images at key moments
- **👤 Speaker Avatars**: Add profile pictures that appear when each speaker talks (NEW!)
- **📱 Vertical Format**: Outputs 9:16 videos optimized for mobile platforms
- **🔄 Auto-Loop**: Automatically loops short videos to meet duration requirements
- **🎨 Customizable**: Choose caption colors, fonts, and shadow effects
- **⚡ Fast Processing**: Async architecture for efficient video generation
- **🌐 Web Interface**: Beautiful, lightweight UI for easy video creation
- **📤 Upload Support**: Use your own background videos (no URLs required!)
- **♻️ Audio Reuse**: Preview audio is reused for video generation (saves time and API costs!)

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- FFmpeg (for video processing)
- OpenAI API key

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd content_gen

# Install dependencies
pip install -r mediachain/requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env

# Edit with your API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 4. Run the Server

```bash
# Make the script executable (Mac/Linux)
chmod +x run_server.sh

# Run the server
./run_server.sh
```

Or directly with Python:

```bash
python app.py
```

### 5. Create Videos!

1. Open your browser to: **http://localhost:8000**
2. Upload a background video (MP4, MOV, AVI, or MKV)
3. Enter your story topic or Reddit question
4. Customize caption styling (optional)
5. Click "Generate Video"
6. Download your finished video!

## 📁 Project Structure

```
content_gen/
├── app.py                      # FastAPI web server (ROOT)
├── run_server.sh              # Server startup script (ROOT)
├── static/                    # Frontend UI (ROOT)
│   └── index.html            # Web interface
├── uploads/                   # Temporary uploaded videos
├── outputs/                   # Generated videos
│
├── mediachain/               # Core video generation library
│   ├── core/                # MediaChain modules
│   │   ├── script/          # AI script generation
│   │   ├── audio/           # TTS and STT services
│   │   ├── image/           # AI image generation
│   │   └── video/           # Video analysis
│   │
│   ├── examples/
│   │   └── moviepy_engine/  # Video editing engine
│   │       ├── reddit_stories/
│   │       │   └── generate_reddit_story.py
│   │       └── src/
│   │           ├── video_editor.py
│   │           └── captions/
│   │
│   └── requirements.txt     # Python dependencies
│
└── README.md                # This file
```

## 🎯 How It Works

### Architecture Overview

```
User Upload → FastAPI → RedditStoryGenerator
                           ↓
    ┌──────────────────────┴──────────────────────┐
    │                                              │
    ↓                                              ↓
Script Generation                        Video Processing
(OpenAI GPT)                            (MoviePy)
    ↓                                              ↓
Text-to-Speech                          Background Video
(OpenAI TTS/ElevenLabs)                 (Crop to 9:16)
    ↓                                              ↓
Speech-to-Text                          Caption Overlay
(Whisper)                               (Word-by-word)
    ↓                                              ↓
Image Generation                        Image Insertion
(DALL-E/Leonardo)                       (At timestamps)
    ↓                                              ↓
    └──────────────────────┬──────────────────────┘
                           ↓
                   Final Video Render
                   (9:16 MP4 output)
```

### Processing Pipeline

1. **Upload & Validation**: Video is uploaded and validated
2. **Script Generation**: AI generates an engaging story script based on your topic
3. **Question Clip**: Creates intro with topic as narrated question
4. **Audio Generation**: Converts script to speech
5. **Caption Generation**: Transcribes audio with timestamps
6. **Image Analysis**: AI determines where images should appear
7. **Image Generation**: Creates relevant AI images
8. **Video Composition**:
   - Crops background to 9:16
   - Overlays captions
   - Inserts images
   - Syncs audio
9. **Rendering**: Exports final video
10. **Cleanup**: Removes temporary files

## 🛠️ API Endpoints

### Web Interface
- `GET /` - Main web interface

### API
- `POST /api/generate-video` - Generate a video
- `GET /api/download/{filename}` - Download generated video
- `GET /api/status/{job_id}` - Check generation status
- `DELETE /api/cleanup/{job_id}` - Clean up job data
- `GET /api/health` - Health check

### API Documentation
Visit **http://localhost:8000/docs** for interactive API documentation (Swagger UI)

## 🎨 Customization

### Caption Styling

Customize captions through the web interface or API:

```python
captions_settings = {
    'color': 'white',           # Font color
    'shadow_color': 'black',    # Shadow color
    'font_size': 40,            # Font size (auto-calculated if not set)
    'font': 'LEMONMILK-Bold.otf'  # Font file
}
```

### Voice Options

Available TTS voices:
- **OpenAI**: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- **ElevenLabs**: Custom voice IDs

### Image Generation

Toggle AI images on/off or customize:
- Enable/disable in UI
- API automatically analyzes script for relevant moments
- Generates images using DALL-E or Leonardo AI

## 📊 Performance

- **Average processing time**: 2-5 minutes per video
- **Factors affecting speed**:
  - Video length
  - Number of AI images
  - Background video resolution
  - API response times

## 🔧 Troubleshooting

### 📚 **Full Debugging Guide:** [DEBUGGING.md](DEBUGGING.md)

For comprehensive debugging help, see the **[DEBUGGING.md](DEBUGGING.md)** guide which includes:
- Structured log format explanation
- Common errors and solutions
- Step-by-step debugging process
- Performance optimization tips
- Testing individual components

### Quick Fixes

**"Background video too short"**
- ✨ **NEW**: Auto-loop feature automatically extends short videos!
- Enable "Auto-loop video if too short" checkbox (enabled by default)
- Or upload a longer video (60+ seconds recommended)
- See [AUTO_LOOP_FEATURE.md](AUTO_LOOP_FEATURE.md) for details

**"OPENAI_API_KEY not set"**
```bash
# Set in .env file
echo "OPENAI_API_KEY=sk-your-key" > .env

# Or export in terminal
export OPENAI_API_KEY=sk-your-key
```

**"Port 8000 already in use"**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or change port in app.py
uvicorn.run(app, host="0.0.0.0", port=8080)
```

**Video upload fails**
- Check file format (must be MP4, MOV, AVI, or MKV)
- Reduce file size if > 500MB
- Ensure disk space available
- Video should be at least 60 seconds long

**Video generation fails**
- Check server logs - they now show exactly what failed
- Verify OpenAI API key is valid
- Check API credits/quota
- See [DEBUGGING.md](DEBUGGING.md) for detailed help

**FFmpeg errors**
```bash
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org
```

### Understanding Logs

All logs now use a structured format:
```
[COMPONENT] Message with ✓ (success) or ✗ (failure) indicators
```

**Example:**
```
[TIMING] ✓ Cut times calculated: Start: 10.5s, End: 35.2s
[CUT] ✗ Failed to cut video - file corrupted
```

See [DEBUGGING.md](DEBUGGING.md) for complete log tag reference.

## 📚 Documentation

### **Core Guides**
- **[CAPTION_SYNC_GUIDE.md](CAPTION_SYNC_GUIDE.md)** - How audio/text synchronization works (Whisper vs ElevenLabs)
- **[AUDIO_NORMALIZATION.md](AUDIO_NORMALIZATION.md)** - Automatic volume normalization for consistent audio (NEW!)
- **[AUDIO_REUSE_FEATURE.md](AUDIO_REUSE_FEATURE.md)** - How preview audio is reused to save time/cost
- **[SPEAKER_AVATARS_FEATURE.md](SPEAKER_AVATARS_FEATURE.md)** - Add speaker profile pictures that appear when talking (NEW!)
- **[DIALOGUE_IMAGES_FEATURE.md](DIALOGUE_IMAGES_FEATURE.md)** - Upload custom images for dialogue lines
- **[SCRIPT_MODE_GUIDE.md](SCRIPT_MODE_GUIDE.md)** - Complete guide for custom script mode with 2 speakers
- **[QUICK_SETUP_SCRIPT_MODE.md](QUICK_SETUP_SCRIPT_MODE.md)** - Quick start for script mode
- **[DEBUGGING.md](DEBUGGING.md)** - Comprehensive debugging and troubleshooting
- **[AUTO_LOOP_FEATURE.md](AUTO_LOOP_FEATURE.md)** - Auto-loop video feature documentation

### **Reference Files**
- **[elevenlabs_timestamps_util.py](elevenlabs_timestamps_util.py)** - Optional ElevenLabs timestamp implementation (not currently used)
- **[SCRIPT_MODE_SUMMARY.txt](SCRIPT_MODE_SUMMARY.txt)** - Quick reference for script mode

## 🌟 Examples

### Example Topics

- "A story about a person who discovered a hidden talent"
- "AITA for refusing to attend my sister's wedding?"
- "The day I realized my cat was actually a genius"
- "A wholesome encounter with a stranger that changed my life"

### Input/Output

**Input:**
- Background video: 1920x1080 gameplay footage (2 minutes)
- Topic: "A story about overcoming fear"
- Settings: White captions, AI images enabled

**Output:**
- Final video: 1080x1920 vertical (45 seconds)
- Contains: Intro question + narrated story + captions + 3 AI images

## 🔐 Security Notes

- API keys are stored in `.env` (not committed to git)
- Uploaded videos are temporary (deleted after processing)
- No data is stored permanently
- All processing happens locally (except API calls)

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review server logs for debugging

## 🎯 Roadmap

- [ ] Queue system for multiple simultaneous generations
- [ ] Progress updates via WebSockets
- [ ] Multiple video engines (not just MoviePy)
- [ ] Batch processing
- [ ] Template library
- [ ] User authentication
- [ ] Cloud deployment guides
- [ ] Docker support

## 💡 Tips & Best Practices

- Use high-quality background videos (1080p or 4K)
- Keep topics clear and specific
- Dark backgrounds → white captions
- Light backgrounds → black captions
- Background video should be 60+ seconds
- Test without images first to validate pipeline

## 🙏 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [MoviePy](https://zulko.github.io/moviepy/) - Video editing
- [OpenAI](https://openai.com/) - AI services
- [ElevenLabs](https://elevenlabs.io/) - TTS (optional)

---

**Ready to create viral content? Start generating videos now! 🚀**

For detailed usage guide, see [QUICKSTART.md](mediachain/examples/moviepy_engine/QUICKSTART.md)

