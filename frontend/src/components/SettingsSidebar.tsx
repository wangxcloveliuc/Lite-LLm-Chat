import React, { useEffect, useRef } from 'react';
import type { DeepSeekSettings } from '../types';

interface SettingsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  provider: string;
  modelId: string;
  settings: DeepSeekSettings;
  onSettingsChange: (settings: DeepSeekSettings) => void;
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

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isOpen && sidebarRef.current && !sidebarRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEsc = (event: KeyboardEvent) => {
      if (isOpen && event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEsc);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEsc);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isThinkingModel = (modelId || '') === 'deepseek-reasoner';
  const maxTokensLimit = isThinkingModel ? 65536 : 8192;
  const defaultTokens = isThinkingModel ? 32768 : 4096;
  const contextLength = "128K";

  const handleChange = (field: keyof DeepSeekSettings, value: any) => {
    onSettingsChange({
      ...settings,
      [field]: value,
    });
  };

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
        {provider === 'deepseek' ? (
          <>
            <div className="provider-info" style={{ marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '600', color: '#6B7280', textTransform: 'uppercase' }}>
                  DeepSeek {isThinkingModel ? 'Reasoner' : 'Chat'}
                </h3>
                <span style={{ fontSize: '12px', background: '#E5E7EB', padding: '2px 6px', borderRadius: '4px', color: '#374151' }}>
                  {contextLength} Context
                </span>
              </div>
            </div>

            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                System Prompt
              </label>
              <textarea
                placeholder="Enter a system prompt to guide the assistant's behavior..."
                value={settings.system_prompt}
                onChange={(e) => handleChange('system_prompt', e.target.value)}
                rows={4}
                style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', resize: 'vertical', fontFamily: 'inherit', fontSize: '14px' }}
              />
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Define how the assistant should behave and respond.
              </p>
            </div>

            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Temperature ({settings.temperature})
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={settings.temperature}
                onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Higher values make output more random, lower values more deterministic.
              </p>
            </div>

            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Max Tokens (Max: {maxTokensLimit / 1024}K)
              </label>
              <input
                type="number"
                min="1"
                max={maxTokensLimit}
                value={settings.max_tokens}
                onChange={(e) => {
                  let val = parseInt(e.target.value) || 0;
                  if (val > maxTokensLimit) val = maxTokensLimit;
                  handleChange('max_tokens', val);
                }}
                style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
              />
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Default is {defaultTokens / 1024}K tokens for this model.
              </p>
            </div>

            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Top P ({settings.top_p})
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={settings.top_p}
                onChange={(e) => handleChange('top_p', parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Nucleus sampling: model considers tokens with top_p probability mass.
              </p>
            </div>

            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Frequency Penalty ({settings.frequency_penalty})
              </label>
              <input
                type="range"
                min="-2"
                max="2"
                step="0.1"
                value={settings.frequency_penalty}
                onChange={(e) => handleChange('frequency_penalty', parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Penalizes new tokens based on their frequency in the text so far.
              </p>
            </div>

            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Presence Penalty ({settings.presence_penalty})
              </label>
              <input
                type="range"
                min="-2"
                max="2"
                step="0.1"
                value={settings.presence_penalty}
                onChange={(e) => handleChange('presence_penalty', parseFloat(e.target.value))}
                style={{ width: '100%' }}
              />
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Penalizes new tokens based on whether they appear in the text so far.
              </p>
            </div>

            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Stop Sequences
              </label>
              <input
                type="text"
                placeholder="Comma separated sequences..."
                value={settings.stop}
                onChange={(e) => handleChange('stop', e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
              />
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Model will stop generating if these sequences are encountered.
              </p>
            </div>
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
