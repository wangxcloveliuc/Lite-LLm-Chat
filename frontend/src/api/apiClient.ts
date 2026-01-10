import type { Provider, Model, Session, Message, ChatRequest, StreamChunk } from '../types';

const BASE_URL = 'http://localhost:8000';
const API_PREFIX = '/api/v1';

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private url(path: string): string {
    return `${this.baseUrl}${API_PREFIX}${path}`;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async getProviders(): Promise<Provider[]> {
    try {
      const response = await fetch(this.url('/providers'));
      if (response.ok) {
        return await response.json();
      }
      return [];
    } catch {
      return [];
    }
  }

  async getModels(provider?: string): Promise<Model[]> {
    try {
      const url = provider
        ? `${this.url('/models')}?provider=${encodeURIComponent(provider)}`
        : this.url('/models');
      const response = await fetch(url);
      if (response.ok) {
        return await response.json();
      }
      return [];
    } catch {
      return [];
    }
  }

  async getSessions(skip: number = 0, limit: number = 100): Promise<Session[]> {
    try {
      const response = await fetch(
        `${this.url('/sessions')}?skip=${skip}&limit=${limit}`
      );
      if (response.ok) {
        return await response.json();
      }
      return [];
    } catch {
      return [];
    }
  }

  async getSession(sessionId: number): Promise<Session | null> {
    try {
      const response = await fetch(this.url(`/sessions/${sessionId}`));
      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch {
      return null;
    }
  }

  async createSession(
    title: string,
    provider: string,
    model: string
  ): Promise<Session | null> {
    try {
      const response = await fetch(this.url('/sessions'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, provider, model }),
      });
      if (response.status === 201) {
        return await response.json();
      }
      return null;
    } catch {
      return null;
    }
  }

  async updateSession(sessionId: number, title: string): Promise<boolean> {
    try {
      const response = await fetch(this.url(`/sessions/${sessionId}`), {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async deleteSession(sessionId: number): Promise<boolean> {
    try {
      const response = await fetch(this.url(`/sessions/${sessionId}`), {
        method: 'DELETE',
      });
      return response.status === 204;
    } catch {
      return false;
    }
  }

  async deleteAllSessions(): Promise<boolean> {
    try {
      const response = await fetch(this.url('/sessions'), {
        method: 'DELETE',
      });
      return response.status === 204;
    } catch {
      return false;
    }
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<StreamChunk, void, unknown> {
    const response = await fetch(this.url('/chat'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith('data:')) continue;

          const dataStr = trimmed.substring(5).trim();
          if (!dataStr || dataStr === '[DONE]') continue;

          try {
            const data = JSON.parse(dataStr) as StreamChunk;
            yield data;
            if (data.error || data.done) return;
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async chat(
    messages: Message[],
    provider: string,
    model: string,
    sessionId?: number,
    title?: string
  ): Promise<{ session_id: number; message: Message } | null> {
    try {
      const response = await fetch(this.url('/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          model,
          messages: messages.map((m) => ({ role: m.role, content: m.content })),
          stream: false,
          session_id: sessionId,
          title,
        }),
      });
      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch {
      return null;
    }
  }
}

export const apiClient = new APIClient();
