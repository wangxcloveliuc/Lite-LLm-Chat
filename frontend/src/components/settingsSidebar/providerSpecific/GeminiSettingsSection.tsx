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
        Thinking Level
      </label>
      <select
        value={settings.thinking_level || 'high'}
        onChange={(e) => handleChange('thinking_level', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="minimal">Minimal (Flash only)</option>
        <option value="low">Low</option>
        <option value="medium">Medium (Flash only)</option>
        <option value="high">High (Default)</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Controls Gemini 3 reasoning depth. Flash supports minimal/medium; Pro supports low/high.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Media Resolution
      </label>
      <select
        value={settings.media_resolution || 'MEDIA_RESOLUTION_UNSPECIFIED'}
        onChange={(e) => handleChange('media_resolution', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="MEDIA_RESOLUTION_UNSPECIFIED">Unspecified</option>
        <option value="MEDIA_RESOLUTION_LOW">Low</option>
        <option value="MEDIA_RESOLUTION_MEDIUM">Medium</option>
        <option value="MEDIA_RESOLUTION_HIGH">High</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Default resolution for media inputs (Gemini 3 models).
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
