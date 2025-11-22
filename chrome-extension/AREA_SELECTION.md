# Chrome Extension - Area Selection Update

## What Changed

The extension now uses **area selection** instead of clicking on images!

### New Behavior:
1. Click "Select Image" for a dialogue
2. **Drag a rectangle** over any part of the screen
3. Release to capture that area
4. Screenshot is automatically cropped and uploaded

### Features:
- ✅ Drag to select any screen area
- ✅ Visual selection box with purple border
- ✅ Dark overlay shows selected region
- ✅ Minimum 50x50px area required
- ✅ Press ESC to cancel
- ✅ Auto-crops and uploads to Flask

### How to Use:
1. **Reload the extension** in Chrome (`chrome://extensions/` → reload)
2. Open extension side panel
3. Click "Select Image" for any dialogue
4. **Drag across the screen** to select an area
5. Release mouse to capture
6. Screenshot uploads automatically!

### Technical Details:
- Uses Chrome's `captureVisibleTab` API
- Crops image to exact selected coordinates
- Accounts for device pixel ratio (retina displays)
- Converts to JPEG at 90% quality
- Uploads as base64 to Flask API

This is much more flexible than clicking on images - you can now capture:
- Parts of images
- Text + images combined
- UI elements
- Anything visible on screen!
