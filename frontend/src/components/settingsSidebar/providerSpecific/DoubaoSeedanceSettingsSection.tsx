import type { DoubaoSeedanceSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type DoubaoSeedanceSettingsSectionProps = {
  settings: DoubaoSeedanceSettings;
  modelId: string;
  handleChange: HandleChange;
};

const DoubaoSeedanceSettingsSection = ({ settings, modelId, handleChange }: DoubaoSeedanceSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Resolution
      </label>
      <select
        value={settings.resolution || '720p'}
        onChange={(e) => handleChange('resolution', e.target.value)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="480p">480p</option>
        <option value="720p">720p</option>
        <option value="1080p">1080p</option>
      </select>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Ratio
      </label>
      <select
        value={settings.ratio || '16:9'}
        onChange={(e) => handleChange('ratio', e.target.value)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="16:9">16:9</option>
        <option value="4:3">4:3</option>
        <option value="1:1">1:1</option>
        <option value="3:4">3:4</option>
        <option value="9:16">9:16</option>
        <option value="21:9">21:9</option>
        <option value="adaptive">Adaptive</option>
      </select>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Duration (Seconds)
      </label>
      <input
        type="number"
        min="2"
        max="12"
        value={settings.duration || 5}
        onChange={(e) => handleChange('duration', parseInt(e.target.value))}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Seedance 1.5 supports 4-12s, earlier versions support 2-12s.
      </p>
    </div>

    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Watermark
        </label>
        <input
          type="checkbox"
          checked={settings.watermark || false}
          onChange={(e) => handleChange('watermark', e.target.checked)}
          style={{ width: '18px', height: '18px', cursor: 'pointer' }}
        />
      </div>
    </div>

    {modelId.includes('1-5') && (
      <>
        <div className="setting-group">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
              Generate Audio
            </label>
            <input
              type="checkbox"
              checked={settings.generate_audio ?? true}
              onChange={(e) => handleChange('generate_audio', e.target.checked)}
              style={{ width: '18px', height: '18px', cursor: 'pointer' }}
            />
          </div>
        </div>

        <div className="setting-group">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
              Draft Mode (Preview)
            </label>
            <input
              type="checkbox"
              checked={settings.draft || false}
              onChange={(e) => handleChange('draft', e.target.checked)}
              style={{ width: '18px', height: '18px', cursor: 'pointer' }}
            />
          </div>
        </div>
      </>
    )}

    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Camera Fixed
        </label>
        <input
          type="checkbox"
          checked={settings.camera_fixed || false}
          onChange={(e) => handleChange('camera_fixed', e.target.checked)}
          style={{ width: '18px', height: '18px', cursor: 'pointer' }}
        />
      </div>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Seed
      </label>
      <input
        type="number"
        placeholder="-1"
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

export default DoubaoSeedanceSettingsSection;
