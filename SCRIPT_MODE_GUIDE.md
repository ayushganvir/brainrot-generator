# 🎭 Script Mode Guide

## Overview

**NEW FEATURE**: Create videos with custom dialogue scripts using ElevenLabs voices for multiple speakers!

## 🎯 What's New

### Two Modes Available:

1. **Topic Mode** (Original) - `http://localhost:8000/`
   - AI generates script based on topic
   - Uses OpenAI TTS
   - Single narrator style

2. **Script Mode** (NEW) - `http://localhost:8000/script`
   - You provide the dialogue script
   - Uses ElevenLabs voices
   - Multi-speaker conversations
   - Voice assignment per speaker
   - Audio preview before generation

---

## 🚀 Using Script Mode

### Step 1: Access Script Mode

Visit: **http://localhost:8000/script**

### Step 2: Upload Background Video

Upload any MP4, MOV, AVI, or MKV file (same as before)

### Step 3: Write Your Dialogue Script

**Format Requirements:**
- Exactly **2 speakers**
- Format: `SpeakerName: Their dialogue`
- One line per dialogue segment

**Example Script:**
```
Peter: Y'know, Stewie, OpenAI is kinda like having a genius buddy who never sleeps. You ask it anything—boom! It's got answers faster than Cleveland running from trouble.

Stewie: Indeed, Peter. OpenAI represents a monumental leap in computational reasoning. It crafts text, solves problems, even generates ideas with unsettling precision.

Peter: Heh, yeah, and it even helps me write emails so Lois stops yelling at me.

Stewie: A noble application of advanced AI—preventing maternal outrage. Truly, OpenAI is shaping the future, even if your use case is… tragically simple.
```

### Step 4: Parse Script & Load Voices

Click **"Parse Script & Load Voices"**

The system will:
- ✓ Parse your dialogue
- ✓ Extract both speakers
- ✓ Fetch available ElevenLabs voices
- ✓ Show dialogue preview

### Step 5: Assign Voices

Select an ElevenLabs voice for each speaker:
- **Speaker 1** → Choose voice (e.g., "Peter - Narrative")
- **Speaker 2** → Choose voice (e.g., "Stewie - Young British")

**Dialogue Preview** shows all segments with speakers highlighted.

### Step 6: Preview Audio (Optional)

Click **"🎧 Preview Audio"**

- Generates full dialogue audio
- Plays preview in browser
- Confirm voices sound correct
- Regenerate if needed

### Step 7: Generate Video

Click **"🎬 Generate Video"**

The system will:
1. Generate audio for each speaker with ElevenLabs
2. Concatenate all dialogue segments
3. Generate captions (using Whisper STT)
4. Compose video with background
5. Render final video

---

## 🎤 ElevenLabs Integration

### API Key Setup

Add to your `.env` file:
```bash
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_API_KEY=your_openai_key_here  # Still needed for captions
```

### Available Voices

The API automatically fetches all voices from your ElevenLabs account:
- Pre-made voices
- Custom cloned voices
- Professional voice library

### Voice Selection Tips

**For Character Dialogues:**
- Match voice to character personality
- Consider age, accent, tone
- Test with preview before generating

**For Professional Content:**
- Use clear, professional voices
- Match formality to content
- Consider your audience

---

## 📝 Script Writing Tips

### Format Rules

✅ **DO:**
```
Peter: This is correct format.
Stewie: This works great!
Peter: Each line starts with speaker name and colon.
```

❌ **DON'T:**
```
Peter said: "This won't parse correctly"
[Peter] This format doesn't work
Peter - This neither
```

### Best Practices

1. **Keep it conversational**
   - Natural dialogue flows better
   - Short sentences work best
   - Match speaker personalities

2. **Balance speakers**
   - Both speakers should have similar amounts
   - Alternate frequently for engagement
   - Avoid long monologues

3. **Consider timing**
   - Script length determines audio length
   - Longer scripts = longer videos
   - Keep under 60 seconds for social media

---

## 🎬 What Gets Generated

### Video Components:

1. **Audio Track**
   - Speaker 1 voice (Eleven Labs)
   - Speaker 2 voice (ElevenLabs)
   - Seamlessly concatenated
   - Natural conversation flow

2. **Visual Elements**
   - Background video (your upload)
   - Auto-looped if too short
   - Cropped to 9:16 (vertical)

3. **Captions**
   - Word-by-word synchronized
   - Whisper STT transcription
   - Customizable styling
   - Follows dialogue

4. **NO Images** (in script mode)
   - DALL-E image generation disabled
   - Focus on dialogue and captions
   - Cleaner, faster generation

