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
  const [abortController, setAbortController] = useState<AbortController | null>(null);

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

  const handleStopGeneration = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!selectedProvider || !selectedModel) return;

    const userMessage: Message = {
      role: 'user',
      content,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    const controller = new AbortController();
    setAbortController(controller);

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
      
      for await (const chunk of apiClient.chatStream(request, controller.signal)) {
        if (chunk.session_id && !newSessionId) {
          newSessionId = chunk.session_id;
          setCurrentSessionId(newSessionId);
          loadSessions();
        }

        if (chunk.content) {
          const incoming = chunk.content;
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg && lastMsg.role === 'assistant') {
              const newContent = incoming.startsWith(lastMsg.content)
                ? incoming // provider sends cumulative content
                : lastMsg.content + incoming; // provider sends deltas
              updated[updated.length - 1] = { ...lastMsg, content: newContent };
            }
            return updated;
          });
        }

        if (chunk.reasoning) {
          const reasoningDelta = chunk.reasoning;
          setMessages((prev) => {
            const updated = [...prev];
            const lastMsg = updated[updated.length - 1];
            if (lastMsg && lastMsg.role === 'assistant') {
              const newReasoning = (lastMsg.thought_process || '') + reasoningDelta;
              updated[updated.length - 1] = { ...lastMsg, thought_process: newReasoning };
            }
            return updated;
          });
        }

        if (chunk.error) {
          console.error('Stream error:', chunk.error);
          break;
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Generation aborted');
      } else {
        console.error('Chat error:', error);
        setMessages((prev) => [
          ...prev.slice(0, -1),
          {
            role: 'assistant',
            content: 'Sorry, an error occurred. Please try again.',
          },
        ]);
      }
    } finally {
      setIsLoading(false);
      setAbortController(null);
      if (currentSessionId) {
        loadSessions();
      }
    }
  };

  const handleRenameSession = async (sessionId: number, newTitle: string) => {
    const success = await apiClient.updateSession(sessionId, newTitle);
    if (success) {
      loadSessions();
    }
  };

  const handleDeleteSession = async (sessionId: number) => {
    const success = await apiClient.deleteSession(sessionId);
    if (success) {
      if (currentSessionId === sessionId) {
        handleNewChat();
      }
      loadSessions();
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSessionSelect={handleSessionSelect}
        onRenameSession={handleRenameSession}
        onDeleteSession={handleDeleteSession}
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
          onStopMessage={handleStopGeneration}
        />
      </main>
    </div>
  );
}

export default App;
