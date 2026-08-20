import React from 'react';
import { Bot, Settings, Layers, FileText, AlertTriangle } from 'lucide-react';
import { useAppStore } from '../store';

export const Header: React.FC = () => {
  const { pageContext, isSettingsOpen, setIsSettingsOpen } = useAppStore();

  const renderBadge = () => {
    if (pageContext.mode === 'record') {
      return (
        <div className="badge badge-record">
          <FileText size={12} />
          <span>Record Mode: {pageContext.record_number || 'INC'}</span>
        </div>
      );
    }
    if (pageContext.mode === 'dashboard') {
      return (
        <div className="badge badge-dashboard">
          <Layers size={12} />
          <span>Dashboard Mode</span>
        </div>
      );
    }
    return (
      <div className="badge badge-unsupported">
        <AlertTriangle size={12} />
        <span>Inert / Unsupported</span>
      </div>
    );
  };

  return (
    <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
            }}
          >
            <Bot size={20} />
          </div>
          <div>
            <h1 style={{ fontSize: '15px', fontWeight: '700', letterSpacing: '-0.2px' }}>ServiceNow AI Assistant</h1>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Enterprise PDI AI Copilot</p>
          </div>
        </div>

        <button
          className="btn-secondary"
          onClick={() => setIsSettingsOpen(!isSettingsOpen)}
          title="Settings & API Configuration"
          style={{ padding: '6px' }}
        >
          <Settings size={16} />
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '4px' }}>
        {renderBadge()}
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>v1.0.0 DEV</span>
      </div>
    </div>
  );
};
