# 🔍 Debugging Guide

This guide helps you debug issues when generating videos.

## 📊 Understanding the Logs

All logs now use a structured format with tags for easy tracking:

```
[COMPONENT] Message
```

### Log Tags Reference

| Tag | Component | What It Does |
|-----|-----------|--------------|
| `[JOB xxx]` | Job Manager | Tracks a specific video generation request |
| `[VALIDATE]` | Input Validation | Checks parameters are valid |
| `[VIDEO_INPUT]` | Video Loading | Loads and analyzes uploaded video |
| `[SCRIPT]` | AI Script Generation | Generates story script |
| `[CREATE_QUESTION]` | Question Creation | Creates intro question clip |
| `[QUESTION]` | Question Audio | Generates TTS for question |
| `[AUDIO]` | Story Audio | Generates TTS for story |
| `[TIMING]` | Timing Calculation | Calculates video cut times |
| `[CUT]` | Video Cutting | Cuts background video |
| `[CUT_VIDEO]` | Video Cutting Details | Detailed cut operation info |
| `[QUESTION_VIDEO]` | Question Composition | Composes question segment |
| `[STORY_VIDEO]` | Story Composition | Composes story segment |
| `[CAPTIONS]` | Caption Generation | Generates word-by-word captions |
| `[IMAGES]` | Image Generation | AI image generation |
| `[COMPOSITION]` | Final Composition | Combines all segments |
| `[RENDER]` | Video Rendering | Renders final video |
| `[CLEANUP]` | Cleanup | Removes temporary files |
| `[SUCCESS]` | Success | Video completed successfully |
| `[ERROR]` | Error | Something went wrong |

### Log Symbols

| Symbol | Meaning |
|--------|---------|
| `✓` | Success / Step completed |
| `✗` | Error / Step failed |
| `⚠️` | Warning / Non-critical issue |

## 🚨 Common Errors & Solutions

### 1. "Background video too short!"

**Error Message:**
```
[TIMING] ✗ Background video too short! Required: XX.XXs, Available: YY.YYs
```

**Cause:** Your background video is shorter than the total audio duration (question + story).

**Solution:**
- Upload a longer background video (at least 60 seconds recommended)
- Or use a shorter/simpler topic that generates less audio

**How to check before uploading:**
```bash
# Check video duration with ffprobe
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 your_video.mp4
```

---

### 2. "Error cutting video: Accessing time t=XX.XX seconds, with clip duration=YY seconds"

**Error Message:**
```
[CUT_VIDEO] Error cutting video: Error in file ..., Accessing time t=15.00-15.04 seconds, with clip duration=14 seconds
```

**Cause:** Code tried to cut video beyond its actual length (now fixed with validation).

**Solution:** This error should no longer occur after the fixes. If it does:
1. Check if your video file is corrupted
2. Try re-encoding the video:
   ```bash
   ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4
   ```

---

### 3. "'NoneType' object has no attribute 'endswith'"

**Error Message:**
```
ERROR:root:Error in video generation: 'NoneType' object has no attribute 'endswith'
```

**Cause:** `cut_video()` returned `None` and downstream code tried to use it (now fixed with validation).

**Solution:** This should be fixed now. The code now:
- Returns proper error messages
- Validates that cut_video succeeded before continuing
- Shows the actual reason for failure

---

### 4. "OPENAI_API_KEY not set in environment"

**Error Message:**
```
[JOB xxx] ✗ OPENAI_API_KEY not configured
```

**Cause:** Missing or invalid API key.

**Solution:**
```bash
# Check if .env exists
ls -la .env

# If missing, create it
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# If exists, check contents
cat .env

# Restart server after changing .env
```

---

### 5. "Failed to generate script"

**Error Message:**
```
[SCRIPT] ✗ Failed to generate script
```

**Possible Causes:**
- Invalid/expired OpenAI API key
- No credits in OpenAI account
- Network issues
- API rate limits

**Solution:**
1. Verify API key is valid:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

2. Check OpenAI account credits at: https://platform.openai.com/account/usage

3. Check server logs for detailed error

---

### 6. Video file format issues

**Error Message:**
```
[JOB xxx] Invalid file format: video.xyz
```

**Supported Formats:**
- MP4 (recommended)
- MOV
- AVI
- MKV

**If you have an unsupported format, convert it:**
```bash
ffmpeg -i input.webm -c:v libx264 -c:a aac output.mp4
```

---

### 7. Memory/Performance Issues

**Symptoms:**
- Server crashes during rendering
- Very slow processing
- "Killed" errors

**Solutions:**

**1. Reduce video resolution:**
```bash
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
```

**2. Disable images temporarily:**
- Uncheck "Add AI-generated images" in UI
- This reduces memory usage significantly

