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

interface ProviderSpecificSettingsProps {
  provider: string;
  modelId: string;
  settings: SettingsUnion;
  handleChange: HandleChange;
}

const ProviderSpecificSettings: React.FC<ProviderSpecificSettingsProps> = ({
  provider,
  modelId,
  settings,
  handleChange,
}) => {
  const isDoubao = provider === 'doubao';
  const isSiliconFlow = provider === 'siliconflow';
  const isCerebras = provider === 'cerebras';
  const isGroq = provider === 'groq';
  const isGrok = provider === 'grok';
  const isOpenRouter = provider === 'openrouter';
  const isMistral = provider === 'mistral';

  const doubaoSettings = settings as DoubaoSettings;
  const siliconflowSettings = settings as SiliconFlowSettings;
  const cerebrasSettings = settings as CerebrasSettings;
  const groqSettings = settings as GroqSettings;
  const openrouterSettings = settings as OpenRouterSettings;
  const mistralSettings = settings as MistralSettings;

  if (!isDoubao && !isSiliconFlow && !isCerebras && !isGroq && !isGrok && !isOpenRouter && !isMistral) return null;

  return (
    <>
      {isOpenRouter && (
        <>
          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Transforms
            </label>
            <input
              type="text"
              placeholder="e.g. middle-out"
              value={openrouterSettings.transforms || ''}
              onChange={(e) => handleChange('transforms', e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
            />
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Comma-separated list of transforms to apply.
            </p>
          </div>

          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Fallback Models
            </label>
            <input
              type="text"
              placeholder="e.g. gpt-4o, claude-3-opus"
              value={openrouterSettings.models || ''}
              onChange={(e) => handleChange('models', e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
            />
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Comma-separated list of models to use as fallbacks.
            </p>
          </div>

          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Routing Preference
            </label>
            <select
              value={openrouterSettings.route || ''}
              onChange={(e) => handleChange('route', e.target.value || undefined)}
              style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
            >
              <option value="">Default</option>
              <option value="fallback">Fallback</option>
              <option value="sort">Sort</option>
            </select>
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Specify routing behavior for this request.
            </p>
          </div>
        </>
      )}

      {isGrok && (
        <div className="setting-group">
          <p style={{ fontSize: '13px', color: '#6B7280', fontStyle: 'italic' }}>
            Grok models utilize standard OpenAI-compatible parameters. Specific models like <strong>grok-4-fast-reasoning</strong> may ignore or reject certain parameters like presence_penalty.
          </p>
        </div>
      )}

      {isMistral && (
        <>
          <div className="setting-group">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
                Safe Prompt
              </label>
              <input
                type="checkbox"
                checked={mistralSettings.safe_prompt || false}
                onChange={(e) => handleChange('safe_prompt', e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Inject a safety prompt before the conversation.
            </p>
          </div>

          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Random Seed
            </label>
            <input
              type="number"
              placeholder="None"
              value={mistralSettings.random_seed !== undefined ? mistralSettings.random_seed : ''}
              onChange={(e) => {
                const val = e.target.value === '' ? undefined : parseInt(e.target.value);
                handleChange('random_seed', val);
              }}
              style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
            />
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Set a seed for deterministic results.
            </p>
          </div>
        </>
      )}

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

      {isCerebras && (
        <>
          {(modelId.toLowerCase().includes('gpt-oss')) && (
            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Reasoning Effort
              </label>
              <select
                value={cerebrasSettings.reasoning_effort || 'medium'}
                onChange={(e) => handleChange('reasoning_effort', e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Adjust the depth of reasoning process (gpt-oss models only).
              </p>
            </div>
          )}

          {(modelId.toLowerCase().includes('zai')) && (
            <div className="setting-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
                  Disable Reasoning
                </label>
                <input
                  type="checkbox"
                  checked={cerebrasSettings.disable_reasoning || false}
                  onChange={(e) => handleChange('disable_reasoning', e.target.checked)}
                  style={{ cursor: 'pointer' }}
                />
              </div>
              <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                Disable reasoning for zai models.
              </p>
            </div>
          )}
        </>
      )}

      {isGroq && (
        <>
          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Reasoning Effort
            </label>
            <select
              value={groqSettings.reasoning_effort || 'default'}
              onChange={(e) => handleChange('reasoning_effort', e.target.value)}
              style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
            >
              {modelId.toLowerCase().includes('qwen') ? (
                <>
                  <option value="none">None (Disable Reasoning)</option>
                  <option value="default">Default</option>
                </>
              ) : (
                <>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </>
              )}
            </select>
          </div>

          {!modelId.toLowerCase().includes('gpt-oss') && (
            <div className="setting-group">
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
                Reasoning Format
              </label>
              <select
                value={groqSettings.reasoning_format || 'parsed'}
                onChange={(e) => {
                  const val = e.target.value;
                  handleChange('reasoning_format', val);
                  if (val !== '') {
                    handleChange('include_reasoning', undefined);
                  }
                }}
                style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
              >
                <option value="parsed">Parsed (Dedicated field)</option>
                <option value="raw">Raw (In text with &lt;think&gt;)</option>
                <option value="hidden">Hidden</option>
              </select>
            </div>
          )}

          {modelId.toLowerCase().includes('gpt-oss') && (
            <div className="setting-group">
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
                  Include Reasoning
                </label>
                <input
                  type="checkbox"
                  checked={groqSettings.include_reasoning ?? true}
                  onChange={(e) => {
                    handleChange('include_reasoning', e.target.checked);
                    handleChange('reasoning_format', undefined);
                  }}
                  style={{ cursor: 'pointer' }}
                />
              </div>
            </div>
          )}

          <div className="setting-group">
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
              Max Completion Tokens
            </label>
            <input
              type="number"
              placeholder="1024"
              value={groqSettings.max_completion_tokens || ''}
              onChange={(e) => {
                const val = e.target.value === '' ? undefined : parseInt(e.target.value);
                handleChange('max_completion_tokens', val);
              }}
              style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
            />
            <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
              Recommended for reasoning models.
            </p>
          </div>
        </>
      )}
    </>
  );
};

export default ProviderSpecificSettings;