---

## 🔧 Technical Details

### API Endpoints

**Get Available Voices:**
```http
GET /api/voices/elevenlabs
```

**Parse Script:**
```http
POST /api/parse-script
Content-Type: multipart/form-data
script=<your_script>
```

**Preview Audio:**
```http
POST /api/preview-audio
Content-Type: multipart/form-data
script=<script>
speaker1_voice=<voice_id>
speaker2_voice=<voice_id>
```

**Generate Video:**
```http
POST /api/generate-video-script
Content-Type: multipart/form-data
video=<file>
script=<script>
speaker1_voice=<voice_id>
speaker2_voice=<voice_id>
loop_if_short=true
```

### Processing Flow

```
1. Upload video → Saved to uploads/
2. Parse script → Extract speakers & dialogue
3. Fetch voices → Get ElevenLabs voice list
4. User selects → Assign voice to each speaker
5. Preview (optional) → Generate & play audio
6. Generate → Create full video
   ├─ Generate audio per speaker
   ├─ Concatenate segments
   ├─ Process background video
   ├─ Generate captions (Whisper)
   ├─ Compose all elements
   └─ Render final video
7. Download → MP4 output (9:16)
```

---

## 📊 Comparison: Topic Mode vs Script Mode

| Feature | Topic Mode | Script Mode |
|---------|-----------|-------------|
| **Input** | Topic/question | Full dialogue script |
| **Script** | AI-generated (GPT) | You provide |
| **Speakers** | 1 narrator | 2 speakers |
| **Voice TTS** | OpenAI | ElevenLabs |
| **Voice Selection** | Fixed voices | Choose per speaker |
| **Preview Audio** | No | Yes ✓ |
| **Images** | DALL-E generated | Disabled |
| **Use Case** | Reddit stories | Character dialogues |

---

## 💡 Example Use Cases

### Entertainment
- **Character Conversations**
  - Peter & Stewie (Family Guy)
  - Rick & Morty
  - Any fictional characters

- **Comedy Sketches**
  - Two-person jokes
  - Dialogue-based humor
  - Character interactions

### Educational
- **Debates**
  - Two perspectives
  - Pro vs Con arguments
  - Historical figure conversations

- **Explanations**
  - Teacher-Student format
  - Expert-Novice dialogue
  - Q&A format

### Marketing
- **Product Demos**
  - Sales person + Customer
  - Feature explanations
  - Testimonial format

- **Brand Content**
  - Company spokesperson dialogues
  - Behind-the-scenes conversations
  - Podcast snippets to video

---

## 🐛 Troubleshooting

### "Script must have exactly 2 speakers"

**Problem:** Wrong number of speakers detected

**Solutions:**
- Check format: `SpeakerName: Text`
- Use exactly 2 different speaker names
- Remove extra speakers or unnamed dialogue

### "ELEVENLABS_API_KEY not set"

**Problem:** Missing ElevenLabs API key

**Solution:**
```bash
# Add to .env file
echo "ELEVENLABS_API_KEY=your_key_here" >> .env

# Restart server
python app.py
```

### "Failed to fetch voices"

**Problem:** Can't connect to ElevenLabs API

**Solutions:**
- Check API key is valid
- Verify internet connection
- Check ElevenLabs service status
- Ensure API key has proper permissions

### Preview audio doesn't play

**Problem:** Audio generation failed

**Solutions:**
- Check both voices are selected
- Verify script is parsed correctly
- Check browser console for errors
- Try different voices

---

## 📦 Dependencies Added

**New packages for Script Mode:**
```
pydub==0.25.1          # Audio concatenation
elevenlabs             # Already in requirements
```

**Install:**
```bash
pip install pydub
# or
pip install -r mediachain/requirements.txt
```

---

## 🔄 Switching Modes

### From Topic Mode → Script Mode
Click: **"🎭 Switch to Script Mode (Multi-Speaker) →"** (top right)

### From Script Mode → Topic Mode
Click: **"← Switch to Topic Mode (AI-Generated)"** (top right)

Both modes fully functional and independent!

---

## 🎉 Summary

**Script Mode gives you:**
- ✅ Complete control over dialogue
- ✅ Professional ElevenLabs voices
- ✅ Multi-speaker conversations
- ✅ Audio preview before generation
- ✅ Perfect for character dialogues
- ✅ Faster generation (no DALL-E)

**Perfect for:**
- Character conversations
- Educational content
- Debates & discussions
- Comedy sketches
- Brand content
- Podcast clips

**Try it now:** http://localhost:8000/script 🚀


