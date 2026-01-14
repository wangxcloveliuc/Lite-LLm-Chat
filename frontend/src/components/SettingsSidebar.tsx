import React, { useRef } from 'react';
import type { DeepSeekSettings, DoubaoSettings, DoubaoSeedreamSettings, SiliconFlowSettings, CerebrasSettings, GroqSettings, GrokSettings, OpenRouterSettings, MistralSettings, GeminiSettings } from '../types';
import { useSidebarDismiss } from './settingsSidebar/useSidebarDismiss';
import ProviderSpecificSettings from './settingsSidebar/ProviderSpecificSettings';
import VisionSettingsSection from './settingsSidebar/VisionSettingsSection';
import CommonSettingsSection from './settingsSidebar/CommonSettingsSection';

type SettingsUnion = DeepSeekSettings | DoubaoSettings | DoubaoSeedreamSettings | SiliconFlowSettings | CerebrasSettings | GroqSettings | GrokSettings | OpenRouterSettings | MistralSettings | GeminiSettings;

interface SettingsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  provider: string;
  modelId: string;
  settings: SettingsUnion;
  onSettingsChange: (settings: SettingsUnion) => void;
}

const SettingsSidebar: React.FC<SettingsSidebarProps> = ({
  isOpen,
  onClose,
  provider,
  modelId,
  settings,
  onSettingsChange,
}) => {
  const sidebarRef = useRef<HTMLDivElement>(null);

  useSidebarDismiss(isOpen, sidebarRef, onClose);

  if (!isOpen) return null;

  const isDeepSeek = provider === 'deepseek';
  const isDoubao = provider === 'doubao';
  const isSiliconFlow = provider === 'siliconflow';
  const isCerebras = provider === 'cerebras';
  const isGroq = provider === 'groq';
  const isGrok = provider === 'grok';
  const isOpenRouter = provider === 'openrouter';
  const isMistral = provider === 'mistral';
  const isGemini = provider === 'gemini';
  const isSeedream = isDoubao && modelId.toLowerCase().includes('seedream');

  const handleChange = (field: string, value: unknown) => {
    onSettingsChange({
      ...settings,
      [field]: value,
    });
  };
  const deepseekSettings = settings as DeepSeekSettings;

  return (
    <div className="settings-sidebar" ref={sidebarRef}>
      <div className="sidebar-header">
        <div className="flex items-center justify-between" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', padding: '0 8px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600' }}>Settings</h2>
          <button 
            onClick={onClose}
            className="close-button"
            style={{ 
              background: 'none', 
              border: 'none', 
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '4px'
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="settings-content" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {isSeedream ? (
          <ProviderSpecificSettings provider={provider} modelId={modelId} settings={settings} handleChange={handleChange} />
        ) : isDeepSeek || isDoubao || isSiliconFlow || isCerebras || isGroq || isGrok || isOpenRouter || isMistral || isGemini ? (
          <>
            <ProviderSpecificSettings provider={provider} modelId={modelId} settings={settings} handleChange={handleChange} />

            {((!isCerebras && !isDeepSeek && !isGroq && !isGrok && !isOpenRouter && !isMistral && !isGemini) || (isGroq && (modelId.toLowerCase().includes('scout') || modelId.toLowerCase().includes('maverick')))) && (
              <VisionSettingsSection settings={deepseekSettings} handleChange={handleChange} />
            )}
            <CommonSettingsSection 
              settings={settings} 
              deepseekSettings={deepseekSettings} 
              isCerebras={isCerebras} 
              modelId={modelId}
              handleChange={handleChange} 
            />
          </>
        ) : (
          <div style={{ textAlign: 'center', color: '#6B7280', marginTop: '40px' }}>
            <p>No special settings for this provider.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsSidebar;
