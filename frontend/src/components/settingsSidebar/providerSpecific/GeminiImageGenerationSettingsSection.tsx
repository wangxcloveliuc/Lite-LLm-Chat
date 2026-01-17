import type { GeminiSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type GeminiImageGenerationSettingsSectionProps = {
  settings: GeminiSettings;
  handleChange: HandleChange;
};

const GeminiImageGenerationSettingsSection = ({
  settings,
  handleChange,
}: GeminiImageGenerationSettingsSectionProps) => {
  const modalities = settings.response_modalities || ['IMAGE', 'TEXT'];

  const toggleModality = (modality: 'IMAGE' | 'TEXT') => {
    const next = new Set(modalities);
    if (next.has(modality)) {
      next.delete(modality);
    } else {
      next.add(modality);
    }
    const normalized = Array.from(next);
    handleChange('response_modalities', normalized.length ? normalized : ['IMAGE']);
  };

  return (
    <>
      <div className="setting-group">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Response Modalities
        </label>
        <div style={{ display: 'flex', gap: '12px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}>
            <input
              type="checkbox"
              checked={modalities.includes('IMAGE')}
              onChange={() => toggleModality('IMAGE')}
            />
            Image
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}>
            <input
              type="checkbox"
              checked={modalities.includes('TEXT')}
              onChange={() => toggleModality('TEXT')}
            />
            Text
          </label>
        </div>
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '6px' }}>
          Controls whether the model responds with image, text, or both.
        </p>
      </div>

      <div className="setting-group">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Aspect Ratio
        </label>
        <select
          value={settings.image_aspect_ratio || '1:1'}
          onChange={(e) => handleChange('image_aspect_ratio', e.target.value || undefined)}
          style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
        >
          {['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9'].map((ratio) => (
            <option key={ratio} value={ratio}>
              {ratio}
            </option>
          ))}
        </select>
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
          Sets the output aspect ratio for generated images.
        </p>
      </div>

      <div className="setting-group">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Image Size
        </label>
        <select
          value={settings.image_size || '1K'}
          onChange={(e) => handleChange('image_size', e.target.value || undefined)}
          style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
        >
          <option value="1K">1K</option>
          <option value="2K">2K</option>
          <option value="4K">4K</option>
        </select>
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
          Higher sizes require models that support 2K/4K (e.g. gemini-3-pro-image-preview).
        </p>
      </div>
    </>
  );
};

export default GeminiImageGenerationSettingsSection;
