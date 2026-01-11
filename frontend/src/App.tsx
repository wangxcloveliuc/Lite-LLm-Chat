import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import SettingsSidebar from './components/SettingsSidebar';
import { apiClient } from './api/apiClient';
import type { Provider, Model, Session, Message, DeepSeekSettings } from './types';
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
  const [showSettings, setShowSettings] = useState(false);
  const [deepseekSettings, setDeepseekSettings] = useState<DeepSeekSettings>({
    frequency_penalty: 0,
    max_tokens: 4096,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
  });

  useEffect(() => {
    if (selectedProvider === 'deepseek') {
      if (selectedModel === 'deepseek-reasoner') {
        setDeepseekSettings((prev) => ({ ...prev, max_tokens: 32768 }));
      } else {
        setDeepseekSettings((prev) => ({ ...prev, max_tokens: 4096 }));
      }
    }
  }, [selectedModel, selectedProvider]);

  useEffect(() => {
    loadProviders();
    loadSessions();
  }, []);

  const handleToggleSettings = async () => {
    // When opening settings, ensure models are loaded so modelId is set
    if (!showSettings && selectedProvider) {
      await loadModels(selectedProvider);
    }
    setShowSettings(!showSettings);
  };

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

  const refreshMessages = async (sessionId: number) => {
    const session = await apiClient.getSession(sessionId);
    if (session?.messages) {
      setMessages(session.messages);
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

    let newSessionId = currentSessionId;
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
        ...(selectedProvider === 'deepseek' ? {
          temperature: deepseekSettings.temperature,
          max_tokens: deepseekSettings.max_tokens,
          frequency_penalty: deepseekSettings.frequency_penalty,
          presence_penalty: deepseekSettings.presence_penalty,
          top_p: deepseekSettings.top_p,
          stop: deepseekSettings.stop ? deepseekSettings.stop.split(',').map(s => s.trim()) : undefined,
          system_prompt: deepseekSettings.system_prompt || undefined,
        } : {}),
      };

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
      const sessionIdToRefresh = newSessionId || currentSessionId;
      if (sessionIdToRefresh) {
        loadSessions();
        await refreshMessages(sessionIdToRefresh);
      }
    }
  };

  const handleRenameSession = async (sessionId: number, newTitle: string) => {
    const success = await apiClient.updateSession(sessionId, newTitle);
    if (success) {
      loadSessions();
    }
  };

  const handleEditMessage = async (index: number, content: string) => {
    const messageToEdit = messages[index];
    if (!messageToEdit || messageToEdit.role !== 'user') return;


    if (currentSessionId) {
      // Stop any current generation
      handleStopGeneration();
      
      // Truncate the session in the backend when we have a persisted message id
      if (messageToEdit.id) {
        await apiClient.truncateSession(currentSessionId, messageToEdit.id);
      }
      
      // Update local state: remove everything from this point onwards
      setMessages(prev => prev.slice(0, index));
      
      // Trigger new message sending
      handleSendMessage(content);
    } else {
      // New chat, haven't saved to DB yet
      handleStopGeneration();
      setMessages(prev => prev.slice(0, index));
      handleSendMessage(content);
    }
  };

  const handleRefreshMessage = async (index: number) => {
    const assistantMessage = messages[index];
    if (!assistantMessage || assistantMessage.role !== 'assistant') return;

    // Find the corresponding user message (should be at index - 1)
    const userMessageIndex = index - 1;
    if (userMessageIndex < 0) return;
    const userMessage = messages[userMessageIndex];
    if (!userMessage || userMessage.role !== 'user') return;

    if (currentSessionId) {
      handleStopGeneration();
      
      // Truncate the session in the backend starting from the user message to avoid duplication
      if (userMessage.id) {
        await apiClient.truncateSession(currentSessionId, userMessage.id);
      }
      
      // Update local state: remove the user message and everything after it
      setMessages(prev => prev.slice(0, userMessageIndex));
      
      // Re-send the user message content - this will re-add it to the state and backend
      handleSendMessage(userMessage.content);
    } else {
      // New chat, haven't saved to DB yet
      handleStopGeneration();
      setMessages(prev => prev.slice(0, userMessageIndex));
      handleSendMessage(userMessage.content);
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
          onToggleSettings={handleToggleSettings}
        />
        <ChatArea
          messages={messages}
          isLoading={isLoading}
          isChatActive={messages.length > 0}
          onSendMessage={handleSendMessage}
          onStopMessage={handleStopGeneration}
          onEditMessage={handleEditMessage}
          onRefreshMessage={handleRefreshMessage}
        />
      </main>
      <SettingsSidebar
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        provider={selectedProvider}
        modelId={selectedModel}
        settings={deepseekSettings}
        onSettingsChange={setDeepseekSettings}
      />
    </div>
  );
}

export default App;
