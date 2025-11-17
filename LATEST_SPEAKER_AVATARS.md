# 🎉 NEW FEATURE: Speaker Avatars

## What's New?

You can now add **profile pictures for each speaker** that appear at the bottom corners when they're talking! This makes your videos more engaging and helps viewers visually identify who's speaking.

## ✨ Quick Overview

### Visual Appearance

```
┌─────────────────────────────┐
│   Dialogue Image (top)      │
│                             │
│   Background Video          │
│                             │
│ [Peter]         [Stewie]    │  ← Your speaker avatars here!
│ (bottom-left)  (bottom-right)
└─────────────────────────────┘
```

### Key Features

✅ **Dynamic appearance** - Avatars only show when that speaker is talking  
✅ **Bottom corner positioning** - Speaker 1 (left), Speaker 2 (right)  
✅ **Square format** - Clean, professional look  
✅ **Instant transitions** - Pop in/out without fading  
✅ **Perfectly synced** - Timing matches audio segments exactly  

## 🚀 How to Use

### Step-by-Step

1. **Go to Script Mode** at `http://localhost:8000/script`
2. **Click "Parse Script & Load Voices"** after entering your dialogue
3. **Upload avatars** for each speaker:
   - Click "📷 Upload Avatar" button under each speaker
   - Select an image file (JPG, PNG, etc. - max 10MB)
   - Preview shows immediately
   - Click "Remove" to change your selection
4. **Generate Video** as usual!

### That's it! 🎬

Your avatars will automatically appear in the video at the right times.

## 📋 Requirements

- **File format:** Any image (JPG, PNG, GIF, WebP)
- **File size:** Max 10MB per avatar
- **Aspect ratio:** Any (will be resized to 120px height)
- **Optional:** You can skip avatars for one or both speakers

## 💡 Tips for Best Results

1. **Use clear headshots** - Face shots work best
2. **Square images** - Upload square images for best results
3. **High contrast** - Avatars with clear outlines stand out better
4. **Consistent style** - Use similar image styles for both speakers
5. **Test first** - Generate a short test video to check positioning

## 📐 Technical Details

### Positioning

- **Size:** 120px height (maintains aspect ratio)
- **Speaker 1 Position:** Bottom-left corner
  - 20px from left edge
  - 100px from bottom
- **Speaker 2 Position:** Bottom-right corner
  - 20px from right edge
  - 100px from bottom

### Timing

Avatars use the exact same timing as audio segments:
- Appear when speaker starts talking
- Disappear when speaker stops
- 1-second gap between speaker changes (no avatar shown)

## 🎨 Example Usage

### Sample Dialogue

```
Peter: Y'know, Stewie, OpenAI is kinda like having a genius buddy.
[Peter's avatar appears at bottom-left]

Stewie: Indeed, Peter. OpenAI represents a monumental leap.
[Switch: Stewie's avatar at bottom-right]

Peter: Heh, yeah, and it even helps me write emails.
[Switch: Peter's avatar at bottom-left]
```

## 🔧 Customization

Want to adjust positioning? Edit `app.py`:

```python
# Inside add_speaker_avatars_to_video()
AVATAR_SIZE = 150         # Bigger avatars
MARGIN = 50               # More space from edges
BOTTOM_OFFSET = 150       # Higher on screen
```

## 📊 Code Changes

### UI Changes (`static/script_mode.html`)

✅ Added avatar upload UI for each speaker  
✅ Drag-and-drop support  
✅ Preview thumbnails  
✅ Form data includes speaker avatars  

### Backend Changes (`app.py`)

✅ New endpoint parameters: `speaker1_avatar`, `speaker2_avatar`  
✅ New function: `add_speaker_avatars_to_video()`  
✅ Avatar file handling and saving  
✅ Integration into video composition  

### Layer Order (bottom to top)

```python
CompositeVideoClip([
    video_with_audio,    # 1. Background
    image_clips,         # 2. Dialogue images (top)
    avatar_clips,        # 3. Speaker avatars (bottom) ← NEW
    caption_clips        # 4. Captions
])
```

## 🐛 Troubleshooting

### Avatar not showing?

- Check browser console for upload errors
- Verify file size is under 10MB
- Look for `[AVATAR]` tags in server logs
- Ensure speaker names match script exactly

### Wrong position?

- Check video dimensions in logs
- Review `[AVATAR]` position coordinates
- Adjust `MARGIN`/`BOTTOM_OFFSET` if needed

## 📚 Related Features

- **Dialogue Images** ([DIALOGUE_IMAGES_FEATURE.md](DIALOGUE_IMAGES_FEATURE.md))
- **Audio Normalization** ([AUDIO_NORMALIZATION.md](AUDIO_NORMALIZATION.md))
- **Audio Reuse** ([AUDIO_REUSE_FEATURE.md](AUDIO_REUSE_FEATURE.md))
- **Caption Sync** ([CAPTION_SYNC_GUIDE.md](CAPTION_SYNC_GUIDE.md))

## 🎯 What's Next?

Try it out! The feature is ready to use in Script Mode.

For detailed technical documentation, see:
**[SPEAKER_AVATARS_FEATURE.md](SPEAKER_AVATARS_FEATURE.md)**

---

**Happy video creating! 🚀**


