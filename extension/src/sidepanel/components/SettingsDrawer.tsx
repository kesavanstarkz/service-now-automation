import React, { useEffect } from 'react';
import { X, Save, Server, Key } from 'lucide-react';
import { useAppStore } from '../store';

export const SettingsDrawer: React.FC = () => {
  const {
    isSettingsOpen,
    setIsSettingsOpen,
    backendUrl,
    setBackendUrl,
    authToken,
    setAuthToken,
  } = useAppStore();

  useEffect(() => {
    // Load from chrome.storage
    chrome.storage.local.get(['backendUrl', 'authToken'], (items) => {
      if (items.backendUrl) setBackendUrl(items.backendUrl);
      if (items.authToken) setAuthToken(items.authToken);
    });
  }, []);

  const handleSave = () => {
    chrome.storage.local.set({ backendUrl, authToken }, () => {
      setIsSettingsOpen(false);
    });
  };

  if (!isSettingsOpen) return null;

  return (
    <div className="card-glass" style={{ border: '1px solid var(--accent-primary)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '14px', fontWeight: '600' }}>Settings & Connection</h3>
        <button className="btn-secondary" onClick={() => setIsSettingsOpen(false)} style={{ padding: '4px' }}>
          <X size={14} />
        </button>
      </div>

      <div>
        <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
          <Server size={12} /> Backend API Endpoint
        </label>
        <input
          type="text"
          value={backendUrl}
          onChange={(e) => setBackendUrl(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--bg-card-border)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-main)',
            fontSize: '12px',
          }}
        />
      </div>

      <div>
        <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
          <Key size={12} /> Auth Token (Bearer / Dev Bypass)
        </label>
        <input
          type="password"
          value={authToken}
          onChange={(e) => setAuthToken(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--bg-card-border)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-main)',
            fontSize: '12px',
          }}
        />
      </div>

      <button className="btn-primary" onClick={handleSave} style={{ alignSelf: 'flex-end', marginTop: '4px' }}>
        <Save size={14} />
        <span>Save Connection Settings</span>
      </button>
    </div>
  );
};
