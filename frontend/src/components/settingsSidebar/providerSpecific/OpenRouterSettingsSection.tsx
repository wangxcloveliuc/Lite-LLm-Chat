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

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Repetition Penalty
      </label>
      <input
        type="number"
        min="0"
        max="2"
        step="0.1"
        placeholder="1.0"
        value={settings.repetition_penalty ?? ''}
        onChange={(e) => {
          const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
          handleChange('repetition_penalty', val);
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Penalize repeated tokens (0.0–2.0). Default is 1.0.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Top A
      </label>
      <input
        type="number"
        min="0"
        max="1"
        step="0.05"
        placeholder="0.0"
        value={settings.top_a ?? ''}
        onChange={(e) => {
          const val = e.target.value === '' ? undefined : parseFloat(e.target.value);
          handleChange('top_a', val);
        }}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Dynamic sampling cutoff (0.0–1.0).
      </p>
    </div>

    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Return Logprobs
        </label>
        <input
          type="checkbox"
          checked={settings.logprobs ?? false}
          onChange={(e) => handleChange('logprobs', e.target.checked)}
          style={{ cursor: 'pointer' }}
        />
      </div>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Include token log probabilities in the response.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Top Logprobs
      </label>
      <input
        type="number"
        min="0"
        max="20"
        step="1"
        placeholder=""
        value={settings.top_logprobs ?? ''}
        onChange={(e) => {
          const val = e.target.value === '' ? undefined : parseInt(e.target.value, 10);
          handleChange('top_logprobs', val);
        }}
        disabled={!settings.logprobs}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px' }}
      />
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Number of alternatives per token (requires logprobs).
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Response Format (JSON)
      </label>
      <textarea
        placeholder='e.g. { "type": "json_object" }'
        value={settings.response_format || ''}
        onChange={(e) => handleChange('response_format', e.target.value)}
        rows={3}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', resize: 'vertical', fontFamily: 'inherit', fontSize: '14px' }}
      />
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        JSON map to force output format. Use JSON mode or JSON schema.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Reasoning Effort
      </label>
      <select
        value={settings.reasoning_effort || ''}
        onChange={(e) => handleChange('reasoning_effort', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="">Default</option>
        <option value="xhigh">X-High</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
        <option value="minimal">Minimal</option>
        <option value="none">None</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Controls reasoning strength for supported models.
      </p>
    </div>

    <div className="setting-group">
      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
        Reasoning Summary
      </label>
      <select
        value={settings.reasoning_summary || ''}
        onChange={(e) => handleChange('reasoning_summary', e.target.value || undefined)}
        style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
      >
        <option value="">Default</option>
        <option value="auto">Auto</option>
        <option value="concise">Concise</option>
        <option value="detailed">Detailed</option>
      </select>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Configure reasoning summaries in responses.
      </p>
    </div>

    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Structured Outputs
        </label>
        <input
          type="checkbox"
          checked={settings.structured_outputs ?? false}
          onChange={(e) => handleChange('structured_outputs', e.target.checked)}
          style={{ cursor: 'pointer' }}
        />
      </div>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Enable structured outputs for JSON schema responses.
      </p>
    </div>

    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Parallel Tool Calls
        </label>
        <input
          type="checkbox"
          checked={settings.parallel_tool_calls ?? true}
          onChange={(e) => handleChange('parallel_tool_calls', e.target.checked)}
          style={{ cursor: 'pointer' }}
        />
      </div>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Allow multiple tool calls in a single turn.
      </p>
    </div>

    <div className="setting-group">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label style={{ fontSize: '14px', fontWeight: '500', cursor: 'pointer' }}>
          Image Generation
        </label>
        <input
          type="checkbox"
          checked={settings.image_generation ?? false}
          onChange={(e) => handleChange('image_generation', e.target.checked)}
          style={{ cursor: 'pointer' }}
        />
      </div>
      <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
        Adds image output to chat completions (modalities: image + text).
      </p>
    </div>

    {settings.image_generation && (
      <>
        <div className="setting-group">
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
            Aspect Ratio
          </label>
          <select
            value={settings.image_aspect_ratio || ''}
            onChange={(e) => handleChange('image_aspect_ratio', e.target.value || undefined)}
            style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
          >
            <option value="">Default (1:1)</option>
            <option value="1:1">1:1 (1024×1024)</option>
            <option value="2:3">2:3 (832×1248)</option>
            <option value="3:2">3:2 (1248×832)</option>
            <option value="3:4">3:4 (864×1184)</option>
            <option value="4:3">4:3 (1184×864)</option>
            <option value="4:5">4:5 (896×1152)</option>
            <option value="5:4">5:4 (1152×896)</option>
            <option value="9:16">9:16 (768×1344)</option>
            <option value="16:9">16:9 (1344×768)</option>
            <option value="21:9">21:9 (1536×672)</option>
          </select>
          <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
            Use Gemini image-generation models to control output proportions.
          </p>
        </div>

        <div className="setting-group">
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
            Image Size (Gemini)
          </label>
          <select
            value={settings.image_size || ''}
            onChange={(e) => handleChange('image_size', e.target.value || undefined)}
            style={{ width: '100%', padding: '8px', border: '1px solid #E5E7EB', borderRadius: '4px', fontSize: '14px' }}
          >
            <option value="">Default (1K)</option>
            <option value="1K">1K</option>
            <option value="2K">2K</option>
            <option value="4K">4K</option>
          </select>
          <p style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
            Higher sizes increase resolution for Gemini image models.
          </p>
        </div>
      </>
    )}
  </>
);

export default OpenRouterSettingsSection;
