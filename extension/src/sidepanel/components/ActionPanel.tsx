import React from 'react';
import { Send, FileText, Sparkles, LayoutList, Loader2 } from 'lucide-react';
import { useAppStore } from '../store';

export const ActionPanel: React.FC = () => {
  const {
    pageContext,
    backendUrl,
    authToken,
    customInstructions,
    setCustomInstructions,
    isLoading,
    setIsLoading,
    setAiResponse,
    setErrorMessage,
  } = useAppStore();

  const handleExecuteAction = (actionType: string) => {
    setIsLoading(true);
    let endpoint = '/api/v1/ai/generate';
    let body: any = {};

    if (pageContext.mode === 'record') {
      if (actionType === 'summarize_incident') {
        endpoint = '/api/v1/ai/summarize';
      } else if (actionType === 'improve_text') {
        endpoint = '/api/v1/ai/improve';
      }

      body = {
        mode: 'record',
        record_type: pageContext.record_type || 'incident',
        record_number: pageContext.record_number || 'INC0000000',
        action: actionType,
        custom_instructions: customInstructions || undefined,
        text_to_improve: actionType === 'improve_text' ? customInstructions : undefined,
      };
    } else if (pageContext.mode === 'dashboard') {
      endpoint = '/api/v1/ai/dashboard-summary';
      body = {
        mode: 'dashboard',
        widgets: pageContext.widgets || [],
        visibleRows: pageContext.visibleRows || [],
        action: 'summarize_queue',
        custom_instructions: customInstructions || undefined,
      };
    }

    chrome.runtime.sendMessage(
      {
        type: 'EXECUTE_BACKEND_API',
        payload: {
          endpoint,
          method: 'POST',
          body,
          token: authToken,
          backendUrl,
        },
      },
      (res) => {
        if (chrome.runtime.lastError) {
          setErrorMessage(chrome.runtime.lastError.message || 'Extension runtime error');
          return;
        }
        if (res && res.status === 'ok') {
          setAiResponse(res.data);
        } else {
          setErrorMessage(res?.error || 'API execution failed');
        }
      }
    );
  };

  if (pageContext.mode === 'unsupported') {
    return (
      <div className="card-glass" style={{ textAlign: 'center', padding: '20px 14px' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
          Navigate to an open <strong>Incident Record</strong> or a <strong>ServiceNow Workspace/Dashboard</strong> to trigger AI Assistant actions.
        </p>
      </div>
    );
  }

  return (
    <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div>
        <label style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
          Custom Prompt / Instructions (Optional)
        </label>
        <textarea
          value={customInstructions}
          onChange={(e) => setCustomInstructions(e.target.value)}
          placeholder={
            pageContext.mode === 'record'
              ? 'e.g. Include troubleshooting steps for VPN reset...'
              : 'e.g. Highlight tickets nearing SLA breach...'
          }
          style={{
            width: '100%',
            height: '60px',
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--bg-card-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px',
            color: 'var(--text-main)',
            fontSize: '12px',
            resize: 'none',
            outline: 'none',
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {pageContext.mode === 'record' ? (
          <>
            <button
              className="btn-primary"
              disabled={isLoading}
              onClick={() => handleExecuteAction('generate_customer_response')}
            >
              {isLoading ? <Loader2 size={16} className="spin" /> : <Send size={16} />}
              <span>Generate Customer Response</span>
            </button>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <button
                className="btn-secondary"
                disabled={isLoading}
                onClick={() => handleExecuteAction('summarize_incident')}
                style={{ justifyContent: 'center' }}
              >
                <FileText size={14} />
                <span>Summarize Incident</span>
              </button>

              <button
                className="btn-secondary"
                disabled={isLoading}
                onClick={() => handleExecuteAction('improve_text')}
                style={{ justifyContent: 'center' }}
              >
                <Sparkles size={14} />
                <span>Improve Text</span>
              </button>
            </div>
          </>
        ) : (
          <button
            className="btn-primary"
            disabled={isLoading}
            onClick={() => handleExecuteAction('summarize_queue')}
          >
            {isLoading ? <Loader2 size={16} className="spin" /> : <LayoutList size={16} />}
            <span>Summarize Queue / What Needs Attention</span>
          </button>
        )}
      </div>
    </div>
  );
};
