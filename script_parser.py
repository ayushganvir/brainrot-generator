"""
Script Parser for Multi-Speaker Dialogue
Parses scripts in format:
Speaker: Text
"""
import re
from typing import List, Dict, Tuple

def parse_dialogue_script(script: str) -> Tuple[List[Dict], List[str]]:
    """
    Parse a dialogue script with speakers.
    
    Format:
        Speaker1: Text here
        Speaker2: More text
    
    Args:
        script: The raw script text
        
    Returns:
        Tuple of (dialogue_list, unique_speakers)
        - dialogue_list: List of {"speaker": "Name", "text": "..."}
        - unique_speakers: List of unique speaker names
    """
    lines = script.strip().split('\n')
    dialogue = []
    speakers = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match pattern "Speaker: Text"
        match = re.match(r'^([^:]+):\s*(.+)$', line)
        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()
            
            dialogue.append({
                "speaker": speaker,
                "text": text
            })
            speakers.add(speaker)
    
    return dialogue, sorted(list(speakers))


def validate_two_speakers(speakers: List[str]) -> bool:
    """Validate that there are 1 or 2 speakers."""
    return 1 <= len(speakers) <= 2


def combine_dialogue_for_speaker(dialogue: List[Dict], speaker: str) -> str:
    """Get all text for a specific speaker combined."""
    return " ".join([d["text"] for d in dialogue if d["speaker"] == speaker])


def get_full_script_text(dialogue: List[Dict]) -> str:
    """Get the full script as continuous text."""
    return " ".join([d["text"] for d in dialogue])


if __name__ == "__main__":
    # Test the parser
    test_script = """
Peter: Y'know, Stewie, OpenAI is kinda like having a genius buddy who never sleeps.
Stewie: Indeed, Peter. OpenAI represents a monumental leap in computational reasoning.
Peter: Heh, yeah, and it even helps me write emails so Lois stops yelling at me.
Stewie: A noble application of advanced AI—preventing maternal outrage.
    """
    
    dialogue, speakers = parse_dialogue_script(test_script)
    print(f"Speakers: {speakers}")
    print(f"Dialogue segments: {len(dialogue)}")
    for d in dialogue:
        print(f"  {d['speaker']}: {d['text'][:50]}...")


