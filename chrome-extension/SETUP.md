# Chrome Extension Setup Instructions

## Quick Start

### 1. Reload Extension in Chrome
1. Go to `chrome://extensions/`
2. Find "ContentGen Image Selector"
3. Click the **reload** icon (🔄)

### 2. Start Flask App
```bash
cd /Users/ayushganvir/Documents/code/content_gen
python3 app.py
```

### 3. Test the Workflow

#### Step 1: Parse Script in Flask
1. Open http://localhost:8000
2. Paste your dialogue script:
   ```
   Peter: This is amazing!
   Stewie: Indeed, quite remarkable.
   ```
3. Click "Parse Script & Load Voices"
4. You'll see "🖼️ Open Extension to Select Images" button

#### Step 2: Open Extension Side Panel
1. Click the ContentGen extension icon in Chrome toolbar
2. Side panel opens on the right
3. You should see your dialogues listed

#### Step 3: Select Images
1. In the side panel, click "Select Image" for any dialogue
2. Navigate to any webpage (e.g., Google Images)
3. Click on any image you want
4. Image uploads automatically
5. Check Flask app - image appears with "✓ From Extension" badge

#### Step 4: Generate Video
1. Return to Flask app
2. All selected images are already populated
3. Assign voices
4. Click "Generate Video"

## Troubleshooting

**Extension shows "No Session Found":**
- Make sure you parsed the script in Flask first
- Refresh the side panel
- Check that Flask is running on http://localhost:8000

**Images not syncing:**
- Check browser console for errors
- Verify Flask API is responding: http://localhost:8000/api/extension/session/session_[timestamp]
- Make sure both Flask and extension are polling (every 2 seconds)

**Can't click on images:**
- Some websites block image capture due to CORS
- Try opening the image in a new tab first
- Press ESC to cancel and try again

## Features

✅ **Integrated Workflow**: Script → Flask → Extension → Images → Video
✅ **Side Panel UI**: Stays visible while browsing
✅ **Real-Time Sync**: Images appear in both UIs instantly
✅ **Consistent Design**: Purple gradient theme throughout
✅ **No Manual Export**: Everything syncs automatically

## Files Modified

- `app.py` - Added extension API endpoints
- `script_mode.html` - Added session creation and polling
- `chrome-extension/manifest.json` - Updated to side panel
- `chrome-extension/sidepanel.html` - New side panel UI
- `chrome-extension/sidepanel.js` - Session and image sync logic
- `chrome-extension/background.js` - Service worker for side panel
