# MoviePy Engine - Reddit Stories

This directory contains the core video generation engine for Reddit story videos.

## 🚨 Important: Run from Project Root

**The web interface and server have been moved to the project root.**

To use this application:

1. Navigate to the project root:
   ```bash
   cd /path/to/content_gen
   ```

2. Follow the instructions in the root [README.md](../../../README.md)

3. Or see [QUICKSTART.md](../../../QUICKSTART.md) for quick setup

## 📁 What's Here

This directory contains:

- **`reddit_stories/`** - Core video generation logic
  - `generate_reddit_story.py` - Main RedditStoryGenerator class
  
- **`src/`** - Video editing utilities
  - `video_editor.py` - Video manipulation (crop, cut, render)
  - `captions/` - Caption generation and styling
  - `json_2_video_engine/` - JSON-based video templating

- **`main_moviepy.py`** - Example script (legacy, use web interface instead)

## 🔧 For Developers

If you want to use the `RedditStoryGenerator` class programmatically:

```python
import os
import asyncio
from mediachain.examples.moviepy_engine.reddit_stories.generate_reddit_story import RedditStoryGenerator

async def main():
    generator = RedditStoryGenerator(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    result = await generator.generate_video(
        video_path_or_url='video_path',
        video_path='/path/to/your/video.mp4',
        video_topic='Your story topic here',
        add_images=True,
        captions_settings={
            'color': 'white',
            'shadow_color': 'black'
        }
    )
    
    print(f"Video generated: {result['output_path']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📖 Documentation

See the root-level documentation for full details:
- [Main README](../../../README.md) - Full documentation
- [Quick Start Guide](../../../QUICKSTART.md) - Get started fast
- [Web Interface](../../../app.py) - FastAPI server

## ⚡ Quick Setup

From the project root:

```bash
# Install dependencies
pip install -r mediachain/requirements.txt

# Set API key
export OPENAI_API_KEY=sk-your-key

# Run the server
python app.py

# Open browser
open http://localhost:8000
```

---

**Note:** This is a library component. Use the web interface at the project root for the best experience!

