import { create } from 'zustand';
import { PageContext } from '../content/servicenow-detector';

export interface GuardrailNotice {
  code: string;
  message: string;
  severity: string;
}

export interface AIResponse {
  mode: string;
  action: string;
  content: string;
  prompt_version: string;
  model_used: string;
  guardrail_notices: GuardrailNotice[];
  record_number?: string;
}

interface AppState {
  pageContext: PageContext;
  backendUrl: string;
  authToken: string;
  aiResponse: AIResponse | null;
  isLoading: boolean;
  errorMessage: string | null;
  customInstructions: string;
  isSettingsOpen: boolean;

  setPageContext: (ctx: PageContext) => void;
  setBackendUrl: (url: string) => void;
  setAuthToken: (token: string) => void;
  setAiResponse: (resp: AIResponse | null) => void;
  setIsLoading: (loading: boolean) => void;
  setErrorMessage: (msg: string | null) => void;
  setCustomInstructions: (inst: string) => void;
  setIsSettingsOpen: (open: boolean) => void;
  resetResponse: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  pageContext: {
    mode: 'unsupported',
    url: '',
    timestamp: new Date().toISOString(),
  },
  backendUrl: 'http://localhost:8000',
  authToken: 'dev-token-bypass',
  aiResponse: null,
  isLoading: false,
  errorMessage: null,
  customInstructions: '',
  isSettingsOpen: false,

  setPageContext: (ctx) => set({ pageContext: ctx }),
  setBackendUrl: (url) => set({ backendUrl: url }),
  setAuthToken: (token) => set({ authToken: token }),
  setAiResponse: (resp) => set({ aiResponse: resp, isLoading: false, errorMessage: null }),
  setIsLoading: (loading) => set({ isLoading: loading, errorMessage: null }),
  setErrorMessage: (msg) => set({ errorMessage: msg, isLoading: false }),
  setCustomInstructions: (inst) => set({ customInstructions: inst }),
  setIsSettingsOpen: (open) => set({ isSettingsOpen: open }),
  resetResponse: () => set({ aiResponse: null, errorMessage: null }),
}));
