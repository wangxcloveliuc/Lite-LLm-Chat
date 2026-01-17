import type { GeminiSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type GeminiImagenSettingsSectionProps = {
  settings: GeminiSettings;
  handleChange: HandleChange;
};

const GeminiImagenSettingsSection = ({ settings, handleChange }: GeminiImagenSettingsSectionProps) => (
  <>
    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Number of Images ({settings.imagen_number_of_images ?? 4})
      </label>
      <input
        type="number"
        min={1}
        max={4}
        value={settings.imagen_number_of_images ?? 4}
        onChange={(e) => {
          const val = e.target.value === '' ? undefined : parseInt(e.target.value, 10);
          handleChange('imagen_number_of_images', val);
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Number of images to generate (1-4). Default is 4.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Image Size
      </label>
      <select
        value={settings.imagen_image_size || '1K'}
        onChange={(e) => handleChange('imagen_image_size', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="1K">1K</option>
        <option value="2K">2K</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Supported for Standard and Ultra models. Default is 1K.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Aspect Ratio
      </label>
      <select
        value={settings.imagen_aspect_ratio || '1:1'}
        onChange={(e) => handleChange('imagen_aspect_ratio', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="1:1">1:1</option>
        <option value="3:4">3:4</option>
        <option value="4:3">4:3</option>
        <option value="9:16">9:16</option>
        <option value="16:9">16:9</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Changes the aspect ratio of generated images. Default is 1:1.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Person Generation
      </label>
      <select
        value={settings.imagen_person_generation || 'allow_adult'}
        onChange={(e) => handleChange('imagen_person_generation', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="dont_allow">Don't Allow</option>
        <option value="allow_adult">Allow Adults (Default)</option>
        <option value="allow_all">Allow Adults + Children</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Controls whether people can be generated in images.
      </p>
    </div>
  </>
);

export default GeminiImagenSettingsSection;
