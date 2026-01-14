import { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import SettingsSidebar from './components/SettingsSidebar';
import { apiClient } from './api/apiClient';
import type { Provider, Model, Session, Message, DeepSeekSettings, DoubaoSettings, SiliconFlowSettings, CerebrasSettings, GroqSettings, MistralSettings, ChatRequest } from './types';
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
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
  });
  const [doubaoSettings, setDoubaoSettings] = useState<DoubaoSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
    thinking: undefined,
    reasoning_effort: 'medium',
    max_completion_tokens: undefined,
  });
  const [siliconflowSettings, setSiliconflowSettings] = useState<SiliconFlowSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
    enable_thinking: undefined,
    thinking_budget: undefined,
    min_p: undefined,
    top_k: undefined,
  });
  const [cerebrasSettings, setCerebrasSettings] = useState<CerebrasSettings>({
    max_tokens: undefined,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    reasoning_effort: 'medium',
    disable_reasoning: false,
  });
  const [groqSettings, setGroqSettings] = useState<GroqSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 0.6,
    top_p: 0.95,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    reasoning_format: 'parsed',
    include_reasoning: true,
    reasoning_effort: 'default',
    max_completion_tokens: undefined,
  });
  const [mistralSettings, setMistralSettings] = useState<MistralSettings>({
    temperature: 0.7,
    top_p: 1,
    max_tokens: undefined,
    safe_prompt: false,
    random_seed: undefined,
    stop: '',
    system_prompt: '',
    frequency_penalty: 0,
    presence_penalty: 0,
  });

  type ChatRequestSettings = {
    temperature?: number;
    max_tokens?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    top_p?: number;
    stop?: string[];
    system_prompt?: string;
    image_detail?: string;
    image_pixel_limit?: {
      max_pixels?: number;
      min_pixels?: number;
    };
    fps?: number;
    video_detail?: string;
    max_frames?: number;
    safe_prompt?: boolean;
    random_seed?: number;
    thinking?: boolean;
    reasoning_effort?: string;
    disable_reasoning?: boolean;
    reasoning_format?: string;
    include_reasoning?: boolean;
    max_completion_tokens?: number;
    enable_thinking?: boolean;
    thinking_budget?: number;
    min_p?: number;
    top_k?: number;
  };

  const loadProviders = useCallback(async () => {
    const data = await apiClient.getProviders();
    setProviders(data);
    if (data.length > 0 && !selectedProvider) {
      setSelectedProvider(data[0].id);
    }
  }, [selectedProvider]);

  const loadModels = useCallback(async (provider: string) => {
    const data = await apiClient.getModels(provider);
    setModels(data);
    if (data.length > 0 && !selectedModel) {
      setSelectedModel(data[0].id);
    }
  }, [selectedModel]);

  const loadSessions = useCallback(async () => {
    const data = await apiClient.getSessions();
    setSessions(data);
  }, []);

  useEffect(() => {
    loadProviders();
    loadSessions();
  }, [loadProviders, loadSessions]);

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
  }, [loadModels, selectedProvider]);

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

  const handleSendMessage = async (content: string, imageUrls?: string[], videoUrls?: string[], audioUrls?: string[]) => {
    if (!selectedProvider || !selectedModel) return;

    const userMessage: Message = {
      role: 'user',
      content,
      images: imageUrls,
      videos: videoUrls,
      audios: audioUrls,
    };

    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
    };

    // Add both messages at once to avoid potential state synchronization issues
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setIsLoading(true);
    const controller = new AbortController();
    setAbortController(controller);

    let newSessionId = currentSessionId;

    // Gather settings based on provider
    let currentSettings: ChatRequestSettings = {};
    if (selectedProvider === 'doubao') {
      currentSettings = {
        ...doubaoSettings,
        stop: doubaoSettings.stop ? doubaoSettings.stop.split(',').map((s) => s.trim()) : undefined,
      };
    } else if (selectedProvider === 'deepseek') {
      currentSettings = {
        ...deepseekSettings,
        stop: deepseekSettings.stop ? deepseekSettings.stop.split(',').map((s) => s.trim()) : undefined,
      };
    } else if (selectedProvider === 'siliconflow') {
      currentSettings = {
        ...siliconflowSettings,
        stop: siliconflowSettings.stop ? siliconflowSettings.stop.split(',').map((s) => s.trim()) : undefined,
      };
    } else if (selectedProvider === 'cerebras') {
      currentSettings = {
        ...cerebrasSettings,
        stop: cerebrasSettings.stop ? cerebrasSettings.stop.split(',').map((s) => s.trim()) : undefined,
      };
    } else if (selectedProvider === 'groq') {
      currentSettings = {
        ...groqSettings,
        stop: groqSettings.stop ? groqSettings.stop.split(',').map((s) => s.trim()) : undefined,
      };
    } else if (selectedProvider === 'mistral') {
      currentSettings = {
        ...mistralSettings,
        stop: mistralSettings.stop ? mistralSettings.stop.split(',').map((s) => s.trim()) : undefined,
      };
    } else {
      // Fallback to deepseek settings as default for other providers (common basic settings)
      currentSettings = {
        ...deepseekSettings,
        stop: deepseekSettings.stop ? deepseekSettings.stop.split(',').map((s) => s.trim()) : undefined,
      };
    }

    try {
      const request: ChatRequest = {
        provider: selectedProvider,
        model: selectedModel,
        messages: [{ role: 'user', content, images: imageUrls, videos: videoUrls, audios: audioUrls }],
        stream: true,
        session_id: currentSessionId || undefined,
        title: currentSessionId ? undefined : content.substring(0, 50),
        // Common basic settings
        temperature: currentSettings.temperature,
        max_tokens: currentSettings.max_tokens,
        frequency_penalty: currentSettings.frequency_penalty,
        presence_penalty: currentSettings.presence_penalty,
        top_p: currentSettings.top_p,
        stop: currentSettings.stop,
        system_prompt: currentSettings.system_prompt || undefined,
        image_detail: currentSettings.image_detail,
        image_pixel_limit: currentSettings.image_pixel_limit,
        fps: currentSettings.fps,
        video_detail: currentSettings.video_detail,
        max_frames: currentSettings.max_frames,
        // Mistral-specific settings
        safe_prompt: currentSettings.safe_prompt,
        random_seed: currentSettings.random_seed,
        // Doubao-specific settings
        thinking: currentSettings.thinking,
        reasoning_effort: currentSettings.reasoning_effort,
        disable_reasoning: currentSettings.disable_reasoning,
        reasoning_format: currentSettings.reasoning_format,
        include_reasoning: currentSettings.include_reasoning,
        max_completion_tokens: currentSettings.max_completion_tokens,
        enable_thinking: currentSettings.enable_thinking,
        thinking_budget: currentSettings.thinking_budget,
        min_p: currentSettings.min_p,
        top_k: currentSettings.top_k,
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
    } catch (error: unknown) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        console.log('Generation aborted');
      } else {
        console.error('Chat error:', error);
        setMessages((prev) => {
          const updated = [...prev];
          if (updated.length > 0 && updated[updated.length - 1].role === 'assistant') {
            updated[updated.length - 1] = {
              role: 'assistant',
              content: 'Sorry, an error occurred. Please try again.',
            };
            return updated;
          }
          return [
            ...prev,
            {
              role: 'assistant',
              content: 'Sorry, an error occurred. Please try again.',
            },
          ];
        });
      }
    } finally {
      setIsLoading(false);
      setAbortController(null);
      const sessionIdToRefresh = newSessionId || currentSessionId;
      if (sessionIdToRefresh) {
        loadSessions();
        // Only refresh messages if it was successful, or if we want to sync with DB
        // If an error occurred, we might want to keep the local error message
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
      handleSendMessage(content, messageToEdit.images);
    } else {
      // New chat, haven't saved to DB yet
      handleStopGeneration();
      setMessages(prev => prev.slice(0, index));
      handleSendMessage(content, messageToEdit.images);
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
      handleSendMessage(userMessage.content, userMessage.images);
    } else {
      // New chat, haven't saved to DB yet
      handleStopGeneration();
      setMessages(prev => prev.slice(0, userMessageIndex));
      handleSendMessage(userMessage.content, userMessage.images);
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
        settings={
          selectedProvider === 'doubao' ? doubaoSettings : 
          selectedProvider === 'siliconflow' ? siliconflowSettings : 
          selectedProvider === 'cerebras' ? cerebrasSettings : 
          selectedProvider === 'groq' ? groqSettings : 
          selectedProvider === 'mistral' ? mistralSettings : 
          deepseekSettings
        }
        onSettingsChange={(newSettings) => {
          if (selectedProvider === 'doubao') {
            setDoubaoSettings(newSettings as DoubaoSettings);
          } else if (selectedProvider === 'siliconflow') {
            setSiliconflowSettings(newSettings as SiliconFlowSettings);
          } else if (selectedProvider === 'cerebras') {
            setCerebrasSettings(newSettings as CerebrasSettings);
          } else if (selectedProvider === 'groq') {
            setGroqSettings(newSettings as GroqSettings);
          } else if (selectedProvider === 'mistral') {
            setMistralSettings(newSettings as MistralSettings);
          } else {
            setDeepseekSettings(newSettings as DeepSeekSettings);
          }
        }}
      />
    </div>
  );
}

export default App;
