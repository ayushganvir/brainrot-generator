# 🎯 Caption Synchronization Guide

## Overview

This guide explains how audio and text captions are synchronized in the video generation pipeline.

---

## 🎬 Current Implementation: Whisper STT (RECOMMENDED)

### **How It Works**

```
1. Generate audio with ElevenLabs (per speaker, with 1s gaps)
2. Concatenate all audio segments into final_audio.mp3
3. Send final_audio.mp3 to OpenAI Whisper STT
4. Whisper transcribes and returns word-level timestamps
5. Generate caption clips with exact timing
6. Overlay captions on video
```

### **Why Whisper?**

✅ **Advantages:**
- **Fully Automatic**: No manual timing calculations needed
- **Very Accurate**: State-of-the-art speech recognition
- **Handles Everything**: Works with concatenated audio, gaps, and all
- **Ready-to-Use Format**: Returns SRT-compatible timestamps
- **Already Implemented**: Working out of the box

❌ **Disadvantages:**
- Extra API call (~$0.006 per minute of audio)
- Requires OpenAI API key

### **Code Flow**

```python
# In app.py - generate_video_script_mode()

# Step 1: Generate audio with ElevenLabs
audio_result = generate_dialogue_audio(
    elevenlabs_api_key, 
    dialogue, 
    voice_mapping
)

# Step 2: Concatenate segments (with 1s gaps)
final_audio = concatenate_audio_segments(
    audio_result["segments"],
    "/tmp/final_audio.mp3"
)

# Step 3: Generate captions via Whisper
caption_handler = CaptionHandler()
subtitles_path, caption_clips = await caption_handler.process(
    final_audio,  # Whisper analyzes this
    captions_color="white",
    shadow_color="black"
)

# Step 4: Overlay on video
final_video = CompositeVideoClip([video_with_audio] + caption_clips)
```

### **What Whisper Returns**

```json
{
  "text": "Y'know, Stewie, OpenAI is kinda like having a genius buddy...",
  "words": [
    {
      "word": "Y'know",
      "start": 0.0,
      "end": 0.52
    },
    {
      "word": "Stewie",
      "start": 0.52,
      "end": 1.08
    },
    {
      "word": "OpenAI",
      "start": 1.08,
      "end": 1.64
    }
    // ... more words with precise timing
  ]
}
```

The `CaptionHandler` automatically:
- Converts this to caption clips
- Positions them on screen
- Handles timing and transitions

---

## 🆕 Alternative: ElevenLabs Timestamps (ADVANCED)

### **How It Works**

ElevenLabs offers a `convert_with_timestamps` endpoint that returns character-level timing data **as it generates audio**.

### **Advantages:**

✅ Direct from source (no transcription needed)
✅ Character-level precision
✅ No additional API call

### **Challenges:**

❌ Need to track cumulative timing across segments
❌ Must account for 1-second gaps we added
❌ More complex implementation
❌ Need to convert character-level → word-level

### **Example Code**

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="your_key")

response = client.text_to_speech.convert_with_timestamps(
    voice_id="voice_id_here",
    text="Y'know, Stewie, OpenAI is kinda like..."
)

audio_base64 = response['audio_base64']
alignment = response['alignment']

# alignment contains:
# {
#   "characters": ["Y", "'", "k", "n", "o", "w", ",", " ", "S", ...],
#   "character_start_times_seconds": [0.0, 0.05, 0.1, 0.15, ...],
#   "character_end_times_seconds": [0.05, 0.1, 0.15, 0.2, ...]
# }
```

### **Implementation Challenge**

Since we generate audio **per dialogue line** and then concatenate:

```
Segment 0 (Peter): "Y'know..." 
  → Duration: 3.2s
  → Timestamps: 0.0 - 3.2s

[1 second gap added]

Segment 1 (Stewie): "Indeed..."
  → Duration: 4.1s
  → Original timestamps: 0.0 - 4.1s
  → Need to offset by: 3.2s + 1.0s = 4.2s
  → Adjusted timestamps: 4.2 - 8.3s

[1 second gap added]

Segment 2 (Peter): "Heh..."
  → Duration: 2.5s
  → Original timestamps: 0.0 - 2.5s
  → Need to offset by: 3.2s + 1.0s + 4.1s + 1.0s = 9.3s
  → Adjusted timestamps: 9.3 - 11.8s
