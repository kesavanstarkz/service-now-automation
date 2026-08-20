import { ServiceNowDetector, PageContext } from './servicenow-detector';

let currentContext: PageContext = ServiceNowDetector.classifyPage();

function updateAndBroadcastContext() {
  const newContext = ServiceNowDetector.classifyPage();
  currentContext = newContext;

  try {
    chrome.runtime.sendMessage({
      type: 'SERVICENOW_CONTEXT_UPDATED',
      payload: newContext,
    });
  } catch (e) {
    // Ignore context invalidation during extension reload
  }
}

// 1. Listen for SPA Navigation (history.pushState / popstate)
const originalPushState = history.pushState;
history.pushState = function (...args) {
  originalPushState.apply(this, args);
  setTimeout(updateAndBroadcastContext, 300);
};

window.addEventListener('popstate', () => {
  setTimeout(updateAndBroadcastContext, 300);
});

// 2. MutationObserver for SPA view changes
const observer = new MutationObserver(() => {
  const newContext = ServiceNowDetector.classifyPage();
  if (
    newContext.mode !== currentContext.mode ||
    newContext.record_number !== currentContext.record_number
  ) {
    currentContext = newContext;
    updateAndBroadcastContext();
  }
});

observer.observe(document.body, { childList: true, subtree: true });

// 3. Handle incoming extension messages
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === 'GET_SERVICENOW_CONTEXT') {
    currentContext = ServiceNowDetector.classifyPage();
    sendResponse({ status: 'ok', payload: currentContext });
    return true;
  }

  if (message.type === 'INSERT_TEXT_INTO_ACTIVE_FIELD') {
    const textToInsert = message.payload?.text || '';
    const success = insertTextIntoActiveElement(textToInsert);
    sendResponse({ status: success ? 'ok' : 'failed' });
    return true;
  }
});

function insertTextIntoActiveElement(text: string): boolean {
  let activeElem = document.activeElement as HTMLInputElement | HTMLTextAreaElement | HTMLElement;

  // Search for work notes / comments textarea if active element is neutral body
  if (!activeElem || activeElem === document.body) {
    activeElem = document.querySelector<HTMLTextAreaElement>(
      'textarea[id$="work_notes"], textarea[name$="work_notes"], textarea[id$="comments"], textarea[aria-label*="Work notes"]'
    ) || activeElem;
  }

  if (activeElem && ('value' in activeElem || activeElem.isContentEditable)) {
    if ('value' in activeElem) {
      const input = activeElem as HTMLInputElement | HTMLTextAreaElement;
      const start = input.selectionStart || 0;
      const end = input.selectionEnd || 0;
      const val = input.value;
      input.value = val.substring(0, start) + text + val.substring(end);
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    } else if (activeElem.isContentEditable) {
      activeElem.innerText = text;
      activeElem.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }
  }

  // Fallback: Copy to clipboard if no active input focused
  navigator.clipboard.writeText(text);
  alert('No active text field was focused. Response has been copied to your clipboard instead!');
  return false;
}

// Initial broadcast on load
setTimeout(updateAndBroadcastContext, 500);
