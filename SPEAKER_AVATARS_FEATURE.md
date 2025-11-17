# Speaker Avatar Feature

## Overview

The speaker avatar feature allows you to upload profile pictures for each speaker in your dialogue. These images appear at the bottom corners of the video when their respective speaker is talking, providing a visual indicator of who is currently speaking.

## 🎯 Visual Layout

```
┌────────────────────────────────┐
│  Dialogue Images (optional)    │  ← Top third (existing feature)
│                                │
│                                │
│    Background Video            │
│                                │
│                                │
│                                │
├────────────────────────────────┤
│ [Speaker1]        [Speaker2]   │  ← NEW: Speaker avatars
│   Avatar            Avatar     │     (bottom corners, appear when speaking)
│ (bottom-left)   (bottom-right) │
└────────────────────────────────┘
```

## 📋 Features

### Avatar Positioning

- **Speaker 1:** Bottom-left corner
- **Speaker 2:** Bottom-right corner
- **Size:** 120px height (maintains aspect ratio)
- **Margins:** 20px from screen edges
- **Bottom offset:** 100px from bottom of screen

### Behavior

1. **Dynamic Appearance:** Avatars only appear when their respective speaker is talking
2. **Instant Transitions:** Avatars pop in/out without fade effects
3. **Synchronized Timing:** Perfectly synced with audio segments
4. **Square Format:** Avatars maintain their square shape (not circular)

## 🎨 How to Use

### Step 1: Upload Avatars in UI

1. Go to **Script Mode** (`/script`)
2. Click **"Parse Script & Load Voices"**
3. For each speaker, you'll see an avatar upload section:
   - Click "📷 Upload Avatar"
   - Select an image file (JPG, PNG, etc.)
   - Preview appears with 60x60 thumbnail
   - Click "Remove" to delete and re-upload

### Step 2: Generate Video

The avatars will automatically be included in the final video:
- They appear at the exact timing when the speaker talks
- They disappear when the speaker stops talking
- Seamless switching between speakers

## 🛠️ Technical Details

### File Requirements

- **Formats:** Any image format (JPG, PNG, GIF, WebP, etc.)
- **Size limit:** 10MB per avatar
- **Aspect ratio:** Any (will be resized to 120px height)
- **Optional:** You can skip avatars for one or both speakers

### Positioning Constants

```python
AVATAR_SIZE = 120        # Height in pixels
MARGIN = 20              # Distance from screen edge
BOTTOM_OFFSET = 100      # Distance from bottom
```

### Positioning Calculations

**Speaker 1 (bottom-left):**
```python
x = 20px (MARGIN)
y = video_height - 120 (AVATAR_SIZE) - 100 (BOTTOM_OFFSET)
# Example for 1920px tall video: (20, 1700)
```

**Speaker 2 (bottom-right):**
```python
x = video_width - 120 (AVATAR_SIZE) - 20 (MARGIN)
y = video_height - 120 (AVATAR_SIZE) - 100 (BOTTOM_OFFSET)
# Example for 1080px wide video: (940, 1700)
```

## 📊 Layer Composition

The final video is composed of these layers (bottom to top):

```python
1. Background video (base layer)
2. Dialogue images (top third, optional)
3. Speaker avatars (bottom corners, when speaking)
4. Captions (center/bottom)
```

## 🔧 Customization

If you want to customize avatar appearance, edit these constants in `app.py`:

```python
# Inside add_speaker_avatars_to_video() function
AVATAR_SIZE = 150         # Make avatars bigger
MARGIN = 50               # More space from edges
BOTTOM_OFFSET = 150       # Position higher on screen
```

## 📝 Code Implementation

### Backend (`app.py`)

**New endpoint parameters:**
```python
speaker1_avatar: UploadFile = File(None)
speaker2_avatar: UploadFile = File(None)
```

**New function:**
```python
def add_speaker_avatars_to_video(
    video_clip,
    speaker_avatars: dict,
    audio_segments: list,
    speakers_list: list
) -> list
```

**Integration:**
```python
avatar_clips = add_speaker_avatars_to_video(
    cropped_video,
    speaker_avatars,
    audio_result["segments"],
    speakers
)

final_video = CompositeVideoClip([
    video_with_audio,
    image_clips,      # Dialogue images
    avatar_clips,     # Speaker avatars (NEW)
    caption_clips     # Captions
])
```

### Frontend (`static/script_mode.html`)

**New state:**
```javascript
let speakerAvatars = {
    speaker1: null,  // File object
    speaker2: null
};
```

**Upload handling:**
- File input with `accept="image/*"`
- Validation: file type and size (10MB max)
- Preview with 60x60 thumbnail
- Remove button to clear selection

**Form submission:**
```javascript
if (speakerAvatars.speaker1) {
    formData.append('speaker1_avatar', speakerAvatars.speaker1);
}
if (speakerAvatars.speaker2) {
    formData.append('speaker2_avatar', speakerAvatars.speaker2);
}
```

## 🎬 Example Usage

### Sample Dialogue with Avatars

```
Peter: Y'know, Stewie, OpenAI is kinda like having a genius buddy who never sleeps.
[Peter's avatar appears at bottom-left]

Stewie: Indeed, Peter. OpenAI represents a monumental leap in computational reasoning.
[Peter's avatar disappears, Stewie's avatar appears at bottom-right]

Peter: Heh, yeah, and it even helps me write emails so Lois stops yelling at me.
[Stewie's avatar disappears, Peter's avatar appears at bottom-left]
```

## 🐛 Troubleshooting

### Avatar not appearing?

1. **Check logs:** Look for `[AVATAR]` tags in console output
2. **Verify upload:** Make sure file was uploaded successfully
3. **Check speaker names:** Must match exactly with script
4. **File size:** Ensure under 10MB

### Avatar in wrong position?

- Check `MARGIN` and `BOTTOM_OFFSET` values
- Verify video dimensions (logged during processing)
- Review `[AVATAR]` logs for position coordinates

### Avatar timing off?

- Avatars use same timing as audio segments
- Check if ElevenLabs audio generation succeeded
- Look for timing info in `[AVATAR]` logs

## 📚 Related Features

- **Dialogue Images:** Upload images for specific dialogue lines (top third)
- **Audio Normalization:** Ensures consistent volume across all dialogue
- **Audio Reuse:** Preview audio is reused to save API calls
- **Caption Sync:** Whisper-based captions synced with audio

## 💡 Tips

1. **Use clear headshots:** Face shots work best for avatars
2. **Square aspect ratio:** Upload square images for best results
3. **High contrast:** Avatars with clear outlines stand out better
4. **Consistent style:** Use similar image styles for both speakers
5. **Test first:** Generate a short test video to check positioning

## 🔄 Version History

- **v1.0 (Current):** Initial release with square avatars, instant transitions, bottom corner positioning


