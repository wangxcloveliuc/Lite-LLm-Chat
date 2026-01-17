import { useCallback } from 'react';
import useChatResources from './useChatResources';
import useChatSettings from './useChatSettings';
import useChatMessages from './useChatMessages';
import useSettingsPanel from './useSettingsPanel';

const useChatApp = () => {
  const resources = useChatResources();
  const settings = useChatSettings({
    selectedProvider: resources.selectedProvider,
    selectedModel: resources.selectedModel,
  });
  const messages = useChatMessages({
    selectedProvider: resources.selectedProvider,
    selectedModel: resources.selectedModel,
    currentSessionId: resources.currentSessionId,
    setCurrentSessionId: resources.setCurrentSessionId,
    loadSessions: resources.loadSessions,
    getCurrentSettings: settings.getCurrentSettings,
  });
  const settingsPanel = useSettingsPanel({
    selectedProvider: resources.selectedProvider,
    loadModels: resources.loadModels,
  });

  const handleNewChat = useCallback(() => {
    resources.resetSession();
    messages.resetMessages();
  }, [messages, resources]);

  const handleSessionSelect = useCallback(
    async (sessionId: number) => {
      const session = await resources.fetchSession(sessionId);
      if (session) {
        resources.applySession(session);
        messages.applySessionMessages(session.messages);
      }
    },
    [messages, resources],
  );

  const handleDeleteSession = useCallback(
    async (sessionId: number) => {
      const success = await resources.handleDeleteSession(sessionId);
      if (success && resources.currentSessionId === sessionId) {
        handleNewChat();
      }
    },
    [handleNewChat, resources],
  );

  return {
    providers: resources.providers,
    models: resources.models,
    sessions: resources.sessions,
    currentSessionId: resources.currentSessionId,
    messages: messages.messages,
    selectedProvider: resources.selectedProvider,
    selectedModel: resources.selectedModel,
    isLoading: messages.isLoading,
    showSettings: settingsPanel.showSettings,
    activeSettings: settings.activeSettings,
    handleToggleSettings: settingsPanel.handleToggleSettings,
    handleCloseSettings: settingsPanel.handleCloseSettings,
    handleNewChat,
    handleSessionSelect,
    handleRenameSession: resources.handleRenameSession,
    handleDeleteSession,
    handleProviderChange: resources.handleProviderChange,
    handleModelChange: resources.handleModelChange,
    handleSendMessage: messages.handleSendMessage,
    handleStopGeneration: messages.handleStopGeneration,
    handleEditMessage: messages.handleEditMessage,
    handleRefreshMessage: messages.handleRefreshMessage,
    handleSettingsChange: settings.handleSettingsChange,
  };
};

export default useChatApp;
