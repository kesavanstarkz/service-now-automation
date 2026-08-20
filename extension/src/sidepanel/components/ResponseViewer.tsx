import React, { useState } from 'react';
import { Copy, Check, CornerDownLeft, RefreshCw, AlertCircle, ShieldAlert } from 'lucide-react';
import { useAppStore } from '../store';

export const ResponseViewer: React.FC = () => {
  const { aiResponse, errorMessage, resetResponse, isLoading } = useAppStore();
  const [copied, setCopied] = useState(false);
  const [inserted, setInserted] = useState(false);

  if (errorMessage) {
    return (
      <div
        className="card-glass"
        style={{
          border: '1px solid rgba(239, 68, 68, 0.3)',
          background: 'rgba(239, 68, 68, 0.1)',
          color: '#fca5a5',
          display: 'flex',
          gap: '10px',
          alignItems: 'flex-start',
        }}
      >
        <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h4 style={{ fontSize: '13px', fontWeight: '600' }}>Backend Request Failed</h4>
          <p style={{ fontSize: '12px', marginTop: '4px' }}>{errorMessage}</p>
        </div>
      </div>
    );
  }

  if (!aiResponse) {
    return null;
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(aiResponse.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleInsert = () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]?.id) {
        chrome.tabs.sendMessage(
          tabs[0].id,
          {
            type: 'INSERT_TEXT_INTO_ACTIVE_FIELD',
            payload: { text: aiResponse.content },
          },
          (res) => {
            if (res && res.status === 'ok') {
              setInserted(true);
              setTimeout(() => setInserted(false), 2000);
            }
          }
        );
      }
    });
  };

  return (
    <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Guardrail Notices Header */}
      {aiResponse.guardrail_notices && aiResponse.guardrail_notices.length > 0 && (
        <div
          style={{
            background: 'var(--warning-bg)',
            border: '1px solid rgba(234, 179, 8, 0.3)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--warning-text)',
            fontSize: '11px',
          }}
        >
          <ShieldAlert size={14} />
          <span>{aiResponse.guardrail_notices[0].message}</span>
        </div>
      )}

      {/* Main Response Output text */}
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.5)',
          borderRadius: 'var(--radius-sm)',
          padding: '12px',
          fontSize: '13px',
          lineHeight: '1.6',
          whiteSpace: 'pre-wrap',
          maxHeight: '300px',
          overflowY: 'auto',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }}
      >
        {aiResponse.content}
      </div>

      {/* Response Metadata & Action Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
          Model: {aiResponse.model_used} | {aiResponse.prompt_version}
        </span>

        <div style={{ display: 'flex', gap: '6px' }}>
          <button className="btn-secondary" onClick={handleCopy} title="Copy to Clipboard">
            {copied ? <Check size={14} color="#4ade80" /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button className="btn-primary" onClick={handleInsert} style={{ padding: '6px 12px', fontSize: '12px' }}>
            {inserted ? <Check size={14} /> : <CornerDownLeft size={14} />}
            <span>{inserted ? 'Inserted' : 'Insert'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
