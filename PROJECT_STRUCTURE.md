# 📂 Project Structure

This document explains the organization of the Reddit Story Video Generator project.

## 🌳 Directory Tree

```
content_gen/                                    # PROJECT ROOT
│
├── 🌐 WEB APPLICATION (ROOT LEVEL)
│   ├── app.py                                 # FastAPI server (main entry point)
│   ├── run_server.sh                          # Server startup script
│   ├── static/                                # Frontend assets
│   │   └── index.html                        # Web UI
│   ├── uploads/                              # Temporary uploaded videos
│   └── outputs/                              # Generated videos
│
├── 📚 DOCUMENTATION (ROOT LEVEL)
│   ├── README.md                             # Main documentation
│   ├── QUICKSTART.md                         # Quick start guide
│   ├── PROJECT_STRUCTURE.md                  # This file
│   └── .gitignore                            # Git ignore rules
│
├── ⚙️ CONFIGURATION (ROOT LEVEL)
│   └── .env.example                          # Environment variables template
│   └── .env                                  # Your API keys (create this!)
│
└── 📦 MEDIACHAIN LIBRARY
    └── mediachain/                           # Core video generation library
        │
        ├── 🎬 CORE MODULES
        │   ├── core/
        │   │   ├── script/                   # AI script generation
        │   │   │   ├── script_generation.py
        │   │   │   ├── services/
        │   │   │   │   ├── openai.py
        │   │   │   │   └── azure_openai.py
        │   │   │   └── prompts/
        │   │   │       └── script.yaml
        │   │   │
        │   │   ├── audio/                    # Audio processing
        │   │   │   ├── text_to_speech/      # TTS services
        │   │   │   │   ├── tts_generation.py
        │   │   │   │   └── services/
        │   │   │   │       ├── openai.py
        │   │   │   │       ├── elevenlabs.py
        │   │   │   │       └── azure_openai.py
        │   │   │   │
        │   │   │   └── speech_to_text/      # STT services
        │   │   │       ├── stt_generation.py
        │   │   │       ├── services/
        │   │   │       │   └── openai.py
        │   │   │       └── utils/
        │   │   │           └── words_parser.py
        │   │   │
        │   │   ├── image/                    # Image generation
        │   │   │   ├── generation/
        │   │   │   │   ├── image_generation.py
        │   │   │   │   └── services/
        │   │   │   │       ├── dalle/
        │   │   │   │       ├── leonardo/
        │   │   │   │       └── pollinations/
        │   │   │   │
        │   │   │   └── utils/
        │   │   │       ├── enhance_prompt.py
        │   │   │       └── image_timestamps.py
        │   │   │
        │   │   └── video/                    # Video analysis
        │   │       └── analyze/
        │   │           ├── analyze_video.py
        │   │           └── services/
        │   │               └── openai.py
        │   │
        │   ├── 🎥 VIDEO ENGINE
        │   │   └── examples/
        │   │       └── moviepy_engine/
        │   │           ├── reddit_stories/
        │   │           │   └── generate_reddit_story.py  # Main generator class
        │   │           │
        │   │           ├── src/
        │   │           │   ├── video_editor.py           # Video manipulation
        │   │           │   │
        │   │           │   ├── captions/                 # Caption system
        │   │           │   │   ├── caption_handler.py
        │   │           │   │   ├── subtitle_generator.py
        │   │           │   │   ├── video_captioner.py
        │   │           │   │   └── fonts/               # Caption fonts
        │   │           │   │
        │   │           │   └── json_2_video_engine/     # JSON templating
        │   │           │       ├── json_2_video.py
        │   │           │       └── json_templates/
        │   │           │
        │   │           ├── main_moviepy.py              # Example script (legacy)
        │   │           └── README.md                    # Engine documentation
        │   │
        │   └── 📋 CONFIGURATION
        │       ├── requirements.txt                     # Python dependencies
        │       ├── README.md                           # Library documentation
        │       └── LICENSE                             # License
        │
        └── venv/                                       # Virtual environment (optional)
```

## 🎯 Key Components

### Root Level (Global/UI)

| File/Folder | Purpose | Location |
|-------------|---------|----------|
| `app.py` | FastAPI web server | `/content_gen/app.py` |
| `run_server.sh` | Server startup script | `/content_gen/run_server.sh` |
| `static/` | Frontend UI | `/content_gen/static/` |
| `uploads/` | Temporary uploads | `/content_gen/uploads/` |
| `outputs/` | Generated videos | `/content_gen/outputs/` |
| `README.md` | Main documentation | `/content_gen/README.md` |
| `.env` | API keys (create this) | `/content_gen/.env` |

