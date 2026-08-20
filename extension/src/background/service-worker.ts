chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((err) => {
  console.warn('Failed to set side panel behavior:', err);
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'EXECUTE_BACKEND_API') {
    const { endpoint, method, body, token } = message.payload;
    const backendUrl = message.payload.backendUrl || 'http://localhost:8000';

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    fetch(`${backendUrl}${endpoint}`, {
      method: method || 'POST',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          sendResponse({ status: 'error', error: data.detail || 'API request failed' });
        } else {
          sendResponse({ status: 'ok', data });
        }
      })
      .catch((err) => {
        sendResponse({ status: 'error', error: err.message || 'Network connection failed' });
      });

    return true; // Async response
  }
});
