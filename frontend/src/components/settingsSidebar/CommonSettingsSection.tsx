import React from 'react';
import type {
  DeepSeekSettings,
  DoubaoSettings,
  SiliconFlowSettings,
  CerebrasSettings,
  GroqSettings,
  GrokSettings,
  OpenRouterSettings,
  MistralSettings,
} from '../../types';

type SettingsUnion = DeepSeekSettings | DoubaoSettings | SiliconFlowSettings | CerebrasSettings | GroqSettings | GrokSettings | OpenRouterSettings | MistralSettings;

type HandleChange = (field: string, value: unknown) => void;

interface CommonSettingsSectionProps {
  settings: SettingsUnion;
  deepseekSettings: DeepSeekSettings;
  isCerebras: boolean;
  modelId: string;
  handleChange: HandleChange;
}

const CommonSettingsSection: React.FC<CommonSettingsSectionProps> = ({
  settings,
  deepseekSettings,
  isCerebras,
  modelId,
  handleChange,
}) => {
  const isReasoningModel = modelId.toLowerCase().includes('reasoning') || 
                           modelId.toLowerCase().startsWith('o1-') || 
                           modelId.toLowerCase().startsWith('o3-');

  return (
    <>
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

      {!isCerebras && !isReasoningModel && (
        <>
          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Frequency Penalty ({deepseekSettings.frequency_penalty})
            </label>
            <input
              type="range"
              min="-2"
              max="2"
              step="0.1"
              value={deepseekSettings.frequency_penalty}
              onChange={(e) => handleChange('frequency_penalty', parseFloat(e.target.value))}
              style={{ width: '100%' }}
            />
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Penalizes new tokens based on their frequency in the text so far.
            </p>
          </div>

          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Presence Penalty ({deepseekSettings.presence_penalty})
            </label>
            <input
              type="range"
              min="-2"
              max="2"
              step="0.1"
              value={deepseekSettings.presence_penalty}
              onChange={(e) => handleChange('presence_penalty', parseFloat(e.target.value))}
              style={{ width: '100%' }}
            />
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Penalizes new tokens based on whether they appear in the text so far.
            </p>
          </div>
        </>
      )}

      {isReasoningModel && (
        <div style={{ padding: '8px', backgroundColor: '#FEF2F2', borderRadius: '4px', border: '1px solid #FEE2E2', marginBottom: '16px' }}>
          <p style={{ fontSize: '12px', color: '#991B1B' }}>
            Note: Frequency and Presence penalties are typically not supported by reasoning models.
          </p>
        </div>
      )}

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
  );
};

export default CommonSettingsSection;
