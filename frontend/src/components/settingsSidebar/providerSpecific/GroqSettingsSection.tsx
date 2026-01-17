import type { GroqSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type GroqSettingsSectionProps = {
  settings: GroqSettings;
  modelId: string;
  handleChange: HandleChange;
};

const GroqSettingsSection = ({ settings, modelId, handleChange }: GroqSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Reasoning Effort
      </label>
      <select
        value={settings.reasoning_effort || 'default'}
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
          value={settings.reasoning_format || 'parsed'}
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
            checked={settings.include_reasoning ?? true}
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
        value={settings.max_completion_tokens || ''}
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
);

export default GroqSettingsSection;