**3. Close other applications** to free RAM

**4. Increase system swap/virtual memory**

---

## 🔍 How to Debug Step-by-Step

### 1. Check Server Logs

The terminal where you ran `./run_server.sh` or `python app.py` shows all logs.

**What to look for:**
```bash
# Success pattern
[JOB xxx] New video generation request
... (lots of processing)
[SUCCESS] ✓✓✓ VIDEO GENERATION COMPLETE ✓✓✓

# Failure pattern
[JOB xxx] New video generation request
... (processing)
[ERROR] ✗✗✗ VIDEO GENERATION FAILED ✗✗✗
[ERROR] Exception: (error details here)
```

### 2. Identify the Failed Step

Logs are sequential, so find the last successful `✓` before the error:

```
[TIMING] ✓ Cut times calculated      ← Last success
[CUT] Cutting background video        ← Started this
[CUT_VIDEO] Error cutting video       ← Failed here!
```

### 3. Read the Error Details

Errors now include:
- What failed
- Why it failed
- Full traceback for debugging

Example:
```
[ERROR] ✗✗✗ VIDEO GENERATION FAILED ✗✗✗
[ERROR] Exception: Background video too short! Required: 45.23s, Available: 14.00s
```

### 4. Check File Paths

If files aren't found:
```bash
# From project root
ls -la uploads/        # Uploaded videos
ls -la outputs/        # Generated videos
ls -la mediachain/examples/moviepy_engine/assets/   # Temporary files
```

### 5. Verify Video Properties

```bash
# Check video info
ffprobe -v error -show_format -show_streams your_video.mp4

# Quick duration check
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 your_video.mp4
```

---

## 🧪 Testing Individual Components

### Test OpenAI API

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Test script generation
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say hello"}]
)
print(response.choices[0].message.content)
```

### Test TTS

```python
from mediachain.core.audio.text_to_speech.tts_generation import generate_text_to_speech

audio_path = generate_text_to_speech(
    "openai", 
    "your-api-key", 
    "Test audio", 
    voice="echo"
)
print(f"Audio generated: {audio_path}")
```

### Test Video Loading

```python
from moviepy.editor import VideoFileClip

clip = VideoFileClip("your_video.mp4")
print(f"Duration: {clip.duration}s")
print(f"Size: {clip.w}x{clip.h}")
print(f"FPS: {clip.fps}")
clip.close()
```

---

## 📈 Performance Optimization

### If Generation Takes Too Long

**Normal times:**
- Simple video (no images): 2-5 minutes
- With images: 5-10 minutes

**If it's slower:**

1. **Disable images** - Saves 50-70% time
2. **Use shorter topics** - Less audio = faster
3. **Use lower resolution videos** - Faster processing
4. **Check CPU usage** - Should be high during render
5. **Close other apps** - Free up resources

---

## 🆘 Getting More Help

### Enable Debug Mode

Edit `app.py`:
```python
# Change INFO to DEBUG
logging.basicConfig(level=logging.DEBUG)
```

### Save Logs to File

```bash
# Run server and save logs
python app.py 2>&1 | tee server.log
```

### Check System Resources

```bash
# CPU and memory usage
top

# Disk space
df -h

# Check if FFmpeg works
ffmpeg -version
```

---

## 📝 Reporting Issues

If you need to report an issue, include:

1. **Error message** from logs
2. **Full log output** around the error (10-20 lines before and after)
3. **Video properties**:
   ```bash
   ffprobe -v error -show_format -show_streams your_video.mp4
   ```
4. **System info**:
   - OS and version
   - Python version: `python --version`
   - RAM available
   - Disk space

5. **What you tried**:
   - Topic used
   - Video size/duration
   - Any settings changed

---

## ✅ Verification Checklist

Before reporting issues, verify:

- [ ] Video is at least 60 seconds long
- [ ] Video format is MP4, MOV, AVI, or MKV
- [ ] OPENAI_API_KEY is set and valid
- [ ] OpenAI account has credits
- [ ] FFmpeg is installed: `ffmpeg -version`
- [ ] Server logs show detailed error
- [ ] Enough disk space (at least 1GB free)
- [ ] Video file isn't corrupted

---

## 🎯 Quick Fixes Checklist

Try these in order:

1. ☐ Use a longer background video (60+ seconds)
2. ☐ Use MP4 format (re-encode if needed)
3. ☐ Disable AI images
4. ☐ Use simpler/shorter topic
5. ☐ Verify API key is valid
6. ☐ Restart the server
7. ☐ Clear uploads/ and outputs/ folders
8. ☐ Try with a fresh video file

---

**Still stuck?** Check the full logs - they now tell you exactly what's happening at every step! 🔍

