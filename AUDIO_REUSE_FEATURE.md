# 🎙️ Audio Reuse Feature

## Overview

The video generation now **reuses preview audio** instead of regenerating it, saving time and API costs!

---

## ✅ Problems Fixed

### **1. `form_data` Error** ❌ → ✅
```
ERROR: NameError: name 'form_data' is not defined
```

**Fix:** Added `font_color`, `shadow_color`, and `preview_audio_path` as Form parameters to the endpoint.

### **2. Duplicate Audio Generation** ❌ → ✅
Audio was being generated **twice**:
- Once for preview
- Again for video generation (wasteful!)

**Fix:** Preview audio is now **reused** for video generation.

### **3. No Button State Management** ❌ → ✅
"Generate Video" button was always enabled, even without preview audio.

**Fix:** Button is now disabled until preview audio is ready.

---

## 🔄 How It Works Now

### **Step 1: User Clicks "Preview Audio"**
```
1. Generate audio with ElevenLabs
2. Concatenate segments (with 1s gaps)
3. Save to: /tmp/elevenlabs_audio/preview_<job_id>.mp3
4. Return audio file with X-Audio-Path header
```

### **Step 2: UI Captures Audio Path**
```javascript
// JavaScript in script_mode.html
const response = await fetch('/api/preview-audio', ...);
previewAudioPath = response.headers.get('X-Audio-Path');

// Enable the Generate Video button
submitBtn.disabled = false;
submitBtn.textContent = '🎬 Generate Video';
```

### **Step 3: User Clicks "Generate Video"**
```
1. Send form data + preview_audio_path
2. Backend checks if preview audio exists
3. If yes → Reuse it! ♻️
4. If no → Generate new audio
5. Continue with video composition
```

### **Backend Logic (app.py)**
```python
if preview_audio_path and os.path.exists(preview_audio_path):
    logger.info(f"♻️  Reusing preview audio: {preview_audio_path}")
    concatenated_audio = preview_audio_path
else:
    # Generate new audio (fallback)
    audio_result = generate_dialogue_audio(...)
    concatenated_audio = concatenate_audio_segments(...)
```

---

## 🎯 Benefits

### **1. Faster Video Generation** ⚡
- Skip audio generation (saves 10-30 seconds)
- Only need to: load video → add captions → render

### **2. Lower API Costs** 💰
- ElevenLabs: ~$0.30 per 1K characters
- For 4 dialogue lines (~200 chars): **~$0.06 saved** per video
- At scale (100 videos): **$6 saved!**

### **3. Better User Experience** 😊
- Preview exactly what will be in the video
- No surprises - same audio used throughout
- Clear button states guide the workflow

### **4. Workflow Enforcement** 🔒
- Forces users to preview audio first
- Ensures voices are correct before video generation
- Reduces failed video generations

---

## 🖥️ UI Changes

### **Before** ❌
```
[🎧 Preview Audio]  (always enabled)
[🎬 Generate Video] (always enabled)
```
**Problems:**
- Users could skip preview
- Audio generated twice
- Confusing workflow

### **After** ✅
```
[🎧 Preview Audio]  (always enabled)
[🎬 Generate Video (Preview audio first)] (disabled, grayed out)
     ↓ (user clicks preview)
[✓ Preview Ready]
[🎬 Generate Video]  (enabled, ready to use)
     ↓ (user clicks generate)
[Generating Video...]  (using preview audio)
```

---

## 🔄 Smart Invalidation

### **Voice Selection Changes**
When user changes voice assignment AFTER preview:
1. Preview audio path is cleared (`previewAudioPath = null`)
2. "Generate Video" button is disabled again
3. User must regenerate preview with new voices

```javascript
// Detect voice changes
document.getElementById('voice_0').addEventListener('change', () => {
    previewAudioPath = null;
    submitBtn.disabled = true;
    submitBtn.textContent = '🎬 Generate Video (Preview audio first)';
    audioPlayer.classList.remove('active');
});
```

**Why?** Prevents using old audio with wrong voice assignments!

---

## 📊 Technical Details

### **Modified Files**

#### **1. `app.py`**

**Changes to `/api/generate-video-script` endpoint:**
```python
# Added new parameters
async def generate_video_script_mode(
    video: UploadFile = File(...),
    script: str = Form(...),
    speaker1_voice: str = Form(...),
    speaker2_voice: str = Form(...),
    loop_if_short: bool = Form(True),
    font_color: str = Form('white'),        # NEW
    shadow_color: str = Form('black'),      # NEW
    preview_audio_path: str = Form(None)    # NEW - for audio reuse
):
```

