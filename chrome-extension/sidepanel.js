// Side panel JavaScript
const API_BASE = 'http://localhost:8000';
let currentSession = null;
let dialogueData = [];
let selectedImages = {};

// Elements
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const dialogueContainer = document.getElementById('dialogueContainer');
const dialogueList = document.getElementById('dialogueList');
const statusBox = document.getElementById('statusBox');
const statusText = document.getElementById('statusText');

// Initialize
async function init() {
    console.log('[SIDEPANEL] Initializing...');

    try {
        // First check Chrome storage
        let result = await chrome.storage.local.get(['sessionId']);
        console.log('[SIDEPANEL] Chrome storage sessionId:', result.sessionId);

        if (!result.sessionId) {
            // Try to get from localhost:8000 page
            console.log('[SIDEPANEL] No session in storage, checking localhost:8000...');
            const tabs = await chrome.tabs.query({ url: 'http://localhost:8000/*' });
            console.log('[SIDEPANEL] Found tabs:', tabs.length);

            if (tabs.length > 0) {
                const tab = tabs[0];
                console.log('[SIDEPANEL] Executing script on tab:', tab.id);

                // Try to get sessionId from the page
                const response = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: () => {
                        console.log('[PAGE] Checking for sessionId...');
                        console.log('[PAGE] window.sessionId:', window.sessionId);
                        console.log('[PAGE] localStorage.sessionId:', localStorage.getItem('sessionId'));
                        // Try multiple sources
                        return window.sessionId || localStorage.getItem('sessionId');
                    }
                });

                console.log('[SIDEPANEL] Script response:', response);

                if (response && response[0] && response[0].result) {
                    const sessionId = response[0].result;
                    console.log('[SIDEPANEL] Found sessionId:', sessionId);
                    await chrome.storage.local.set({ sessionId });
                    await loadSession(sessionId);
                    return;
                } else {
                    console.log('[SIDEPANEL] No sessionId found in page');
                }
            } else {
                console.log('[SIDEPANEL] No localhost:8000 tabs open');
            }
        } else {
            console.log('[SIDEPANEL] Loading session from storage:', result.sessionId);
            await loadSession(result.sessionId);
            return;
        }

        console.log('[SIDEPANEL] Showing empty state');
        showEmptyState();
    } catch (error) {
        console.error('[SIDEPANEL] Init error:', error);
        showEmptyState();
    }
}

// Listen for session updates from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[SIDEPANEL] Received message:', request);
    if (request.action === 'sessionCreated' && request.sessionId) {
        console.log('[SIDEPANEL] Session created via message:', request.sessionId);
        chrome.storage.local.set({ sessionId: request.sessionId });
        loadSession(request.sessionId);
    }
});

// Load session from API
async function loadSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE}/api/extension/session/${sessionId}`);

        if (!response.ok) {
            throw new Error('Session not found');
        }

        const data = await response.json();
        currentSession = sessionId;
        dialogueData = data.dialogue;
        selectedImages = data.images || {};

        showDialogueList();
        showStatus('Session loaded successfully!', 'success');

        // Poll for updates every 2 seconds
        startPolling();
    } catch (error) {
        console.error('Load session error:', error);
        showEmptyState();
    }
}

// Show dialogue list
function showDialogueList() {
    loadingState.style.display = 'none';
    emptyState.style.display = 'none';
    dialogueContainer.style.display = 'block';

    renderDialogueList();
}

// Render dialogue list
function renderDialogueList() {
    dialogueList.innerHTML = '';

    dialogueData.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'dialogue-item';

        const header = document.createElement('div');
        header.className = 'dialogue-header';

        const speaker = document.createElement('div');
        speaker.className = 'dialogue-speaker';
        speaker.textContent = item.speaker;

        const indexLabel = document.createElement('div');
        indexLabel.className = 'dialogue-index';
        indexLabel.textContent = `#${index + 1}`;

        header.appendChild(speaker);
        header.appendChild(indexLabel);
        div.appendChild(header);

        const text = document.createElement('div');
        text.className = 'dialogue-text';
        text.textContent = item.text;
        div.appendChild(text);

        // Show image if selected
        if (selectedImages[index]) {
            const img = document.createElement('img');
            img.className = 'image-preview';
            img.src = selectedImages[index];
            div.appendChild(img);
        }

        // Buttons
        const btnGroup = document.createElement('div');
        btnGroup.className = 'btn-group';

        const selectBtn = document.createElement('button');
        selectBtn.className = 'btn btn-small';
        selectBtn.textContent = selectedImages[index] ? '✓ Change Image' : 'Select Image';
        selectBtn.addEventListener('click', () => selectImageForDialogue(index));
        btnGroup.appendChild(selectBtn);

        if (selectedImages[index]) {
            const removeBtn = document.createElement('button');
            removeBtn.className = 'btn btn-small btn-danger';
            removeBtn.textContent = 'Remove';
            removeBtn.addEventListener('click', () => removeImage(index));
            btnGroup.appendChild(removeBtn);
        }

        div.appendChild(btnGroup);
        dialogueList.appendChild(div);
    });
}

// Select image for dialogue
async function selectImageForDialogue(index) {
    try {
        // Get active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Store the dialogue index we're selecting for
        await chrome.storage.local.set({ selectingForIndex: index });

        // Inject content script to enable area selection
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: enableAreaSelection,
            args: [index, currentSession]
        });

        showStatus('Drag to select an area on the page...', 'info');
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error enabling area selection', 'error');
    }
}

