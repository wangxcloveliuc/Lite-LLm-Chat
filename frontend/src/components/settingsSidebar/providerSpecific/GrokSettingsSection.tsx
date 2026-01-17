const GrokSettingsSection = () => (
  <div className="setting-group">
    <p style={{ fontSize: '13px', color: '#6B7280', fontStyle: 'italic' }}>
      Grok models utilize standard OpenAI-compatible parameters. Specific models like <strong>grok-4-fast-reasoning</strong> may ignore or reject certain parameters like presence_penalty.
    </p>
  </div>
);

export default GrokSettingsSection;