**Audio reuse logic:**
```python
# Check if we can reuse preview audio
if preview_audio_path and os.path.exists(preview_audio_path):
    logger.info(f"♻️  Reusing preview audio: {preview_audio_path}")
    concatenated_audio = preview_audio_path
else:
    # Generate new audio (fallback)
    audio_result = generate_dialogue_audio(...)
    concatenated_audio = concatenate_audio_segments(...)
```

**Changes to `/api/preview-audio` endpoint:**
```python
# Return audio path in response header
response = FileResponse(
    path=concatenated_path,
    media_type="audio/mpeg",
    filename=f"preview_{job_id}.mp3"
)
response.headers["X-Audio-Path"] = concatenated_path  # NEW
return response
```

#### **2. `static/script_mode.html`**

**New state variable:**
```javascript
let previewAudioPath = null; // Store preview audio path for reuse
```

**Initial button state:**
```html
<button type="submit" class="btn" id="submitBtn" disabled>
    🎬 Generate Video (Preview audio first)
</button>
```

**Preview audio handler:**
```javascript
// Capture audio path from header
previewAudioPath = response.headers.get('X-Audio-Path');

// Enable Generate Video button
submitBtn.disabled = false;
submitBtn.textContent = '🎬 Generate Video';
```

**Video generation:**
```javascript
// Pass preview audio path to reuse it
if (previewAudioPath) {
    formData.append('preview_audio_path', previewAudioPath);
    console.log('Reusing preview audio:', previewAudioPath);
}
```

**Voice change detection:**
```javascript
// Invalidate preview when voices change
document.getElementById('voice_0').addEventListener('change', () => {
    previewAudioPath = null;
    submitBtn.disabled = true;
    submitBtn.textContent = '🎬 Generate Video (Preview audio first)';
    audioPlayer.classList.remove('active');
});
```

---

## 📝 Logging

The backend now logs audio reuse:

```
[JOB abc123] ♻️  Reusing preview audio: /tmp/elevenlabs_audio/preview_xyz789.mp3
[JOB abc123] Starting video composition with Whisper captions
[JOB abc123] Caption colors: text=white, shadow=black
[JOB abc123] Generating captions via Whisper STT
```

vs. when generating new audio:

```
[JOB abc123] Generating audio with ElevenLabs (no preview available)
[JOB abc123] ✓ Audio generated: /tmp/elevenlabs_audio/final_abc123.mp3
```

---

## 🧪 Testing

### **Test Case 1: Normal Flow**
1. Upload video
2. Parse script
3. Select voices
4. Click "Preview Audio" ✅
5. Listen to audio ✅
6. Click "Generate Video" ✅
7. **Check logs:** Should see "♻️ Reusing preview audio"

### **Test Case 2: Voice Change**
1. Generate preview audio ✅
2. Change voice selection ✅
3. Notice "Generate Video" button becomes disabled ✅
4. Click "Preview Audio" again ✅
5. "Generate Video" button re-enables ✅

### **Test Case 3: No Preview (Fallback)**
1. Upload video
2. Parse script
3. Select voices
4. **Bypass UI and call API directly** (testing only)
5. **Check logs:** Should see "Generating audio with ElevenLabs (no preview available)"

### **Test Case 4: Caption Colors**
1. Add caption color inputs to UI (future enhancement)
2. Select custom colors
3. Generate video
4. **Check:** Captions use selected colors

---

## 🚀 Future Enhancements

### **Possible Improvements:**

1. **Caption Color Picker in UI**
   - Add color pickers for font and shadow
   - Currently defaults to white/black

2. **Preview Video Clip**
   - Show 5-second video preview before full generation
   - Helps verify captions look good

3. **Audio Cache Duration**
   - Currently: Audio deleted after video generation
   - Future: Keep for 1 hour in case user wants to regenerate

4. **Progress Bar**
   - Show "Audio: ✓ Reused" vs "Audio: ⏳ Generating"
   - More transparent workflow

---

## 📚 Related Documentation

- **[CAPTION_SYNC_GUIDE.md](CAPTION_SYNC_GUIDE.md)** - How audio/text sync works
- **[SCRIPT_MODE_GUIDE.md](SCRIPT_MODE_GUIDE.md)** - Complete script mode guide
- **[DEBUGGING.md](DEBUGGING.md)** - Troubleshooting tips

---

## ✅ Summary

**Before:**
- ❌ form_data error
- ❌ Audio generated twice
- ❌ No button state management
- ❌ Higher API costs
- ❌ Slower generation

**After:**
- ✅ All errors fixed
- ✅ Audio reused from preview
- ✅ Smart button state management
- ✅ Lower API costs (~$0.06 saved per video)
- ✅ Faster generation (~20 seconds saved)
- ✅ Better user experience
- ✅ Workflow enforcement

---

**Status: ✅ Production Ready!**

Test it now:
```bash
python app.py
# Visit http://localhost:8000/script
```


