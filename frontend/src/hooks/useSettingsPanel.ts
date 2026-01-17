import { useState, useCallback } from 'react';

type UseSettingsPanelParams = {
  selectedProvider: string;
  loadModels: (provider: string) => Promise<void>;
};

type UseSettingsPanelReturn = {
  showSettings: boolean;
  handleToggleSettings: () => Promise<void>;
  handleCloseSettings: () => void;
};

const useSettingsPanel = ({ selectedProvider, loadModels }: UseSettingsPanelParams): UseSettingsPanelReturn => {
  const [showSettings, setShowSettings] = useState(false);

  const handleToggleSettings = useCallback(async () => {
    if (!showSettings && selectedProvider) {
      await loadModels(selectedProvider);
    }
    setShowSettings((prev) => !prev);
  }, [loadModels, selectedProvider, showSettings]);

  const handleCloseSettings = useCallback(() => {
    setShowSettings(false);
  }, []);

  return {
    showSettings,
    handleToggleSettings,
    handleCloseSettings,
  };
};

export default useSettingsPanel;
