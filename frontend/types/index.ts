// TypeScript types for the Todo application

export interface TodoItem {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  userId: string;
}

export interface UserSession {
  userId: string;
  jwtToken: string;
  expiresAt: string; // ISO date string
  isAuthenticated: boolean;
}

export interface UIState {
  loading: boolean;
  error: string | null;
  success: string | null;
  currentView: string;
  breakpoints: {
    isMobile: boolean;
    isTablet: boolean;
    isDesktop: boolean;
  };
}

export interface FormState {
  formData: Record<string, any>;
  touched: Record<string, boolean>;
  errors: Record<string, string>;
  isValid: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  user_id: string;
  message: string;
  conversation_history: ChatMessage[];
}

export interface ChatResponse {
  response_text: string;
  tool_invocations: any[];
  metadata: Record<string, any>;
}