import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/apiClient';
import type { Provider, Model, Session } from '../types';

type UseChatResourcesReturn = {
  providers: Provider[];
  models: Model[];
  sessions: Session[];
  selectedProvider: string;
  selectedModel: string;
  currentSessionId: number | null;
  setCurrentSessionId: (sessionId: number | null) => void;
  loadModels: (provider: string) => Promise<void>;
  loadSessions: () => Promise<void>;
  handleProviderChange: (providerId: string) => void;
  handleModelChange: (modelId: string) => void;
  fetchSession: (sessionId: number) => Promise<Session | null>;
  applySession: (session: Session) => void;
  resetSession: () => void;
  handleRenameSession: (sessionId: number, newTitle: string) => Promise<boolean>;
  handleDeleteSession: (sessionId: number) => Promise<boolean>;
};

const useChatResources = (): UseChatResourcesReturn => {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');

  const loadProviders = useCallback(async () => {
    const data = await apiClient.getProviders();
    setProviders(data);
    if (data.length > 0 && !selectedProvider) {
      setSelectedProvider(data[0].id);
    }
  }, [selectedProvider]);

  const loadModels = useCallback(
    async (provider: string) => {
      const data = await apiClient.getModels(provider);
      setModels(data);
      if (data.length > 0 && !selectedModel) {
        setSelectedModel(data[0].id);
      }
    },
    [selectedModel],
  );

  const loadSessions = useCallback(async () => {
    const data = await apiClient.getSessions();
    setSessions(data);
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      void loadProviders();
      void loadSessions();
    });
  }, [loadProviders, loadSessions]);

  useEffect(() => {
    if (selectedProvider) {
      queueMicrotask(() => {
        void loadModels(selectedProvider);
      });
    }
  }, [loadModels, selectedProvider]);

  const handleProviderChange = useCallback((providerId: string) => {
    setSelectedProvider(providerId);
    setSelectedModel('');
  }, []);

  const handleModelChange = useCallback((modelId: string) => {
    setSelectedModel(modelId);
  }, []);

  const fetchSession = useCallback(async (sessionId: number) => {
    return apiClient.getSession(sessionId);
  }, []);

  const applySession = useCallback((session: Session) => {
    setCurrentSessionId(session.id);
    setSelectedProvider(session.provider);
    setSelectedModel(session.model);
  }, []);

  const resetSession = useCallback(() => {
    setCurrentSessionId(null);
  }, []);

  const handleRenameSession = useCallback(
    async (sessionId: number, newTitle: string) => {
      const success = await apiClient.updateSession(sessionId, newTitle);
      if (success) {
        loadSessions();
      }
      return success;
    },
    [loadSessions],
  );

  const handleDeleteSession = useCallback(
    async (sessionId: number) => {
      const success = await apiClient.deleteSession(sessionId);
      if (success) {
        loadSessions();
      }
      return success;
    },
    [loadSessions],
  );

  return {
    providers,
    models,
    sessions,
    selectedProvider,
    selectedModel,
    currentSessionId,
    setCurrentSessionId,
    loadModels,
    loadSessions,
    handleProviderChange,
    handleModelChange,
    fetchSession,
    applySession,
    resetSession,
    handleRenameSession,
    handleDeleteSession,
  };
};

export default useChatResources;