// This function runs in the page context - Area Selection
function enableAreaSelection(dialogueIndex, sessionId) {
    // Remove existing overlay
    const existingOverlay = document.getElementById('contentgen-overlay');
    if (existingOverlay) existingOverlay.remove();

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'contentgen-overlay';
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(102, 126, 234, 0.2); z-index: 999999; cursor: crosshair;
    `;

    // Create selection box
    const selectionBox = document.createElement('div');
    selectionBox.style.cssText = `
        position: fixed; border: 3px solid #667eea;
        background: transparent;
        display: none; z-index: 1000000;
        box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
        pointer-events: none;
    `;

    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
        background: white; padding: 15px 25px; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000001;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px; font-weight: 600;
    `;
    message.textContent = `📸 Drag to select area for dialogue #${dialogueIndex + 1} (ESC to cancel)`;

    document.body.appendChild(overlay);
    document.body.appendChild(selectionBox);
    document.body.appendChild(message);

    let startX, startY, isSelecting = false;

    const handleMouseDown = (e) => {
        isSelecting = true;
        startX = e.clientX;
        startY = e.clientY;
        selectionBox.style.left = startX + 'px';
        selectionBox.style.top = startY + 'px';
        selectionBox.style.width = '0px';
        selectionBox.style.height = '0px';
        selectionBox.style.display = 'block';
    };

    const handleMouseMove = (e) => {
        if (!isSelecting) return;

        const currentX = e.clientX;
        const currentY = e.clientY;

        const width = Math.abs(currentX - startX);
        const height = Math.abs(currentY - startY);
        const left = Math.min(currentX, startX);
        const top = Math.min(currentY, startY);

        selectionBox.style.left = left + 'px';
        selectionBox.style.top = top + 'px';
        selectionBox.style.width = width + 'px';
        selectionBox.style.height = height + 'px';
    };

    const handleMouseUp = async (e) => {
        if (!isSelecting) return;
        isSelecting = false;

        const rect = selectionBox.getBoundingClientRect();

        // Check if area is too small
        if (rect.width < 50 || rect.height < 50) {
            alert('Selected area too small. Please select a larger area.');
            selectionBox.style.display = 'none';
            return;
        }

        try {
            message.textContent = '📸 Capturing area...';

            // Hide overlay and selection box before capture to avoid blue tint
            overlay.style.display = 'none';
            selectionBox.style.display = 'none';
            message.style.display = 'none';

            // Wait a moment for the UI to update
            await new Promise(resolve => setTimeout(resolve, 100));

            // Send message to background to capture
            // Use viewport dimensions (what captureVisibleTab actually captures)
            const response = await new Promise((resolve) => {
                chrome.runtime.sendMessage({
                    action: 'captureArea',
                    rect: {
                        x: rect.left,
                        y: rect.top,
                        width: rect.width,
                        height: rect.height
                    },
                    screenWidth: window.innerWidth,  // viewport width, not screen width
                    screenHeight: window.innerHeight, // viewport height, not screen height
                    dialogueIndex: dialogueIndex,
                    sessionId: sessionId
                }, resolve);
            });

            if (response && response.success) {
                cleanup();
                const successMsg = document.createElement('div');
                successMsg.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #4caf50; color: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000001; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; font-weight: 600;';
                successMsg.textContent = '✓ Area captured successfully!';
                document.body.appendChild(successMsg);
                setTimeout(() => successMsg.remove(), 2000);
            } else {
                throw new Error(response?.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error capturing area: ' + error.message);
            cleanup();
        }
    };

    const handleEscape = (e) => {
        if (e.key === 'Escape') cleanup();
    };

    const cleanup = () => {
        overlay.remove();
        selectionBox.remove();
        message.remove();
        document.removeEventListener('mousedown', handleMouseDown);
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.removeEventListener('keydown', handleEscape);
    };

    overlay.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('keydown', handleEscape);
}

// Remove image
async function removeImage(index) {
    try {
        const response = await fetch(`${API_BASE}/api/extension/image/${currentSession}/${index}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            delete selectedImages[index];
            renderDialogueList();
            showStatus('Image removed', 'success');
        }
    } catch (error) {
        console.error('Error removing image:', error);
        showStatus('Error removing image', 'error');
    }
}

// Poll for updates
let pollingInterval;
function startPolling() {
    if (pollingInterval) clearInterval(pollingInterval);

    pollingInterval = setInterval(async () => {
        if (!currentSession) return;

        try {
            const response = await fetch(`${API_BASE}/api/extension/images/${currentSession}`);
            if (response.ok) {
                const images = await response.json();
                selectedImages = images;
                renderDialogueList();
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 2000);
}

// Show status
function showStatus(message, type = 'info') {
    statusBox.className = `status-box ${type}`;
    statusText.textContent = message;
    statusBox.style.display = 'block';

    setTimeout(() => {
        statusBox.style.display = 'none';
    }, 3000);
}

// Show empty state
function showEmptyState() {
    loadingState.style.display = 'none';
    dialogueContainer.style.display = 'none';
    emptyState.style.display = 'block';
}

// Initialize on load
init();
