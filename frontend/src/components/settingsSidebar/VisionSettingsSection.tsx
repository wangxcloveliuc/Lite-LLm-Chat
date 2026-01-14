import React from 'react';
import type { DeepSeekSettings } from '../../types';

type HandleChange = (field: string, value: unknown) => void;

interface VisionSettingsSectionProps {
  settings: DeepSeekSettings;
  handleChange: HandleChange;
}

const VisionSettingsSection: React.FC<VisionSettingsSectionProps> = ({ settings, handleChange }) => {
  return (
    <div className="setting-group" style={{ borderTop: '1px solid #F3F4F6', paddingTop: '16px' }}>
      <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#374151' }}>Vision Settings</h3>
      <div className="setting-item" style={{ marginBottom: '16px' }}>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Image Detail
        </label>
        <select
          value={settings.image_detail || 'auto'}
          onChange={(e) => handleChange('image_detail', e.target.value)}
          style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
        >
          <option value="auto">Auto</option>
          <option value="low">Low</option>
          <option value="high">High</option>
        </select>
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
          Control the level of detail used for images.
        </p>
      </div>

      <div className="setting-item">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Image Pixel Limit
        </label>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="number"
            placeholder="Max Pixels"
            value={settings.image_pixel_limit?.max_pixels || ''}
            onChange={(e) => {
              const val = e.target.value === '' ? undefined : parseInt(e.target.value);
              handleChange('image_pixel_limit', {
                ...settings.image_pixel_limit,
                max_pixels: val
              });
            }}
            style={{ width: '50%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
          />
          <input
            type="number"
            placeholder="Min Pixels"
            value={settings.image_pixel_limit?.min_pixels || ''}
            onChange={(e) => {
              const val = e.target.value === '' ? undefined : parseInt(e.target.value);
              handleChange('image_pixel_limit', {
                ...settings.image_pixel_limit,
                min_pixels: val
              });
            }}
            style={{ width: '50%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
          />
        </div>
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
          Set max/min pixels for image processing.
        </p>
      </div>

      <div className="setting-item">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Video FPS ({settings.fps || 'Auto'})
        </label>
        <input
          type="number"
          min="0.1"
          max="10"
          step="0.1"
          placeholder="e.g. 1.0"
          value={settings.fps || ''}
          onChange={(e) => {
            const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
            handleChange('fps', val);
          }}
          style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
        />
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
          Sampling rate for video understanding (frames per second).
        </p>
      </div>

      <div className="setting-group">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Video Detail ({settings.video_detail || 'auto'})
        </label>
        <select
          value={settings.video_detail || 'auto'}
          onChange={(e) => handleChange('video_detail', e.target.value)}
          style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
        >
          <option value="auto">Auto</option>
          <option value="low">Low</option>
          <option value="high">High</option>
        </select>
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
          Fidelity level for video processing.
        </p>
      </div>

      <div className="setting-group">
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          Max Frames
        </label>
        <input
          type="number"
          min="1"
          placeholder="e.g. 10"
          value={settings.max_frames || ''}
          onChange={(e) => {
            const val = e.target.value === '' ? undefined : parseInt(e.target.value);
            handleChange('max_frames', val);
          }}
          style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
        />
        <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
          Specify how many frames to extract from video.
        </p>
      </div>
    </div>
  );
};

export default VisionSettingsSection;
