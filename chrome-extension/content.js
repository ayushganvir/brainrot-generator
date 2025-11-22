// Content script - runs on all pages
console.log('ContentGen Image Selector loaded');

// Listen for session creation on localhost:8000
if (window.location.hostname === 'localhost' && window.location.port === '8000') {
    window.addEventListener('contentgen-session-created', (event) => {
        console.log('Session created:', event.detail.sessionId);
        // Send to extension
        chrome.runtime.sendMessage({
            action: 'sessionCreated',
            sessionId: event.detail.sessionId
        });
    });

    // Also check on load
    setTimeout(() => {
        const sessionId = window.sessionId || localStorage.getItem('sessionId');
        if (sessionId) {
            chrome.runtime.sendMessage({
                action: 'sessionCreated',
                sessionId: sessionId
            });
        }
    }, 1000);
}
