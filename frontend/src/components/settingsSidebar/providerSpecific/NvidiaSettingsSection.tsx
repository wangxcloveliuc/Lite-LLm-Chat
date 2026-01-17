import React from 'react';
import type { NvidiaSettings } from '../../../types';

type HandleChange = (field: string, value: unknown) => void;

type NvidiaSettingsSectionProps = {
  settings?: NvidiaSettings;
  handleChange: HandleChange;
};

const NvidiaSettingsSection: React.FC<NvidiaSettingsSectionProps> = ({ settings, handleChange }) => (
  <>
    <div className="setting-group">
      <p style={{ fontSize: '13px', color: '#6B7280', fontStyle: 'italic' }}>
        Nvidia NIM models utilize standard OpenAI-compatible parameters. High-throughput models might have specific limitations on certain parameters.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Chat Template Thinking
      </label>
      <select
        value={settings?.thinking === undefined ? '' : settings?.thinking ? 'true' : 'false'}
        onChange={(e) => {
          const val = e.target.value;
          handleChange('thinking', val === '' ? undefined : val === 'true');
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="">Default</option>
        <option value="true">Enabled</option>
        <option value="false">Disabled</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Maps to chat_template_kwargs.thinking in the request body.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Reasoning Effort
      </label>
      <select
        value={settings?.reasoning_effort || ''}
        onChange={(e) => handleChange('reasoning_effort', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="">Default</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Control reasoning strength; leave blank to omit.
      </p>
    </div>
  </>
);

export default NvidiaSettingsSection;
