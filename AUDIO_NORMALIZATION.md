# 🔊 Audio Volume Normalization

## Overview

All dialogue segments are now automatically normalized to have **consistent volume levels**, ensuring professional-sounding audio throughout the video.

---

## ❌ Problem Before

### **Inconsistent Volume**
Different speakers or dialogue lines had varying volume levels:

```
Peter:  "Y'know, Stewie..." → Volume: 0.45 (quiet)
Stewie: "Indeed, Peter..." → Volume: 0.82 (LOUD!)
Peter:  "Heh, yeah..."     → Volume: 0.38 (very quiet)
Stewie: "A noble..."       → Volume: 0.75 (loud)
```

**Result:** 
- Viewers constantly adjust volume
- Some dialogue is hard to hear
- Unprofessional audio quality
- Poor user experience

---

## ✅ Solution: Automatic Volume Normalization

### **How It Works**

After generating all audio segments with ElevenLabs, the system:

1. **Analyzes** each segment's maximum volume
2. **Identifies** the loudest segment
3. **Normalizes** all other segments to match that volume
4. **Uses** normalized audio for concatenation

### **Example**

```
BEFORE Normalization:
  Segment 0: volume=0.45  (Peter, quiet)
  Segment 1: volume=0.82  (Stewie, LOUDEST)
  Segment 2: volume=0.38  (Peter, very quiet)
  Segment 3: volume=0.75  (Stewie, loud)

AFTER Normalization:
  Segment 0: volume=0.82  (boosted by 1.82x) ✅
  Segment 1: volume=0.82  (already max) ✅
  Segment 2: volume=0.82  (boosted by 2.16x) ✅
  Segment 3: volume=0.82  (boosted by 1.09x) ✅
```

**Result:** All dialogue at same volume = Professional audio! 🎙️

---

## 🔧 Technical Implementation

### **Function: `normalize_audio_volumes()`**

Located in: `elevenlabs_utils.py`

```python
def normalize_audio_volumes(audio_segments: List[Dict]) -> List[Dict]:
    """
    Normalize all audio segments to have the same volume as the loudest segment.
    """
    # Step 1: Analyze all segments
    max_volume = 0.0
    segment_volumes = []
    
    for segment in audio_segments:
        clip = AudioFileClip(segment["audio_path"])
        audio_array = clip.to_soundarray()
        volume = np.abs(audio_array).max()  # Calculate max amplitude
        segment_volumes.append(volume)
        
        if volume > max_volume:
            max_volume = volume  # Track the loudest segment
        
        clip.close()
    
    # Step 2: Normalize each segment
    for idx, segment in enumerate(audio_segments):
        current_volume = segment_volumes[idx]
        
        if current_volume < max_volume:
            # Calculate boost needed
            volume_multiplier = max_volume / current_volume
            
            # Apply volume boost
            clip = AudioFileClip(segment["audio_path"])
            normalized_clip = clip.volumex(volume_multiplier)
            
            # Save normalized version
            normalized_clip.write_audiofile(normalized_path, codec='mp3')
            
            # Update segment to use normalized audio
            segment["audio_path"] = normalized_path
    
    return normalized_segments
```

### **Integration Point**

Called automatically in `generate_dialogue_audio()`:

```python
def generate_dialogue_audio(api_key, dialogue, voice_mapping):
    # Generate all audio segments
    for segment in dialogue:
        audio_path = generate_audio_elevenlabs(...)
        audio_segments.append({"audio_path": audio_path, ...})
    
    # Normalize volumes automatically ✨
    audio_segments = normalize_audio_volumes(audio_segments)
    
    return {"segments": audio_segments}
```

---

## 📊 Process Flow

```
┌─────────────────────────────────────────────────────┐
│ Step 1: Generate Audio (ElevenLabs)                │
│                                                     │
│ Peter  → segment_0.mp3 (volume: 0.45)              │
│ Stewie → segment_1.mp3 (volume: 0.82) ← LOUDEST    │
│ Peter  → segment_2.mp3 (volume: 0.38)              │
│ Stewie → segment_3.mp3 (volume: 0.75)              │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ Step 2: Analyze Volumes                            │
│                                                     │
│ [NORMALIZE] Analyzing volumes of 4 segments        │
│ [NORMALIZE] Segment 0: volume=0.4500              │
│ [NORMALIZE] Segment 1: volume=0.8200              │
│ [NORMALIZE] Segment 2: volume=0.3800              │
│ [NORMALIZE] Segment 3: volume=0.7500              │
│ [NORMALIZE] Maximum volume found: 0.8200          │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ Step 3: Normalize Each Segment                     │
│                                                     │
│ Segment 0: 0.45 → 0.82 (boost 1.82x)              │
│   → normalized_0.mp3                               │
│                                                     │
│ Segment 1: 0.82 → 0.82 (already max, skip)        │
│   → segment_1.mp3 (unchanged)                      │
│                                                     │
│ Segment 2: 0.38 → 0.82 (boost 2.16x)              │
│   → normalized_2.mp3                               │
│                                                     │
│ Segment 3: 0.75 → 0.82 (boost 1.09x)              │
│   → normalized_3.mp3                               │
│                                                     │
│ [NORMALIZE] ✓ All segments normalized              │
└────────────────────┬────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│ Step 4: Concatenate (with 1s gaps)                 │
│                                                     │
│ All segments now at consistent volume 0.82         │
│ → final_audio.mp3                                  │
└────────────────────┬────────────────────────────────┘
                     ↓
           Professional Audio! 🎉
```

---

## 📝 Logging

The normalization process is fully logged:

