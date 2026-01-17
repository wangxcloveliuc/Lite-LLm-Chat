import { useState, useCallback } from 'react';
import { apiClient } from '../api/apiClient';
import type { Message, ChatRequest, SearchResult } from '../types';
import type { ChatRequestSettings } from './useChatSettings';

type UseChatMessagesParams = {
  selectedProvider: string;
  selectedModel: string;
  currentSessionId: number | null;
  setCurrentSessionId: (sessionId: number | null) => void;
  loadSessions: () => Promise<void>;
  getCurrentSettings: () => ChatRequestSettings;
};

type UseChatMessagesReturn = {
  messages: Message[];
  isLoading: boolean;
  handleSendMessage: (content: string, imageUrls?: string[], videoUrls?: string[], audioUrls?: string[]) => Promise<void>;
  handleStopGeneration: () => void;
  handleEditMessage: (index: number, content: string) => Promise<void>;
  handleRefreshMessage: (index: number) => Promise<void>;
  resetMessages: () => void;
  applySessionMessages: (messages?: Message[]) => void;
};

const useChatMessages = ({
  selectedProvider,
  selectedModel,
  currentSessionId,
  setCurrentSessionId,
  loadSessions,
  getCurrentSettings,
}: UseChatMessagesParams): UseChatMessagesReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const isGeminiImagen = selectedProvider === 'gemini' && selectedModel.toLowerCase().startsWith('imagen-');

  const handleStopGeneration = useCallback(() => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsLoading(false);
    }
  }, [abortController]);

  const refreshMessages = useCallback(async (sessionId: number) => {
    const session = await apiClient.getSession(sessionId);
    if (session?.messages) {
      setMessages(session.messages);
    }
  }, []);

  const handleSendMessage = useCallback(
    async (content: string, imageUrls?: string[], videoUrls?: string[], audioUrls?: string[]) => {
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

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setIsLoading(true);
      const controller = new AbortController();
      setAbortController(controller);

      let newSessionId = currentSessionId;
      const currentSettings = getCurrentSettings();
      let parsedResponseFormat: Record<string, unknown> | undefined;
      if (currentSettings.response_format) {
        try {
          parsedResponseFormat = JSON.parse(currentSettings.response_format);
        } catch (error) {
          console.warn('Invalid response_format JSON. Skipping.', error);
        }
      }
      const reasoningConfig: Record<string, unknown> | undefined =
        currentSettings.reasoning_effort || currentSettings.reasoning_summary
          ? {
              effort: currentSettings.reasoning_effort,
              summary: currentSettings.reasoning_summary,
            }
          : undefined;
      const imageConfig =
        currentSettings.image_aspect_ratio || currentSettings.image_size
          ? {
              aspect_ratio: currentSettings.image_aspect_ratio,
              image_size: currentSettings.image_size,
            }
          : undefined;
      const webSearchPlugin = currentSettings.web_search
        ? {
            id: 'web',
            ...(currentSettings.web_search_engine ? { engine: currentSettings.web_search_engine } : {}),
            ...(currentSettings.web_search_results ? { max_results: currentSettings.web_search_results } : {}),
            ...(currentSettings.web_search_prompt ? { search_prompt: currentSettings.web_search_prompt } : {}),
          }
        : undefined;
      const plugins = webSearchPlugin ? [webSearchPlugin] : undefined;
      const webSearchOptions = currentSettings.web_search_context_size
        ? { search_context_size: currentSettings.web_search_context_size }
        : undefined;

      try {
        const request: ChatRequest = {
          provider: selectedProvider,
          model: selectedModel,
          messages: [{ role: 'user', content, images: imageUrls, videos: videoUrls, audios: audioUrls }],
          stream: !isGeminiImagen,
          session_id: currentSessionId || undefined,
          title: currentSessionId ? undefined : content.substring(0, 50),
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
          safe_prompt: currentSettings.safe_prompt,
          random_seed: currentSettings.random_seed,
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
          transforms: currentSettings.transforms
            ? currentSettings.transforms.split(',').map((s) => s.trim())
            : undefined,
          models: currentSettings.models ? currentSettings.models.split(',').map((s) => s.trim()) : undefined,
          route: currentSettings.route,
          repetition_penalty: currentSettings.repetition_penalty,
          top_a: currentSettings.top_a,
          logprobs: currentSettings.logprobs,
          top_logprobs: currentSettings.top_logprobs,
          response_format: parsedResponseFormat,
          structured_outputs: currentSettings.structured_outputs,
          parallel_tool_calls: currentSettings.parallel_tool_calls,
          reasoning: reasoningConfig,
          modalities: currentSettings.image_generation ? ['image', 'text'] : undefined,
          image_config: imageConfig,
          plugins,
          web_search_options: webSearchOptions,
          seed: currentSettings.seed,
          safety_threshold: currentSettings.safety_threshold,
          sequential_image_generation: currentSettings.sequential_image_generation,
          max_images: currentSettings.max_images,
          watermark: currentSettings.watermark,
          prompt_optimize_mode: currentSettings.prompt_optimize_mode,
          size: currentSettings.size,
          resolution: currentSettings.resolution,
          ratio: currentSettings.ratio,
          duration: currentSettings.duration,
          generate_audio: currentSettings.generate_audio,
          draft: currentSettings.draft,
          camera_fixed: currentSettings.camera_fixed,
          imagen_number_of_images: currentSettings.imagen_number_of_images,
          imagen_image_size: currentSettings.imagen_image_size,
          imagen_aspect_ratio: currentSettings.imagen_aspect_ratio,
          imagen_person_generation: currentSettings.imagen_person_generation,
        };
        if (isGeminiImagen) {
          const response = await apiClient.chat(request);
          if (response?.session_id && !newSessionId) {
            newSessionId = response.session_id;
            setCurrentSessionId(newSessionId);
            loadSessions();
          }
          if (response?.message) {
            setMessages((prev) => {
              const updated = [...prev];
              const lastMsg = updated[updated.length - 1];
              if (lastMsg && lastMsg.role === 'assistant') {
                updated[updated.length - 1] = response.message;
              }
              return updated;
            });
          }
        } else {
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
                    ? incoming
                    : lastMsg.content + incoming;
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

            if (chunk.search_results) {
              const incomingResults = chunk.search_results as SearchResult[];
              setMessages((prev) => {
                const updated = [...prev];
                const lastMsg = updated[updated.length - 1];
                if (lastMsg && lastMsg.role === 'assistant') {
                  const existing = lastMsg.search_results || [];
                  const merged = [...existing, ...incomingResults];
                  updated[updated.length - 1] = { ...lastMsg, search_results: merged };
                }
                return updated;
              });
            }

            if (chunk.error) {
              console.error('Stream error:', chunk.error);
              break;
            }
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
          await refreshMessages(sessionIdToRefresh);
        }
      }
    },
    [
      currentSessionId,
      getCurrentSettings,
      isGeminiImagen,
      loadSessions,
      refreshMessages,
      selectedModel,
      selectedProvider,
      setCurrentSessionId,
    ],
  );

  const handleEditMessage = useCallback(
    async (index: number, content: string) => {
      const messageToEdit = messages[index];
      if (!messageToEdit || messageToEdit.role !== 'user') return;

      if (currentSessionId) {
        handleStopGeneration();

        if (messageToEdit.id) {
          await apiClient.truncateSession(currentSessionId, messageToEdit.id);
        }

        setMessages((prev) => prev.slice(0, index));
        handleSendMessage(content, messageToEdit.images);
      } else {
        handleStopGeneration();
        setMessages((prev) => prev.slice(0, index));
        handleSendMessage(content, messageToEdit.images);
      }
    },
    [currentSessionId, handleSendMessage, handleStopGeneration, messages],
  );

  const handleRefreshMessage = useCallback(
    async (index: number) => {
      const assistantMessage = messages[index];
      if (!assistantMessage || assistantMessage.role !== 'assistant') return;

      const userMessageIndex = index - 1;
      if (userMessageIndex < 0) return;
      const userMessage = messages[userMessageIndex];
      if (!userMessage || userMessage.role !== 'user') return;

      if (currentSessionId) {
        handleStopGeneration();

        if (userMessage.id) {
          await apiClient.truncateSession(currentSessionId, userMessage.id);
        }

        setMessages((prev) => prev.slice(0, userMessageIndex));
        handleSendMessage(userMessage.content, userMessage.images);
      } else {
        handleStopGeneration();
        setMessages((prev) => prev.slice(0, userMessageIndex));
        handleSendMessage(userMessage.content, userMessage.images);
      }
    },
    [currentSessionId, handleSendMessage, handleStopGeneration, messages],
  );

  const resetMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const applySessionMessages = useCallback((sessionMessages?: Message[]) => {
    setMessages(sessionMessages || []);
  }, []);

  return {
    messages,
    isLoading,
    handleSendMessage,
    handleStopGeneration,
    handleEditMessage,
    handleRefreshMessage,
    resetMessages,
    applySessionMessages,
  };
};

export default useChatMessages;
