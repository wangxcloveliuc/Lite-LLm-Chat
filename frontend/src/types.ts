export interface Provider {
  id: string;
  name: string;
  description: string;
  supported?: boolean;
}

export interface Model {
  id: string;
  name: string;
  provider: string;
  description: string;
  context_length?: number;
}

export interface Message {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at?: string;
  provider?: string;
  model?: string;
  thought_process?: string;
}

export interface Session {
  id: number;
  title: string;
  provider: string;
  model: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  messages?: Message[];
}

export interface ChatRequest {
  provider: string;
  model: string;
  messages: { role: string; content: string }[];
  stream: boolean;
  temperature?: number;
  max_tokens?: number;
  session_id?: number;
  message_provider?: string;
  message_model?: string;
  title?: string;
}

export interface StreamChunk {
  content?: string;
  reasoning?: string;
  session_id?: number;
  error?: string;
  done?: boolean;
}
