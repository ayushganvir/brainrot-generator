# ⚡ Quick Setup - Script Mode

## 🚀 Get Started in 3 Steps

### Step 1: Verify Dependencies

All required dependencies are already installed with MoviePy!

```bash
cd /Users/ayushganvir/Documents/code/content_gen
# No additional installs needed - MoviePy handles audio concatenation
```

### Step 2: Add ElevenLabs API Key

```bash
# Add to your .env file
echo "ELEVENLABS_API_KEY=your_elevenlabs_api_key_here" >> .env
```

Your `.env` should now have:
```
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
```

### Step 3: Restart Server

```bash
python app.py
```

---

## 🎭 Access Script Mode

Open in browser: **http://localhost:8000/script**

---

## 📝 Quick Test

1. **Upload** any video
2. **Paste** this example script:

```
Peter: Y'know, Stewie, OpenAI is kinda like having a genius buddy who never sleeps.
Stewie: Indeed, Peter. OpenAI represents a monumental leap in computational reasoning.
Peter: Heh, yeah, and it even helps me write emails so Lois stops yelling at me.
Stewie: A noble application of advanced AI.
```

3. Click **"Parse Script & Load Voices"**
4. **Select voices** for Peter and Stewie from dropdowns
5. Click **"Preview Audio"** to hear it
6. Click **"Generate Video"**
7. **Download** your video!

---

## 🔄 Switch Between Modes

- **Topic Mode**: http://localhost:8000/ (AI-generated scripts)
- **Script Mode**: http://localhost:8000/script (Your custom scripts)

Use the mode switcher links in the top-right of each page!

---

## ✨ Key Features

- **Two Speakers**: Assign different ElevenLabs voices to each speaker
- **Natural Pacing**: Automatic 1-second gaps when speaker changes
- **Audio Preview**: Test voices before generating video
- **Auto Loop**: Background video loops if too short

---

## 📖 Full Documentation

- **SCRIPT_MODE_GUIDE.md** - Complete guide
- **SCRIPT_MODE_SUMMARY.txt** - Quick reference
- **README.md** - General documentation

---

## 🎉 You're Ready!

**All your requirements are implemented:**
- ✅ Custom script input (no AI generation)
- ✅ 2-speaker dialogue support
- ✅ ElevenLabs voice integration
- ✅ Voice selection per speaker
- ✅ Audio preview before generation
- ✅ NO DALL-E images
- ✅ NO OpenAI audio
- ✅ Beautiful UI with linear dialogue display

**Try it now:** http://localhost:8000/script 🚀

