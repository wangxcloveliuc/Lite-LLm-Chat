import React from 'react';

const NvidiaSettingsSection: React.FC = () => {
  return (
    <div className="setting-group">
      <p style={{ fontSize: '13px', color: '#6B7280', fontStyle: 'italic' }}>
        Nvidia NIM models utilize standard OpenAI-compatible parameters. High-throughput models might have specific limitations on certain parameters.
      </p>
    </div>
  );
};

export default NvidiaSettingsSection;
