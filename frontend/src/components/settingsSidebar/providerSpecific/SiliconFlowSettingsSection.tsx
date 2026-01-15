import type { SiliconFlowSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type SiliconFlowSettingsSectionProps = {
  settings: SiliconFlowSettings;
  handleChange: HandleChange;
};

const SiliconFlowSettingsSection = ({ settings, handleChange }: SiliconFlowSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Enable Thinking
        </label>
        <select
          value={settings.enable_thinking === undefined ? 'default' : (settings.enable_thinking ? 'enabled' : 'disabled')}
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
        Thinking Budget ({settings.thinking_budget || 4096})
      </label>
      <input
        type="number"
        min="128"
        max="32768"
        value={settings.thinking_budget || ''}
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
        Min P ({settings.min_p !== undefined ? settings.min_p : 'Default'})
      </label>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={settings.min_p !== undefined ? settings.min_p : 0}
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
        Top K ({settings.top_k !== undefined ? settings.top_k : 'Default'})
      </label>
      <input
        type="number"
        placeholder="None"
        value={settings.top_k !== undefined ? settings.top_k : ''}
        onChange={(e) => {
          const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
          handleChange('top_k', val);
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
    </div>
  </>
);

export default SiliconFlowSettingsSection;
