import React, { useEffect } from 'react';
import { Header } from './components/Header';
import { SettingsDrawer } from './components/SettingsDrawer';
import { ActionPanel } from './components/ActionPanel';
import { ResponseViewer } from './components/ResponseViewer';
import { useAppStore } from './store';
import { ServiceNowDetector } from '../content/servicenow-detector';

export const App: React.FC = () => {
  const { setPageContext } = useAppStore();

  useEffect(() => {
    // 1. Fetch current tab context on mount
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_SERVICENOW_CONTEXT' }, (response) => {
          if (response && response.payload) {
            setPageContext(response.payload);
          } else if (tabs[0].url) {
            // Fallback classification if content script hasn't responded yet
            setPageContext(ServiceNowDetector.classifyPage());
          }
        });
      }
    });

    // 2. Listen for runtime context updates sent from content script
    const listener = (message: any) => {
      if (message.type === 'SERVICENOW_CONTEXT_UPDATED' && message.payload) {
        setPageContext(message.payload);
      }
    };

    chrome.runtime.onMessage.addListener(listener);
    return () => chrome.runtime.onMessage.removeListener(listener);
  }, []);

  return (
    <div className="app-container">
      <Header />
      <SettingsDrawer />
      <ActionPanel />
      <ResponseViewer />
    </div>
  );
};
