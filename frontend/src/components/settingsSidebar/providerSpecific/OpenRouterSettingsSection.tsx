import type { OpenRouterSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type OpenRouterSettingsSectionProps = {
  settings: OpenRouterSettings;
  handleChange: HandleChange;
};

const OpenRouterSettingsSection = ({ settings, handleChange }: OpenRouterSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Transforms
      </label>
      <input
        type="text"
        placeholder="e.g. middle-out"
        value={settings.transforms || ''}
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
        value={settings.models || ''}
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
        value={settings.route || ''}
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
);

export default OpenRouterSettingsSection;