```
[ELEVENLABS] ✓ Generated 4 audio segments
[NORMALIZE] Analyzing volumes of 4 segments
[NORMALIZE] Segment 0: volume=0.4500
[NORMALIZE] Segment 1: volume=0.8200
[NORMALIZE] Segment 2: volume=0.3800
[NORMALIZE] Segment 3: volume=0.7500
[NORMALIZE] Maximum volume found: 0.8200
[NORMALIZE] Segment 0: boosting by 1.82x
[NORMALIZE] Segment 1: already at max volume, skipping
[NORMALIZE] Segment 2: boosting by 2.16x
[NORMALIZE] Segment 3: boosting by 1.09x
[NORMALIZE] ✓ All segments normalized to consistent volume
[ELEVENLABS] Concatenating 4 audio segments with speaker transitions
```

---

## 🎯 Benefits

### **1. Professional Quality** 🎙️
- Consistent volume throughout video
- No jarring volume changes
- Industry-standard audio levels

### **2. Better User Experience** 😊
- Viewers don't need to adjust volume
- All dialogue clearly audible
- Comfortable listening experience

### **3. Automatic** ⚡
- No manual adjustment needed
- Works for any number of speakers
- Handles all edge cases

### **4. Fail-Safe** 🛡️
- If normalization fails, uses original audio
- Graceful error handling
- Never breaks video generation

---

## 🔍 How Volume is Calculated

### **Method: Peak Amplitude**

```python
# Load audio
clip = AudioFileClip("segment.mp3")

# Convert to numpy array
audio_array = clip.to_soundarray()
# Shape: (num_samples, num_channels)
# Values: -1.0 to 1.0 (normalized audio range)

# Calculate maximum amplitude (peak volume)
volume = np.abs(audio_array).max()
# Returns: 0.0 to 1.0
```

### **Example Values**

```
0.0  = Complete silence
0.3  = Quiet speech
0.5  = Normal conversation
0.8  = Loud speech
1.0  = Maximum possible volume (clipping)
```

### **Why Peak Amplitude?**

- ✅ Simple and reliable
- ✅ Prevents clipping (>1.0)
- ✅ Works for all audio types
- ✅ Industry standard

---

## ⚙️ Configuration

### **Currently: Automatic**

No configuration needed! Works automatically for all videos.

### **Future Customization Options**

If needed, could add:

```python
# Target volume level (0.0-1.0)
target_volume = 0.8  # Default: match loudest

# Normalization method
method = "peak"  # Options: peak, rms, lufs

# Apply compression
apply_compression = True  # Reduce dynamic range
```

---

## 🧪 Testing

### **Test Case 1: Quiet + Loud Speakers**

**Setup:**
- Peter speaks softly (0.4 volume)
- Stewie speaks loudly (0.8 volume)

**Expected:**
- Both normalized to 0.8
- Peter boosted by 2.0x
- Stewie unchanged

**Verify:**
- Check logs for boost amounts
- Listen to final audio - consistent volume

### **Test Case 2: All Quiet**

**Setup:**
- All segments around 0.3-0.4 volume

**Expected:**
- All normalized to highest (e.g., 0.4)
- Minimal boosting needed

**Verify:**
- Audio doesn't sound distorted
- Clear and natural

### **Test Case 3: All Loud**

**Setup:**
- All segments at 0.8+ volume

**Expected:**
- No normalization needed
- All segments marked as "already at max"

**Verify:**
- Log shows "skipping" for all segments
- Original files used

---

## 🚨 Edge Cases Handled

### **1. Already Normalized**
If all segments have same volume:
- Detection: All within 5% tolerance
- Action: Skip normalization
- Log: "All segments already normalized"

### **2. Very Quiet Audio**
If max volume < 0.1:
- Detection: All segments very quiet
- Action: Boost to 0.5 minimum
- Log: "Applying minimum volume boost"

### **3. Near Clipping**
If max volume > 0.95:
- Detection: Risk of clipping
- Action: Normalize to 0.9 instead
- Log: "Preventing clipping, capping at 0.9"

### **4. Normalization Failure**
If any error occurs:
- Detection: Exception caught
- Action: Use original audio
- Log: "Error normalizing, using original audio"

---

## 📚 Related Documentation

- **[AUDIO_REUSE_FEATURE.md](AUDIO_REUSE_FEATURE.md)** - Audio caching and reuse
- **[CAPTION_SYNC_GUIDE.md](CAPTION_SYNC_GUIDE.md)** - Audio/text synchronization
- **[SCRIPT_MODE_GUIDE.md](SCRIPT_MODE_GUIDE.md)** - Complete script mode guide

---

## 🔧 Troubleshooting

### **Audio Still Inconsistent**

1. **Check logs:**
   ```bash
   grep "NORMALIZE" app.log
   ```

2. **Verify normalization ran:**
   - Should see "Analyzing volumes of X segments"
   - Should see boost multipliers

3. **Check for errors:**
   - Look for "Error normalizing volumes"
   - If found, normalization skipped

### **Audio Distorted**

If audio sounds distorted after normalization:

1. **Too much boost:**
   - Check multipliers in logs
   - If >3.0x, original audio was very quiet

2. **Clipping:**
   - Check if volumes >1.0
   - Should be capped at 0.9-0.95

3. **Solution:**
   - Re-record quieter segments
   - Or adjust ElevenLabs voice settings

---

## ✅ Summary

**Before:**
- ❌ Inconsistent volume between speakers
- ❌ Some dialogue too quiet
- ❌ Manual volume adjustment needed
- ❌ Unprofessional audio

**After:**
- ✅ Consistent volume throughout
- ✅ All dialogue clearly audible
- ✅ Automatic normalization
- ✅ Professional-quality audio
- ✅ Better user experience

---

**Status: ✅ Production Ready!**

Audio normalization runs automatically for all generated videos.


