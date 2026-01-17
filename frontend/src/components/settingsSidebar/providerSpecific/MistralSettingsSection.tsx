import type { MistralSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type MistralSettingsSectionProps = {
  settings: MistralSettings;
  handleChange: HandleChange;
};

const MistralSettingsSection = ({ settings, handleChange }: MistralSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Safe Prompt
        </label>
        <input
          type="checkbox"
          checked={settings.safe_prompt || false}
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
        value={settings.random_seed !== undefined ? settings.random_seed : ''}
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
);

export default MistralSettingsSection;
