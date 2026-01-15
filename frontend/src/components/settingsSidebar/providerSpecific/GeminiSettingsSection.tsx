import type { GeminiSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type GeminiSettingsSectionProps = {
  settings: GeminiSettings;
  handleChange: HandleChange;
};

const GeminiSettingsSection = ({ settings, handleChange }: GeminiSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Thinking Budget ({settings.thinking_budget || 'Auto'})
      </label>
      <input
        type="number"
        placeholder="e.g. 16000"
        value={settings.thinking_budget || ''}
        onChange={(e) => {
          const val = e.target.value === '' ? undefined : parseInt(e.target.value);
          handleChange('thinking_budget', val);
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Maximum thinking budget in bytes. Only for thinking models (e.g., flash-thinking).
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Safety Threshold
      </label>
      <select
        value={settings.safety_threshold || 'BLOCK_NONE'}
        onChange={(e) => handleChange('safety_threshold', e.target.value)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="BLOCK_NONE">Block None</option>
        <option value="BLOCK_LOW_AND_ABOVE">Block Low and Above</option>
        <option value="BLOCK_MED_AND_ABOVE">Block Medium and Above</option>
        <option value="BLOCK_ONLY_HIGH">Block Only High</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Global safety filter threshold for all categories.
      </p>
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
          const val = e.target.value === '' ? undefined : parseInt(e.target.value);
          handleChange('top_k', val);
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Seed
      </label>
      <input
        type="number"
        placeholder="None"
        value={settings.seed !== undefined ? settings.seed : ''}
        onChange={(e) => {
          const val = e.target.value === '' ? undefined : parseInt(e.target.value);
          handleChange('seed', val);
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
    </div>
  </>
);

export default GeminiSettingsSection;