```

You'd need to:
1. Get timestamps for each segment
2. Calculate cumulative offsets
3. Add gap durations
4. Merge all timing data
5. Convert character-level → word-level
6. Generate caption clips

---

## 🏆 Recommendation

**Use Whisper** (current implementation) because:

1. ✅ **Simple**: Works out of the box
2. ✅ **Accurate**: Industry-leading speech recognition
3. ✅ **Maintainable**: Easy to understand and debug
4. ✅ **Cost-effective**: ~$0.006/min is negligible
5. ✅ **Proven**: Already working in Topic Mode

The ElevenLabs timestamp approach is **possible** but adds complexity for minimal benefit.

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ USER INPUT                                              │
│ - Script with 2 speakers                               │
│ - Background video                                      │
│ - Voice assignments                                     │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ AUDIO GENERATION (ElevenLabs)                          │
│                                                         │
│ For each dialogue line:                                │
│   → Generate audio with assigned voice                 │
│   → Save segment_N.mp3                                 │
│                                                         │
│ Result:                                                 │
│   - segment_0.mp3 (Peter, 3.2s)                       │
│   - segment_1.mp3 (Stewie, 4.1s)                      │
│   - segment_2.mp3 (Peter, 2.5s)                       │
│   - segment_3.mp3 (Stewie, 3.8s)                      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ CONCATENATION (MoviePy)                                │
│                                                         │
│ Combine segments with 1s gaps:                         │
│   segment_0 (0.0-3.2s)                                 │
│   [1s gap]                                             │
│   segment_1 (4.2-8.3s)                                 │
│   [1s gap]                                             │
│   segment_2 (9.3-11.8s)                                │
│   [1s gap]                                             │
│   segment_3 (12.8-16.6s)                               │
│                                                         │
│ Result: final_audio.mp3 (16.6s)                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ CAPTION GENERATION (Whisper STT)                       │
│                                                         │
│ Send final_audio.mp3 to OpenAI Whisper                │
│                                                         │
│ Whisper returns:                                        │
│   - Full transcription                                 │
│   - Word-level timestamps                              │
│                                                         │
│ Example:                                                │
│   "Y'know" → 0.0-0.52s                                 │
│   "Stewie" → 0.52-1.08s                                │
│   "OpenAI" → 1.08-1.64s                                │
│   "is" → 1.64-1.82s                                    │
│   ...                                                   │
│   "Indeed" → 4.2-4.78s (after gap!)                    │
│   "Peter" → 4.78-5.24s                                 │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ VIDEO COMPOSITION (MoviePy)                            │
│                                                         │
│ 1. Load background video                               │
│ 2. Loop if too short                                   │
│ 3. Crop to 9:16                                        │
│ 4. Sync final_audio.mp3                                │
│ 5. Overlay caption clips (using Whisper timestamps)   │
│ 6. Render final MP4                                    │
└────────────────────┬────────────────────────────────────┘
                     ↓
              FINAL VIDEO
         (Audio + Captions Synced!)
```

---

## 🔧 Technical Details

### **Whisper API Call**

```python
# In mediachain/examples/moviepy_engine/src/captions/caption_handler.py

import openai

def generate_speech_to_text(provider, api_key, audio_file_path):
    client = openai.OpenAI(api_key=api_key)
    
    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",  # Gets word timestamps
            timestamp_granularities=["word"]
        )
    
    return response
```

### **Caption Clip Generation**

```python
# CaptionHandler converts Whisper output to MoviePy clips

for word_data in whisper_response['words']:
    word = word_data['word']
    start = word_data['start']
    end = word_data['end']
    
    # Create text clip
    text_clip = TextClip(
        word,
        fontsize=60,
        color='white',
        stroke_color='black',
        stroke_width=2
    ).set_start(start).set_end(end).set_position('center')
    
    caption_clips.append(text_clip)
```

---

## 💡 Best Practices

1. **Always use Whisper for captions** unless you have a specific reason not to
2. **Test audio preview first** to ensure voices sound good
3. **Check video duration** - auto-loop handles this
4. **Review captions** in the final video for accuracy
5. **Keep scripts clear** - better transcription accuracy

---

## 🚀 Future Enhancements

If you want to implement ElevenLabs timestamps in the future:

1. Modify `generate_dialogue_audio()` to use `convert_with_timestamps`
2. Store timing data for each segment
3. Calculate cumulative offsets
4. Convert character → word timestamps
5. Generate caption clips manually

**But honestly, Whisper is simpler and better!** 🎯

---

## 📚 References

- [ElevenLabs Timestamps API](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [MoviePy TextClip](https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html#textclip)

---

**Current Status: ✅ Fully Implemented and Working!**


