# 🎬 BrainRot Generator

**AI-Powered Dialogue Video Generator with Chrome Extension for Image Selection**

Transform any dialogue script into engaging short-form videos with AI voices, custom backgrounds, and web-scraped images - perfect for creating viral content!

---

## ✨ Features

### 🎙️ **AI Voice Generation**
- Multi-speaker dialogue support with ElevenLabs voices
- Character-specific voice assignment (Peter Griffin, Stewie, custom voices)
- Natural conversation flow with automated timing

### 🎥 **Video Creation**
- Custom background videos or random defaults
- Auto-loop short backgrounds to match dialogue length
- Animated captions with speaker avatars
- Professional styling with shadows and positioning
- Export-ready MP4 output (1080x1920 vertical format)

### 🖼️ **Chrome Extension - Image Selection**
- **Drag-to-select** area capture from any webpage
- Real-time sync between extension and web app
- Side panel UI for easy image management
- Dialogue-specific image association
- Works on all websites (respects CORS)

### 📝 **Script Parsing**
- Automatic speaker detection
- Dialogue breakdown and preview
- Optional image upload per dialogue line
- Voice preview before generation

### 📱 **Instagram Integration**
- Direct upload to Instagram (Reels/Feed)
- Multiple account management
- Upload history tracking
- Public URL support via ngrok

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
pip install -r requirements.txt

# API Keys (add to .env)
OPENAI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
PUBLIC_URL=https://your-ngrok-url.ngrok-free.app  # for Instagram
```

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd content_gen
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Install Chrome Extension**
- Open Chrome: `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked"
- Select `chrome-extension` folder

5. **Run the app**
```bash
python app.py
# Visit http://localhost:8000
```

---

## 🎯 How It Works

### 1. **Write Your Script**
```
Peter: Y'know, this AI stuff is pretty cool!
Stewie: Indeed, quite remarkable technology.
```

### 2. **Select Images (Optional)**
- Click extension icon in Chrome
- Navigate to any webpage
- Drag to select areas for each dialogue
- Images sync automatically to the app

### 3. **Assign Voices**
- Choose ElevenLabs voices for each speaker
- Preview audio before generating
- Upload custom speaker avatars (optional)

### 4. **Generate Video**
- Upload background video or use defaults
- Click "Generate Video"
- Download or upload directly to Instagram

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python
- **AI**: OpenAI GPT, ElevenLabs TTS
- **Video**: MoviePy, FFmpeg
- **Frontend**: Vanilla HTML/CSS/JS
- **Extension**: Chrome Extension Manifest V3
- **APIs**: Instagram Graph API

---

## 📂 Project Structure

```
content_gen/
├── app.py                 # Main FastAPI application
├── script_parser.py       # Dialogue parsing logic
├── instagram_manager.py   # Instagram API integration
├── static/
│   ├── index.html        # Landing page
│   └── script_mode.html  # Main app interface
├── chrome-extension/      # Chrome extension
│   ├── manifest.json
│   ├── sidepanel.html
│   ├── sidepanel.js
│   └── background.js
├── outputs/              # Generated videos
├── default_videos/       # Default backgrounds
└── uploads/              # User uploads
```

---

## 🎨 Chrome Extension Features

### Area Selection
- **Drag-to-select** any screen region
- Transparent selection box (no blue tint)
- Accurate coordinate mapping (works on all DPIs)
- Minimum 50x50px selection

### Side Panel UI
- Persistent while browsing
- Real-time image preview
- Dialogue-to-image mapping
- Remove/change images easily

### Session Management
- Auto-syncs with Flask app
- Stores session in Chrome storage
- Polls for updates every 2 seconds
- Works across browser restarts

---

## 🔧 Configuration

### Video Settings
- **Resolution**: 1080x1920 (vertical)
- **Frame Rate**: 30 FPS
- **Audio**: 44.1kHz stereo
- **Format**: MP4 (H.264)

### Caption Styling
- Font: Arial Bold
- Size: 60px
- Color: White with black outline
- Position: Bottom third
- Shadow: 3px offset

### Instagram Upload
- Requires `PUBLIC_URL` environment variable
- Uses Instagram Graph API
- Supports video containers and publishing
- Auto-cleanup after upload (optional)

---

## 📸 Screenshots

### Main Interface
![Main App](screenshots/main_app.png)

### Chrome Extension
![Extension](screenshots/extension.png)

### Generated Video
![Video Output](screenshots/output.png)

---

## 🐛 Troubleshooting

**Extension shows "No session found":**
- Parse script in Flask app first
- Refresh extension side panel
- Check Flask is running on localhost:8000

**Images not syncing:**
- Check browser console for errors
- Verify Flask API is responding
- Ensure both are polling (every 2s)

**Instagram upload fails:**
- Set `PUBLIC_URL` in .env (use ngrok)
- Check access token is valid
- Ensure video is publicly accessible

**Area selection captures wrong area:**
- Reload extension after updates
- Check device pixel ratio in console
- Ensure viewport is not zoomed

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - feel free to use for personal or commercial projects!

---

## 🙏 Acknowledgments

- **ElevenLabs** - AI voice generation
- **OpenAI** - Script parsing assistance
- **MoviePy** - Video processing
- **Instagram Graph API** - Social media integration

---

## 📞 Contact

Questions? Issues? Feature requests?
- Open an issue on GitHub
- Or reach out via [your contact method]

---

**⭐ Star this repo if you found it useful!**

Made with ❤️ for creating viral content
