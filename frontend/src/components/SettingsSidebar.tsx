import React, { useEffect, useRef } from 'react';
import type { DeepSeekSettings, DoubaoSettings, SiliconFlowSettings } from '../types';

interface SettingsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  provider: string;
  modelId: string;
  settings: DeepSeekSettings | DoubaoSettings | SiliconFlowSettings;
  onSettingsChange: (settings: any) => void;
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

  const isDeepSeek = provider === 'deepseek';
  const isDoubao = provider === 'doubao';
  const isSiliconFlow = provider === 'siliconflow';

  const handleChange = (field: string, value: any) => {
    onSettingsChange({
      ...settings,
      [field]: value,
    });
  };

  const doubaoSettings = settings as DoubaoSettings;
  const siliconflowSettings = settings as SiliconFlowSettings;

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
        {isDeepSeek || isDoubao || isSiliconFlow ? (
          <>
            {isDoubao && (
              <>
                <div className="setting-group">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
                      Thinking Mode
                    </label>
                    <select
                      value={doubaoSettings.thinking === undefined ? 'default' : (doubaoSettings.thinking ? 'enabled' : 'disabled')}
                      onChange={(e) => {
                        const val = e.target.value;
                        handleChange('thinking', val === 'default' ? undefined : val === 'enabled');
                      }}
                      style={{ padding: '4px 8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
                    >
                      <option value="default">Default</option>
                      <option value="enabled">Enabled</option>
                      <option value="disabled">Disabled</option>
                    </select>
                  </div>
                  <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                    Enable deep reasoning for supported models.
                  </p>
                </div>

                <div className="setting-group">
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                    Reasoning Effort
                  </label>
                  <select
                    value={doubaoSettings.reasoning_effort || 'medium'}
                    onChange={(e) => handleChange('reasoning_effort', e.target.value)}
                    style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                  <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                    Adjust the depth of reasoning process.
                  </p>
                </div>

                <div className="setting-group">
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                    Max Completion Tokens
                  </label>
                  <input
                    type="number"
                    placeholder="Unlimited"
                    value={doubaoSettings.max_completion_tokens || ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? undefined : parseInt(e.target.value);
                      handleChange('max_completion_tokens', val);
                    }}
                    style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
                  />
                  <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                    Maximum tokens allowed for the reasoning and response combined.
                  </p>
                </div>
              </>
            )}

            {isSiliconFlow && (
              <>
                <div className="setting-group">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
                      Enable Thinking
                    </label>
                    <select
                      value={siliconflowSettings.enable_thinking === undefined ? 'default' : (siliconflowSettings.enable_thinking ? 'enabled' : 'disabled')}
                      onChange={(e) => {
                        const val = e.target.value;
                        handleChange('enable_thinking', val === 'default' ? undefined : val === 'enabled');
                      }}
                      style={{ padding: '4px 8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
                    >
                      <option value="default">Default</option>
                      <option value="enabled">Enabled</option>
                      <option value="disabled">Disabled</option>
                    </select>
                  </div>
                  <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                    Enable chain-of-thought for reasoning models.
                  </p>
                </div>

                <div className="setting-group">
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                    Thinking Budget ({siliconflowSettings.thinking_budget || 4096})
                  </label>
                  <input
                    type="number"
                    min="128"
                    max="32768"
                    value={siliconflowSettings.thinking_budget || ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? undefined : parseInt(e.target.value);
                      handleChange('thinking_budget', val);
                    }}
                    style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
                  />
                  <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                    Max tokens for chain-of-thought (128 - 32768).
                  </p>
                </div>

                <div className="setting-group">
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                    Min P ({siliconflowSettings.min_p !== undefined ? siliconflowSettings.min_p : 'Default'})
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={siliconflowSettings.min_p !== undefined ? siliconflowSettings.min_p : 0}
                    onChange={(e) => handleChange('min_p', parseFloat(e.target.value))}
                    style={{ width: '100%' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                    <p style={{ fontSize: '12px', color: '#6B7280' }}>
                      Dynamic filtering threshold (Qwen3 only).
                    </p>
                    <button 
                      onClick={() => handleChange('min_p', undefined)}
                      style={{ fontSize: '10px', background: '#F3F4F6', border: 'none', padding: '2px 6px', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      Reset
                    </button>
                  </div>
                </div>

                <div className="setting-group">
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                    Top K ({siliconflowSettings.top_k !== undefined ? siliconflowSettings.top_k : 'Default'})
                  </label>
                  <input
                    type="number"
                    placeholder="None"
                    value={siliconflowSettings.top_k !== undefined ? siliconflowSettings.top_k : ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
                      handleChange('top_k', val);
                    }}
                    style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
                  />
                </div>
              </>
            )}

            <div className="setting-group" style={{ borderTop: '1px solid #F3F4F6', paddingTop: '16px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#374151' }}>Vision Settings</h3>
              <div className="setting-item" style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                  Image Detail
                </label>
                <select
                  value={settings.image_detail || 'auto'}
                  onChange={(e) => handleChange('image_detail', e.target.value)}
                  style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
                >
                  <option value="auto">Auto</option>
                  <option value="low">Low</option>
                  <option value="high">High</option>
                </select>
                <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                  Control the level of detail used for images.
                </p>
              </div>

              <div className="setting-item">
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                  Image Pixel Limit
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="number"
                    placeholder="Max Pixels"
                    value={settings.image_pixel_limit?.max_pixels || ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? undefined : parseInt(e.target.value);
                      handleChange('image_pixel_limit', {
                        ...settings.image_pixel_limit,
                        max_pixels: val
                      });
                    }}
                    style={{ width: '50%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
                  />
                  <input
                    type="number"
                    placeholder="Min Pixels"
                    value={settings.image_pixel_limit?.min_pixels || ''}
                    onChange={(e) => {
                      const val = e.target.value === '' ? undefined : parseInt(e.target.value);
                      handleChange('image_pixel_limit', {
                        ...settings.image_pixel_limit,
                        min_pixels: val
                      });
                    }}
                    style={{ width: '50%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
                  />
                </div>
                <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                  Set max/min pixels for image processing.
                </p>
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
                Max Tokens
              </label>
              <input
                type="number"
                min="1"
                placeholder="Unlimited"
                value={settings.max_tokens || ''}
                onChange={(e) => {
                  const val = e.target.value === '' ? undefined : parseInt(e.target.value);
                  handleChange('max_tokens', val);
                }}
                style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
              />
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
