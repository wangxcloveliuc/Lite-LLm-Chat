import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import SettingsSidebar from './components/SettingsSidebar';
import useChatApp from './hooks/useChatApp';
import './App.css';

function App() {
  const {
    providers,
    models,
    sessions,
    currentSessionId,
    messages,
    selectedProvider,
    selectedModel,
    isLoading,
    showSettings,
    activeSettings,
    handleToggleSettings,
    handleCloseSettings,
    handleNewChat,
    handleSessionSelect,
    handleRenameSession,
    handleDeleteSession,
    handleProviderChange,
    handleModelChange,
    handleSendMessage,
    handleStopGeneration,
    handleEditMessage,
    handleRefreshMessage,
    handleSettingsChange,
  } = useChatApp();

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
        onClose={handleCloseSettings}
        provider={selectedProvider}
        modelId={selectedModel}
        settings={activeSettings}
        onSettingsChange={handleSettingsChange}
      />
    </div>
  );
}

export default App;
