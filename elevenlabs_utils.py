"""
ElevenLabs Utilities
Functions for interacting with ElevenLabs API
"""
import os
import logging
from elevenlabs import ElevenLabs
from typing import List, Dict

logger = logging.getLogger(__name__)


def get_available_voices(api_key: str) -> List[Dict]:
    """
    Get all available voices from ElevenLabs.
    
    Args:
        api_key: ElevenLabs API key
        
    Returns:
        List of voice dictionaries with 'voice_id' and 'name'
    """
    try:
        client = ElevenLabs(api_key=api_key)
        voices_response = client.voices.get_all()
        
        voices = []
        for voice in voices_response.voices:
            voices.append({
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": getattr(voice, 'category', 'unknown'),
                "labels": getattr(voice, 'labels', {})
            })
        
        logger.info(f"[ELEVENLABS] Retrieved {len(voices)} voices")
        return voices
        
    except Exception as e:
        logger.error(f"[ELEVENLABS] Error fetching voices: {e}")
        return []


def generate_audio_elevenlabs(api_key: str, text: str, voice_id: str, output_path: str = None) -> str:
    """
    Generate audio using ElevenLabs TTS.
    
    Args:
        api_key: ElevenLabs API key
        text: Text to convert to speech
        voice_id: Voice ID to use
        output_path: Optional output path (auto-generated if not provided)
        
    Returns:
        Path to generated audio file
    """
    try:
        import uuid
        from pathlib import Path
        
        client = ElevenLabs(api_key=api_key)
        
        # Generate audio
        logger.info(f"[ELEVENLABS] Generating audio with voice {voice_id}")
        logger.info(f"[ELEVENLABS] Text length: {len(text)} characters")
        
        audio_generator = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_monolingual_v1"
        )
        
        # Save audio
        if not output_path:
            temp_dir = Path("/tmp/elevenlabs_audio")
            temp_dir.mkdir(exist_ok=True)
            output_path = str(temp_dir / f"audio_{uuid.uuid4()}.mp3")
        
        # Write audio to file
        with open(output_path, 'wb') as f:
            for chunk in audio_generator:
                f.write(chunk)
        
        logger.info(f"[ELEVENLABS] ✓ Audio generated: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"[ELEVENLABS] ✗ Error generating audio: {e}", exc_info=True)
        return None


def normalize_audio_volumes(audio_segments: List[Dict]) -> List[Dict]:
    """
    Normalize all audio segments to have the same volume as the loudest segment.
    
    Args:
        audio_segments: List of dicts with 'audio_path' keys
        
    Returns:
        Updated audio_segments with normalized audio paths
    """
    try:
        from moviepy.editor import AudioFileClip
        import numpy as np
        import uuid
        from pathlib import Path
        
        logger.info(f"[NORMALIZE] Analyzing volumes of {len(audio_segments)} segments")
        
        # Step 1: Find the maximum volume across all segments
        max_volume = 0.0
        segment_volumes = []
        
        for segment in audio_segments:
            audio_path = segment["audio_path"]
            clip = AudioFileClip(audio_path)
            
            # Get the audio array and calculate max amplitude
            audio_array = clip.to_soundarray()
            volume = np.abs(audio_array).max()
            segment_volumes.append(volume)
            
            if volume > max_volume:
                max_volume = volume
            
            clip.close()
            
            logger.info(f"[NORMALIZE] Segment {segment['index']}: volume={volume:.4f}")
        
        logger.info(f"[NORMALIZE] Maximum volume found: {max_volume:.4f}")
        
        # Step 2: Normalize each segment to match the max volume
        temp_dir = Path("/tmp/elevenlabs_audio")
        normalized_segments = []
        
        for idx, segment in enumerate(audio_segments):
            audio_path = segment["audio_path"]
            current_volume = segment_volumes[idx]
            
            # Calculate volume multiplier
            if current_volume > 0 and current_volume < max_volume:
                volume_multiplier = max_volume / current_volume
                logger.info(f"[NORMALIZE] Segment {idx}: boosting by {volume_multiplier:.2f}x")
                
                # Load audio and adjust volume
                clip = AudioFileClip(audio_path)
                normalized_clip = clip.volumex(volume_multiplier)
                
                # Save normalized audio
                normalized_path = str(temp_dir / f"normalized_{idx}_{uuid.uuid4()}.mp3")
                normalized_clip.write_audiofile(normalized_path, codec='mp3', logger=None)
                
                clip.close()
                normalized_clip.close()
                
                # Update segment with normalized path
                segment["audio_path"] = normalized_path
                segment["original_path"] = audio_path
                segment["volume_multiplier"] = volume_multiplier
            else:
                logger.info(f"[NORMALIZE] Segment {idx}: already at max volume, skipping")
                segment["volume_multiplier"] = 1.0
            
            normalized_segments.append(segment)
        
        logger.info(f"[NORMALIZE] ✓ All segments normalized to consistent volume")
        return normalized_segments
        
    except Exception as e:
        logger.error(f"[NORMALIZE] ✗ Error normalizing volumes: {e}", exc_info=True)
        # Return original segments if normalization fails
        return audio_segments


def generate_dialogue_audio(api_key: str, dialogue: List[Dict], voice_mapping: Dict[str, str]) -> Dict:
    """
    Generate audio for each dialogue segment.
    Audio volumes are automatically normalized to be consistent.
    
    Args:
        api_key: ElevenLabs API key
        dialogue: List of {"speaker": "Name", "text": "..."}
        voice_mapping: {"Speaker1": "voice_id_1", "Speaker2": "voice_id_2"}
        
    Returns:
        Dictionary with audio paths and metadata
    """
    try:
        import uuid
        from pathlib import Path
        
        temp_dir = Path("/tmp/elevenlabs_audio")
        temp_dir.mkdir(exist_ok=True)
        
        audio_segments = []
        
        for idx, segment in enumerate(dialogue):
            speaker = segment["speaker"]
            text = segment["text"]
            voice_id = voice_mapping.get(speaker)
            
            if not voice_id:
                logger.error(f"[ELEVENLABS] No voice mapped for speaker: {speaker}")
                continue
            
            logger.info(f"[ELEVENLABS] Generating segment {idx+1}/{len(dialogue)} - {speaker}")
            
            output_path = str(temp_dir / f"segment_{idx}_{uuid.uuid4()}.mp3")
            audio_path = generate_audio_elevenlabs(api_key, text, voice_id, output_path)
            
            if audio_path:
                audio_segments.append({
                    "speaker": speaker,
                    "text": text,
                    "audio_path": audio_path,
                    "index": idx
                })
        
        logger.info(f"[ELEVENLABS] ✓ Generated {len(audio_segments)} audio segments")
        
        # Normalize audio volumes to match the loudest segment
        if len(audio_segments) > 0:
            audio_segments = normalize_audio_volumes(audio_segments)
        
        return {
            "segments": audio_segments,
            "count": len(audio_segments)
        }
        
    except Exception as e:
        logger.error(f"[ELEVENLABS] ✗ Error generating dialogue audio: {e}", exc_info=True)
        return {"segments": [], "count": 0}


def concatenate_audio_segments(audio_segments: List[dict], output_path: str) -> str:
    """
    Concatenate multiple audio files into one using MoviePy.
    Adds 1-second gap when speaker changes.
    
    Args:
        audio_segments: List of segment dicts with 'audio_path' and 'speaker' keys
        output_path: Output path for concatenated audio
        
    Returns:
        Path to concatenated audio file
    """
    try:
        from moviepy.editor import AudioFileClip, concatenate_audioclips, AudioClip
        import numpy as np
        
        logger.info(f"[ELEVENLABS] Concatenating {len(audio_segments)} audio segments with speaker transitions")
        
        # Load all audio clips and add gaps between speaker changes
        audio_clips = []
        previous_speaker = None
        
        for i, segment in enumerate(audio_segments):
            path = segment["audio_path"]
            speaker = segment["speaker"]
            
            # Add 1-second silence when speaker changes (but not at the very start)
            if previous_speaker is not None and speaker != previous_speaker:
                logger.info(f"[ELEVENLABS] Adding 1s gap: {previous_speaker} → {speaker}")
                
                # Create 1-second silent audio clip
                def make_frame(t):
                    return np.array([0, 0])  # Stereo silence
                
                silence = AudioClip(make_frame, duration=1.0, fps=44100)
                audio_clips.append(silence)
            
            # Load the actual audio segment
            logger.info(f"[ELEVENLABS] Loading segment {i+1}/{len(audio_segments)}: {speaker}")
            clip = AudioFileClip(path)
            audio_clips.append(clip)
            
            previous_speaker = speaker
        
        # Concatenate all clips (audio + silence gaps)
        logger.info(f"[ELEVENLABS] Combining {len(audio_clips)} audio clips (including gaps)")
        combined = concatenate_audioclips(audio_clips)
        
        # Write to output file
        logger.info(f"[ELEVENLABS] Writing concatenated audio to: {output_path}")
        combined.write_audiofile(output_path, codec='mp3', logger=None)
        
        # Clean up
        for clip in audio_clips:
            clip.close()
        combined.close()
        
        logger.info(f"[ELEVENLABS] ✓ Audio concatenated: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"[ELEVENLABS] ✗ Error concatenating audio: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # Test voice retrieval
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if api_key:
        voices = get_available_voices(api_key)
        print(f"Found {len(voices)} voices:")
        for v in voices[:5]:  # Show first 5
            print(f"  - {v['name']} ({v['voice_id']})")

