import type { DoubaoSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type DoubaoSettingsSectionProps = {
  settings: DoubaoSettings;
  modelId: string;
  handleChange: HandleChange;
};

const DoubaoSettingsSection = ({ settings, modelId, handleChange }: DoubaoSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Thinking Mode
        </label>
        <select
          value={settings.thinking === undefined ? 'default' : (settings.thinking ? 'enabled' : 'disabled')}
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

    {!modelId.toLowerCase().includes('seed-code-preview') && (
      <div className="setting-group">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Reasoning Effort
        </label>
        <select
          value={settings.reasoning_effort || 'medium'}
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
    )}

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Max Completion Tokens
      </label>
      <input
        type="number"
        placeholder="Unlimited"
        value={settings.max_completion_tokens || ''}
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
);

export default DoubaoSettingsSection;