### MediaChain Library

| Module | Purpose | Location |
|--------|---------|----------|
| `core/script/` | AI script generation | `/mediachain/core/script/` |
| `core/audio/` | TTS & STT | `/mediachain/core/audio/` |
| `core/image/` | Image generation | `/mediachain/core/image/` |
| `core/video/` | Video analysis | `/mediachain/core/video/` |
| `examples/moviepy_engine/` | Video editing engine | `/mediachain/examples/moviepy_engine/` |

## 🔄 Data Flow

```
User Browser
    ↓
static/index.html (Upload video + topic)
    ↓
app.py (FastAPI server)
    ↓
uploads/ (Temporary storage)
    ↓
RedditStoryGenerator (mediachain/examples/moviepy_engine/reddit_stories/)
    ↓
┌──────────────┴──────────────┐
↓                             ↓
MediaChain Core               MoviePy Engine
├─ script_generation.py      ├─ video_editor.py
├─ tts_generation.py         ├─ caption_handler.py
├─ stt_generation.py         └─ video composition
├─ image_generation.py
└─ image_timestamps.py
    ↓                             ↓
└──────────────┬──────────────┘
               ↓
        outputs/ (Final video)
               ↓
        Browser (Download)
```

## 📍 Where to Find Things

### Need to...

**Modify the web UI?**
→ `static/index.html`

**Change server endpoints?**
→ `app.py`

**Adjust video editing logic?**
→ `mediachain/examples/moviepy_engine/src/video_editor.py`

**Change how scripts are generated?**
→ `mediachain/core/script/script_generation.py`

**Modify caption styling?**
→ `mediachain/examples/moviepy_engine/src/captions/caption_handler.py`

**Add new TTS provider?**
→ `mediachain/core/audio/text_to_speech/services/`

**Change image generation?**
→ `mediachain/core/image/generation/image_generation.py`

**Adjust the main generation flow?**
→ `mediachain/examples/moviepy_engine/reddit_stories/generate_reddit_story.py`

## 🎨 Architecture Layers

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│    (FastAPI + HTML/JS Frontend)        │
│         app.py + static/               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         Application Layer               │
│       (Video Generation Logic)          │
│  RedditStoryGenerator (orchestrator)   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         Service Layer                   │
│   (MediaChain Core + MoviePy Engine)   │
│  Script│Audio│Image│Video Processing   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         External Services               │
│  OpenAI│ElevenLabs│Leonardo│FFmpeg     │
└─────────────────────────────────────────┘
```

## 🚀 Entry Points

### For End Users
```bash
cd /path/to/content_gen
./run_server.sh
# Open http://localhost:8000
```

### For Developers
```python
# Use the library programmatically
from mediachain.examples.moviepy_engine.reddit_stories.generate_reddit_story import RedditStoryGenerator

generator = RedditStoryGenerator(openai_api_key="...")
result = await generator.generate_video(...)
```

### For API Consumers
```bash
curl -X POST http://localhost:8000/api/generate-video \
  -F "video=@video.mp4" \
  -F "topic=Your story here"
```

## 📝 Configuration Files

| File | Purpose | Example |
|------|---------|---------|
| `.env` | API keys | `OPENAI_API_KEY=sk-...` |
| `requirements.txt` | Python packages | `fastapi==0.115.0` |
| `.gitignore` | Ignored files | `*.mp4`, `.env` |

## 🗂️ Temporary Files

**Created during processing (auto-deleted):**
- `uploads/{job_id}_{filename}` - Uploaded video
- `{random}_audio.mp3` - Generated TTS audio
- `{random}_subtitles.srt` - Generated captions
- `cut_video_{random}.mp4` - Intermediate video

**Persistent output:**
- `outputs/final_video_{timestamp}.mp4` - Your generated video!

## 🔐 Important Files (Don't Commit!)

- `.env` - Contains API keys
- `uploads/` - Temporary videos
- `outputs/` - Generated videos
- `venv/` - Python virtual environment

All protected by `.gitignore`

## 💡 Best Practices

✅ **DO:**
- Run server from project root (`/content_gen/`)
- Store API keys in `.env`
- Read root-level README for documentation
- Use web interface for easiest experience

❌ **DON'T:**
- Run server from `mediachain/examples/moviepy_engine/`
- Hard-code API keys
- Commit `.env` or video files
- Modify core library without understanding data flow

---

**Questions about structure?** See [README.md](README.md) or check individual module READMEs.

