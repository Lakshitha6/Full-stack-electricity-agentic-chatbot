// Interface for chat data

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    sql?: string;
    error?: string;
    confidence?: number;
    [key: string]: any;
  };
}

export interface Session {
  session_id: string;
  title: string;
  started_at: string;
  last_message_at?: string;
  is_active?: boolean;
}

export interface ChatRequest {
  electricity_id: string;
  session_id?: string;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  message_id: string;
  response: string;
  timestamp: string;
  metadata?: {
    sql?: string;
    error?: string;
    [key: string]: any;
  };
}