// Background service worker
chrome.action.onClicked.addListener((tab) => {
    // Open side panel when extension icon is clicked
    chrome.sidePanel.open({ windowId: tab.windowId });
});

// Listen for messages from content script or side panel
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'openSidePanel') {
        chrome.sidePanel.open({ windowId: sender.tab.windowId });
    }

    // Handle area capture
    if (request.action === 'captureArea') {
        handleAreaCapture(request, sender, sendResponse);
        return true; // Keep channel open for async response
    }

    return true;
});

// Capture selected area
async function handleAreaCapture(request, sender, sendResponse) {
    try {
        console.log('[BACKGROUND] Capturing area:', request.rect);

        // Capture the visible tab
        const dataUrl = await chrome.tabs.captureVisibleTab(sender.tab.windowId, {
            format: 'png'
        });

        console.log('[BACKGROUND] Screenshot captured, cropping...');

        // Create offscreen document for canvas operations
        const croppedImage = await cropImageInOffscreen(dataUrl, request.rect, request.screenWidth, request.screenHeight);

        console.log('[BACKGROUND] Image cropped, uploading...');

        // Upload to API
        const response = await fetch('http://localhost:8000/api/extension/upload-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: request.sessionId,
                dialogue_index: request.dialogueIndex,
                image_data: croppedImage
            })
        });

        if (response.ok) {
            console.log('[BACKGROUND] Upload successful');
            sendResponse({ success: true });
        } else {
            console.error('[BACKGROUND] Upload failed:', await response.text());
            sendResponse({ success: false, error: 'Upload failed' });
        }
    } catch (error) {
        console.error('[BACKGROUND] Capture error:', error);
        sendResponse({ success: false, error: error.message });
    }
}

// Crop image using fetch and blob
async function cropImageInOffscreen(dataUrl, rect, screenWidth, screenHeight) {
    console.log('[BACKGROUND] Cropping with rect:', rect);
    console.log('[BACKGROUND] Screen dimensions:', screenWidth, 'x', screenHeight);

    // Convert data URL to blob
    const response = await fetch(dataUrl);
    const blob = await response.blob();

    // Create ImageBitmap (works in service worker)
    const imageBitmap = await createImageBitmap(blob);

    const actualWidth = imageBitmap.width;
    const actualHeight = imageBitmap.height;

    console.log('[BACKGROUND] Screenshot size:', actualWidth, 'x', actualHeight);
    console.log('[BACKGROUND] Requested rect (viewport coords):', rect);

    // captureVisibleTab captures the VIEWPORT at device pixel ratio
    // So we need to scale based on the ratio between screenshot and viewport
    // The device pixel ratio is: actualWidth / viewportWidth

    // Since rect is in CSS pixels (viewport coordinates), we need to scale by DPR
    // DPR = screenshot width / viewport width (which is same as screen width in most cases)
    // But more accurately, we should use the actual viewport dimensions

    // For now, assume viewport width ≈ screen width (works when not zoomed)
    const dpr = actualWidth / screenWidth;

    console.log('[BACKGROUND] Detected DPR:', dpr);

    // Scale the coordinates by DPR
    const scaledRect = {
        x: Math.round(rect.x * dpr),
        y: Math.round(rect.y * dpr),
        width: Math.round(rect.width * dpr),
        height: Math.round(rect.height * dpr)
    };

    console.log('[BACKGROUND] Scaled rect (device pixels):', scaledRect);

    // Ensure we don't go out of bounds
    scaledRect.x = Math.max(0, Math.min(scaledRect.x, actualWidth - scaledRect.width));
    scaledRect.y = Math.max(0, Math.min(scaledRect.y, actualHeight - scaledRect.height));
    scaledRect.width = Math.min(scaledRect.width, actualWidth - scaledRect.x);
    scaledRect.height = Math.min(scaledRect.height, actualHeight - scaledRect.y);

    console.log('[BACKGROUND] Final rect (clamped):', scaledRect);

    // Create offscreen canvas with the output size
    const canvas = new OffscreenCanvas(scaledRect.width, scaledRect.height);
    const ctx = canvas.getContext('2d');

    // Draw cropped portion
    ctx.drawImage(
        imageBitmap,
        scaledRect.x, scaledRect.y, scaledRect.width, scaledRect.height,  // source
        0, 0, scaledRect.width, scaledRect.height                          // destination
    );

    // Convert to blob then to data URL
    const croppedBlob = await canvas.convertToBlob({ type: 'image/jpeg', quality: 0.9 });

    console.log('[BACKGROUND] Cropped image size:', scaledRect.width, 'x', scaledRect.height);

    // Convert blob to data URL
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(croppedBlob);
    });
}
