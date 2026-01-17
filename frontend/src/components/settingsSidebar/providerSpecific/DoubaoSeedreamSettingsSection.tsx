import type { DoubaoSeedreamSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type DoubaoSeedreamSettingsSectionProps = {
  settings: DoubaoSeedreamSettings;
  handleChange: HandleChange;
};

const DoubaoSeedreamSettingsSection = ({ settings, handleChange }: DoubaoSeedreamSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Image Size
      </label>
      <select
        value={settings.size || '2048x2048'}
        onChange={(e) => handleChange('size', e.target.value)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <optgroup label="Resolutions">
          <option value="1K">1K</option>
          <option value="2K">2K</option>
          <option value="4K">4K</option>
        </optgroup>
        <optgroup label="Proportions (1:1)">
          <option value="2048x2048">2048x2048 (1:1)</option>
        </optgroup>
        <optgroup label="Proportions (Landscape)">
          <option value="2304x1728">2304x1728 (4:3)</option>
          <option value="2560x1440">2560x1440 (16:9)</option>
          <option value="2496x1664">2496x1664 (3:2)</option>
          <option value="3024x1296">3024x1296 (21:9)</option>
        </optgroup>
        <optgroup label="Proportions (Portrait)">
          <option value="1728x2304">1728x2304 (3:4)</option>
          <option value="1440x2560">1440x2560 (9:16)</option>
          <option value="1664x2496">1664x2496 (2:3)</option>
        </optgroup>
      </select>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Sequential Generation
      </label>
      <select
        value={settings.sequential_image_generation || 'disabled'}
        onChange={(e) => handleChange('sequential_image_generation', e.target.value)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="disabled">Disabled (Single Image)</option>
        <option value="auto">Auto (Allow Multiple Images)</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Control whether the model generates a series of related images.
      </p>
    </div>

    {settings.sequential_image_generation === 'auto' && (
      <div className="setting-group">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Max Images ({settings.max_images || 4})
        </label>
        <input
          type="range"
          min="1"
          max="15"
          step="1"
          value={settings.max_images || 4}
          onChange={(e) => handleChange('max_images', parseInt(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>
    )}

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Prompt Optimization
      </label>
      <select
        value={settings.prompt_optimize_mode || 'standard'}
        onChange={(e) => handleChange('prompt_optimize_mode', e.target.value)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="standard">Standard (Higher quality)</option>
        <option value="fast">Fast (Quicker)</option>
      </select>
    </div>

    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Watermark
        </label>
        <input
          type="checkbox"
          checked={settings.watermark !== false}
          onChange={(e) => handleChange('watermark', e.target.checked)}
          style={{ width: '18px', height: '18px', cursor: 'pointer' }}
        />
      </div>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Add an AI-generated watermark to the image.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Seed
      </label>
      <input
        type="number"
        placeholder="Random (-1)"
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

export default DoubaoSeedreamSettingsSection;
