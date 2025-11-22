// Parse dialogue script
function parseDialogue(script) {
    const lines = script.trim().split('\n');
    const dialogue = [];

    for (const line of lines) {
        const match = line.match(/^([^:]+):\s*(.+)$/);
        if (match) {
            dialogue.push({
                speaker: match[1].trim(),
                text: match[2].trim()
            });
        }
    }

    return dialogue;
}

// State
let dialogueData = [];
let selectedImages = {};

// Elements
const scriptSection = document.getElementById('scriptSection');
const selectionSection = document.getElementById('selectionSection');
const scriptInput = document.getElementById('scriptInput');
const parseBtn = document.getElementById('parseBtn');
const dialogueList = document.getElementById('dialogueList');
const exportBtn = document.getElementById('exportBtn');
const resetBtn = document.getElementById('resetBtn');

// Load saved state
chrome.storage.local.get(['dialogueData', 'selectedImages'], (result) => {
    if (result.dialogueData) {
        dialogueData = result.dialogueData;
        selectedImages = result.selectedImages || {};
        showSelectionSection();
    }
});

// Parse script
parseBtn.addEventListener('click', () => {
    const script = scriptInput.value.trim();
    if (!script) {
        alert('Please enter a dialogue script');
        return;
    }

    dialogueData = parseDialogue(script);
    if (dialogueData.length === 0) {
        alert('No valid dialogue found. Use format: "Speaker: Text"');
        return;
    }

    selectedImages = {};
    saveState();
    showSelectionSection();
});

// Show selection section
function showSelectionSection() {
    scriptSection.classList.add('hidden');
    selectionSection.classList.remove('hidden');
    renderDialogueList();
}

// Render dialogue list
function renderDialogueList() {
    dialogueList.innerHTML = '';

    dialogueData.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'dialogue-item';

        const text = document.createElement('div');
        text.className = 'dialogue-text';
        text.textContent = `${item.speaker}: ${item.text}`;
        div.appendChild(text);

        const selectBtn = document.createElement('button');
        selectBtn.className = 'btn btn-small';
        selectBtn.textContent = selectedImages[index] ? '✓ Change Image' : 'Select Image';
        selectBtn.addEventListener('click', () => selectImageForDialogue(index));
        div.appendChild(selectBtn);

        if (selectedImages[index]) {
            const img = document.createElement('img');
            img.className = 'image-preview';
            img.src = selectedImages[index];
            div.appendChild(img);
        }

        dialogueList.appendChild(div);
    });
}

// Select image for dialogue
async function selectImageForDialogue(index) {
    try {
        // Get active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Inject content script and enable selection mode
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: enableImageSelection,
            args: [index]
        });

        // Close popup to allow user to select
        window.close();
    } catch (error) {
        console.error('Error:', error);
        alert('Error enabling image selection. Please try again.');
    }
}

// This function runs in the page context
function enableImageSelection(dialogueIndex) {
    // Remove existing overlay if any
    const existingOverlay = document.getElementById('contentgen-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'contentgen-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999999;
        cursor: crosshair;
    `;

    const message = document.createElement('div');
    message.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
    `;
    message.textContent = '📸 Click on any image to select it (ESC to cancel)';

    document.body.appendChild(overlay);
    document.body.appendChild(message);

    // Handle image click
    const handleImageClick = async (e) => {
        if (e.target.tagName === 'IMG') {
            e.preventDefault();
            e.stopPropagation();

            try {
                // Convert image to data URL
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = e.target.naturalWidth || e.target.width;
                canvas.height = e.target.naturalHeight || e.target.height;
                ctx.drawImage(e.target, 0, 0);
                const dataUrl = canvas.toDataURL('image/jpeg', 0.8);

                // Save to storage
                chrome.storage.local.get(['selectedImages'], (result) => {
                    const images = result.selectedImages || {};
                    images[dialogueIndex] = dataUrl;
                    chrome.storage.local.set({ selectedImages: images });
                });

                cleanup();
                alert('✓ Image selected successfully!');
            } catch (error) {
                console.error('Error capturing image:', error);
                alert('Error capturing image. Please try again.');
            }
        }
    };

    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            cleanup();
        }
    };

    const cleanup = () => {
        overlay.remove();
        message.remove();
        document.removeEventListener('click', handleImageClick, true);
        document.removeEventListener('keydown', handleEscape);
    };

    document.addEventListener('click', handleImageClick, true);
    document.addEventListener('keydown', handleEscape);
}

// Export data
exportBtn.addEventListener('click', async () => {
    const exportData = {
        dialogue: dialogueData,
        images: selectedImages,
        timestamp: new Date().toISOString()
    };

    const jsonString = JSON.stringify(exportData, null, 2);

    try {
        await navigator.clipboard.writeText(jsonString);
        alert('✓ Data copied to clipboard! Paste it in the ContentGen web app.');
    } catch (error) {
        // Fallback: show in alert
        prompt('Copy this data:', jsonString);
    }
});

// Reset
resetBtn.addEventListener('click', () => {
    if (confirm('Reset and start over?')) {
        dialogueData = [];
        selectedImages = {};
        chrome.storage.local.clear();
        scriptSection.classList.remove('hidden');
        selectionSection.classList.add('hidden');
        scriptInput.value = '';
    }
});

// Save state
function saveState() {
    chrome.storage.local.set({
        dialogueData: dialogueData,
        selectedImages: selectedImages
    });
}
