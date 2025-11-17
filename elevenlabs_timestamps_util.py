"""
OPTIONAL: ElevenLabs Timestamp-based Caption Generation

This is a reference implementation showing how to use ElevenLabs' 
convert_with_timestamps API for caption synchronization.

⚠️ NOT CURRENTLY USED - Whisper STT is simpler and more accurate!

This file is provided as a reference for future implementation if needed.
"""

import logging
from typing import List, Dict, Tuple
from elevenlabs import ElevenLabs

logger = logging.getLogger(__name__)


def generate_audio_with_timestamps(
    api_key: str, 
    text: str, 
    voice_id: str
) -> Dict:
    """
    Generate audio with character-level timestamps from ElevenLabs.
    
    Args:
        api_key: ElevenLabs API key
        text: Text to convert to speech
        voice_id: Voice ID to use
        
    Returns:
        Dictionary with audio data and alignment info
    """
    try:
        client = ElevenLabs(api_key=api_key)
        
        response = client.text_to_speech.convert_with_timestamps(
            voice_id=voice_id,
            text=text
        )
        
        return {
            "audio_base64": response['audio_base64'],
            "alignment": response['alignment']
        }
        
    except Exception as e:
        logger.error(f"Error generating audio with timestamps: {e}")
        return None


def character_to_word_timestamps(
    characters: List[str],
    start_times: List[float],
    end_times: List[float],
    text: str
) -> List[Dict]:
    """
    Convert character-level timestamps to word-level.
    
    Args:
        characters: List of characters
        start_times: Start time for each character
        end_times: End time for each character
        text: Original text
        
    Returns:
        List of word dictionaries with start/end times
    """
    words = []
    current_word = ""
    word_start = None
    word_end = None
    
    for i, char in enumerate(characters):
        if char.strip():  # Non-whitespace
            if word_start is None:
                word_start = start_times[i]
            current_word += char
            word_end = end_times[i]
        else:  # Whitespace - end of word
            if current_word:
                words.append({
                    "word": current_word,
                    "start": word_start,
                    "end": word_end
                })
                current_word = ""
                word_start = None
    
    # Add last word if exists
    if current_word:
        words.append({
            "word": current_word,
            "start": word_start,
            "end": word_end
        })
    
    return words


def generate_dialogue_with_timestamps(
    api_key: str,
    dialogue_segments: List[Dict],
    voice_mapping: Dict[str, str]
) -> List[Dict]:
    """
    Generate audio for dialogue and calculate cumulative timestamps.
    
    This handles:
    - Multiple speakers
    - 1-second gaps between speaker changes
    - Cumulative timing offsets
    
    Args:
        api_key: ElevenLabs API key
        dialogue_segments: List of {speaker, text} dicts
        voice_mapping: Map of speaker -> voice_id
        
    Returns:
        List of segments with audio and adjusted timestamps
    """
    result_segments = []
    cumulative_time = 0.0
    previous_speaker = None
    
    for i, segment in enumerate(dialogue_segments):
        speaker = segment["speaker"]
        text = segment["text"]
        voice_id = voice_mapping.get(speaker)
        
        if not voice_id:
            logger.error(f"No voice mapping for speaker: {speaker}")
            continue
        
        # Add 1-second gap when speaker changes
        if previous_speaker is not None and speaker != previous_speaker:
            logger.info(f"Adding 1s gap: {previous_speaker} → {speaker}")
            cumulative_time += 1.0
        
        # Generate audio with timestamps
        logger.info(f"Generating segment {i+1}: {speaker}")
        audio_data = generate_audio_with_timestamps(api_key, text, voice_id)
        
        if not audio_data:
            logger.error(f"Failed to generate audio for segment {i+1}")
            continue
        
        alignment = audio_data["alignment"]
        
        # Convert character-level to word-level timestamps
        words = character_to_word_timestamps(
            alignment["characters"],
            alignment["character_start_times_seconds"],
            alignment["character_end_times_seconds"],
            text
        )
        
        # Adjust timestamps by cumulative offset
        adjusted_words = []
        for word in words:
            adjusted_words.append({
                "word": word["word"],
                "start": word["start"] + cumulative_time,
                "end": word["end"] + cumulative_time
            })
        
        # Calculate segment duration
        segment_duration = alignment["character_end_times_seconds"][-1]
        
        result_segments.append({
            "speaker": speaker,
            "text": text,
            "audio_base64": audio_data["audio_base64"],
            "words": adjusted_words,
            "duration": segment_duration,
            "start_time": cumulative_time,
            "end_time": cumulative_time + segment_duration
        })
        
        # Update cumulative time
        cumulative_time += segment_duration
        previous_speaker = speaker
    
    return result_segments


def create_srt_from_timestamps(word_data: List[Dict], output_path: str) -> str:
    """
    Create an SRT subtitle file from word timestamp data.
    
    Args:
        word_data: List of {word, start, end} dicts
        output_path: Path to save SRT file
        
    Returns:
        Path to SRT file
    """
    try:
        with open(output_path, 'w') as f:
            for i, word_info in enumerate(word_data, start=1):
                start = format_srt_time(word_info["start"])
                end = format_srt_time(word_info["end"])
                word = word_info["word"]
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{word}\n\n")
        
        logger.info(f"Created SRT file: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating SRT file: {e}")
        return None


def format_srt_time(seconds: float) -> str:
    """
    Format seconds to SRT timestamp format: HH:MM:SS,mmm
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# Example usage
if __name__ == "__main__":
    import os
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    # Example dialogue
    dialogue = [
        {"speaker": "Peter", "text": "Y'know, Stewie, OpenAI is kinda like having a genius buddy."},
        {"speaker": "Stewie", "text": "Indeed, Peter. OpenAI represents a monumental leap."},
        {"speaker": "Peter", "text": "Heh, yeah, and it even helps me write emails."},
        {"speaker": "Stewie", "text": "A noble application of advanced AI."}
    ]
    
    voice_mapping = {
        "Peter": "voice_id_1",
        "Stewie": "voice_id_2"
    }
    
    # Generate with timestamps
    segments = generate_dialogue_with_timestamps(api_key, dialogue, voice_mapping)
    
    # Extract all words across all segments
    all_words = []
    for segment in segments:
        all_words.extend(segment["words"])
    
    # Create SRT file
    create_srt_from_timestamps(all_words, "/tmp/captions.srt")
    
    # Print summary
    print(f"\nGenerated {len(segments)} segments")
    print(f"Total words: {len(all_words)}")
    print(f"Total duration: {segments[-1]['end_time']:.2f}s")
    
    # Print first few words
    print("\nFirst 10 words with timestamps:")
    for word in all_words[:10]:
        print(f"  {word['start']:.2f}s - {word['end']:.2f}s: {word['word']}")


