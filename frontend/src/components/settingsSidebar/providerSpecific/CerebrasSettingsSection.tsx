import type { CerebrasSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type CerebrasSettingsSectionProps = {
  settings: CerebrasSettings;
  modelId: string;
  handleChange: HandleChange;
};

const CerebrasSettingsSection = ({ settings, modelId, handleChange }: CerebrasSettingsSectionProps) => (
  <>
    {modelId.toLowerCase().includes('gpt-oss') && (
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
          Adjust the depth of reasoning process (gpt-oss models only).
        </p>
      </div>
    )}

    {modelId.toLowerCase().includes('zai') && (
      <div className="setting-group">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
            Disable Reasoning
          </label>
          <input
            type="checkbox"
            checked={settings.disable_reasoning || false}
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
);

export default CerebrasSettingsSection;
