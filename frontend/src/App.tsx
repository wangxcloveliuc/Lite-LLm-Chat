import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import { apiClient } from './api/apiClient';
import type { Provider, Model, Session, Message } from './types';
import './App.css';

function App() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadProviders();
    loadSessions();
  }, []);

  useEffect(() => {
    if (selectedProvider) {
      loadModels(selectedProvider);
    }
  }, [selectedProvider]);

  const loadProviders = async () => {
    const data = await apiClient.getProviders();
    setProviders(data);
    if (data.length > 0 && !selectedProvider) {
      setSelectedProvider(data[0].id);
    }
  };

  const loadModels = async (provider: string) => {
    const data = await apiClient.getModels(provider);
    setModels(data);
    if (data.length > 0 && !selectedModel) {
      setSelectedModel(data[0].id);
    }
  };

  const loadSessions = async () => {
    const data = await apiClient.getSessions();
    setSessions(data);
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
  };

  const handleSessionSelect = async (sessionId: number) => {
    const session = await apiClient.getSession(sessionId);
    if (session) {
      setCurrentSessionId(session.id);
      setMessages(session.messages || []);
      setSelectedProvider(session.provider);
      setSelectedModel(session.model);
    }
  };

  const handleProviderChange = (providerId: string) => {
    setSelectedProvider(providerId);
    setSelectedModel('');
  };

  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
  };

  const handleSendMessage = async (content: string) => {
    if (!selectedProvider || !selectedModel) return;

    const userMessage: Message = {
      role: 'user',
      content,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const assistantMessage: Message = {
        role: 'assistant',
        content: '',
      };

      setMessages((prev) => [...prev, assistantMessage]);

      const request = {
        provider: selectedProvider,
        model: selectedModel,
        messages: [{ role: 'user', content }],
        stream: true,
        session_id: currentSessionId || undefined,
        title: currentSessionId ? undefined : content.substring(0, 50),
      };

      let newSessionId = currentSessionId;
      
      for await (const chunk of apiClient.chatStream(request)) {
        if (chunk.session_id && !newSessionId) {
          newSessionId = chunk.session_id;
          setCurrentSessionId(newSessionId);
          loadSessions();
        }

        if (chunk.content) {
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg && lastMsg.role === 'assistant') {
              lastMsg.content += chunk.content;
            }
            return updated;
          });
        }

        if (chunk.error) {
          console.error('Stream error:', chunk.error);
          break;
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: 'Sorry, an error occurred. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
      if (currentSessionId) {
        loadSessions();
      }
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSessionSelect={handleSessionSelect}
      />
      <main className="main-content">
        <Header
          providers={providers}
          models={models}
          selectedProvider={selectedProvider}
          selectedModel={selectedModel}
          onProviderChange={handleProviderChange}
          onModelChange={handleModelChange}
        />
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          isChatActive={messages.length > 0}
          onSendMessage={handleSendMessage}
        />
      </main>
    </div>
  );
}

export default App;
