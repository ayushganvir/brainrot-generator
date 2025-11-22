# ContentGen Image Selector - Chrome Extension

A Chrome extension that allows you to select images from any webpage and associate them with dialogue lines in your video script.

## Features

- 📝 Paste your dialogue script directly in the extension
- 🖼️ Click on any image from any webpage to select it
- 🎬 Associate images with specific dialogue lines
- 📤 Export data to integrate with ContentGen app

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder from your ContentGen directory
5. The extension icon should appear in your toolbar

## Usage

### Step 1: Paste Your Script
1. Click the ContentGen extension icon in your toolbar
2. Paste your dialogue script in the format:
   ```
   Peter: This is amazing!
   Stewie: Indeed, quite remarkable.
   ```
3. Click "Parse Script"

### Step 2: Select Images
1. For each dialogue line, click "Select Image"
2. The extension will activate selection mode on the current page
3. Click on any image you want to associate with that dialogue
4. The image will be captured and saved
5. Repeat for all dialogue lines

### Step 3: Export Data
1. Once all images are selected, click "Export to ContentGen"
2. The data will be copied to your clipboard
3. Go to your ContentGen web app (http://localhost:8000)
4. Paste the data in the designated import field

## Tips

- You can browse different websites while selecting images
- Press ESC to cancel image selection mode
- The extension saves your progress automatically
- Use "Reset" to start over with a new script

## Keyboard Shortcuts

- **ESC** - Cancel image selection mode

## Troubleshooting

**Extension not appearing?**
- Make sure Developer mode is enabled in chrome://extensions/
- Try reloading the extension

**Can't select images?**
- Some websites may block image capture due to CORS policies
- Try right-clicking and "Open image in new tab" first

**Images not exporting?**
- Make sure you've selected images for all dialogue lines
- Check your clipboard permissions

## Integration with ContentGen

The exported JSON contains:
- `dialogue`: Array of speaker/text pairs
- `images`: Object mapping dialogue index to base64 image data
- `timestamp`: When the data was exported

This data can be imported into the ContentGen web app for video generation.
