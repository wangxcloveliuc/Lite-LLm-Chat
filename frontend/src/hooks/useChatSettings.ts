import { useState, useMemo, useCallback } from 'react';
import type {
  DeepSeekSettings,
  DoubaoSettings,
  DoubaoSeedreamSettings,
  DoubaoSeedanceSettings,
  SiliconFlowSettings,
  CerebrasSettings,
  GroqSettings,
  GrokSettings,
  NvidiaSettings,
  OpenRouterSettings,
  GeminiSettings,
  MistralSettings,
} from '../types';

export type ChatRequestSettings = {
  temperature?: number;
  max_tokens?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  top_p?: number;
  stop?: string[];
  system_prompt?: string;
  image_detail?: string;
  image_pixel_limit?: {
    max_pixels?: number;
    min_pixels?: number;
  };
  fps?: number;
  video_detail?: string;
  max_frames?: number;
  safe_prompt?: boolean;
  random_seed?: number;
  thinking?: boolean;
  reasoning_effort?: string;
  disable_reasoning?: boolean;
  reasoning_format?: string;
  include_reasoning?: boolean;
  max_completion_tokens?: number;
  enable_thinking?: boolean;
  thinking_budget?: number;
  min_p?: number;
  top_k?: number;
  seed?: number;
  safety_threshold?: string;
  sequential_image_generation?: string;
  max_images?: number;
  watermark?: boolean;
  prompt_optimize_mode?: string;
  size?: string;
  resolution?: string;
  ratio?: string;
  duration?: number;
  generate_audio?: boolean;
  draft?: boolean;
  camera_fixed?: boolean;
  transforms?: string;
  models?: string;
  route?: string;
  repetition_penalty?: number;
  top_a?: number;
  logprobs?: boolean;
  top_logprobs?: number;
  response_format?: string;
  structured_outputs?: boolean;
  parallel_tool_calls?: boolean;
  reasoning_summary?: 'auto' | 'concise' | 'detailed';
  image_generation?: boolean;
  response_modalities?: ('IMAGE' | 'TEXT')[];
  image_aspect_ratio?: string;
  image_size?: '1K' | '2K' | '4K';
  thinking_level?: 'minimal' | 'low' | 'medium' | 'high';
  media_resolution?:
    | 'MEDIA_RESOLUTION_UNSPECIFIED'
    | 'MEDIA_RESOLUTION_LOW'
    | 'MEDIA_RESOLUTION_MEDIUM'
    | 'MEDIA_RESOLUTION_HIGH';
  google_search?: boolean;
  url_context?: boolean;
  web_search?: boolean;
  web_search_results?: number;
  web_search_engine?: 'native' | 'exa';
  web_search_prompt?: string;
  web_search_context_size?: 'low' | 'medium' | 'high';
  imagen_number_of_images?: number;
  imagen_image_size?: '1K' | '2K';
  imagen_aspect_ratio?: '1:1' | '3:4' | '4:3' | '9:16' | '16:9';
  imagen_person_generation?: 'dont_allow' | 'allow_adult' | 'allow_all';
};

type UseChatSettingsParams = {
  selectedProvider: string;
  selectedModel: string;
};

type UseChatSettingsReturn = {
  activeSettings:
    | DeepSeekSettings
    | DoubaoSettings
    | DoubaoSeedreamSettings
    | DoubaoSeedanceSettings
    | SiliconFlowSettings
    | CerebrasSettings
    | GroqSettings
    | GrokSettings
    | NvidiaSettings
    | OpenRouterSettings
    | GeminiSettings
    | MistralSettings;
  getCurrentSettings: () => ChatRequestSettings;
  handleSettingsChange: (newSettings: unknown) => void;
};

const parseStop = (stop?: string) => (stop ? stop.split(',').map((s) => s.trim()) : undefined);

const isSeedreamModel = (provider: string, modelId: string) =>
  provider === 'doubao' && modelId.toLowerCase().includes('seedream');

const isSeedanceModel = (provider: string, modelId: string) =>
  provider === 'doubao' && modelId.toLowerCase().includes('seedance');

const useChatSettings = ({ selectedProvider, selectedModel }: UseChatSettingsParams): UseChatSettingsReturn => {
  const [deepseekSettings, setDeepseekSettings] = useState<DeepSeekSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
  });
  const [doubaoSettings, setDoubaoSettings] = useState<DoubaoSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
    thinking: undefined,
    reasoning_effort: 'medium',
    max_completion_tokens: undefined,
  });
  const [doubaoSeedreamSettings, setDoubaoSeedreamSettings] = useState<DoubaoSeedreamSettings>({
    size: '2048x2048',
    seed: undefined,
    sequential_image_generation: 'disabled',
    max_images: 1,
    watermark: true,
    prompt_optimize_mode: 'standard',
  });
  const [doubaoSeedanceSettings, setDoubaoSeedanceSettings] = useState<DoubaoSeedanceSettings>({
    resolution: '720p',
    ratio: '16:9',
    duration: 5,
    watermark: false,
    generate_audio: true,
    draft: false,
    seed: undefined,
    camera_fixed: false,
  });
  const [siliconflowSettings, setSiliconflowSettings] = useState<SiliconFlowSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
    enable_thinking: undefined,
    thinking_budget: undefined,
    min_p: undefined,
    top_k: undefined,
  });
  const [cerebrasSettings, setCerebrasSettings] = useState<CerebrasSettings>({
    max_tokens: undefined,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    reasoning_effort: 'medium',
    disable_reasoning: false,
  });
  const [groqSettings, setGroqSettings] = useState<GroqSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 0.6,
    top_p: 0.95,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    reasoning_format: 'parsed',
    include_reasoning: true,
    reasoning_effort: 'default',
    max_completion_tokens: undefined,
  });
  const [nvidiaSettings, setNvidiaSettings] = useState<NvidiaSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
    thinking: undefined,
    reasoning_effort: undefined,
  });
  const [openrouterSettings, setOpenrouterSettings] = useState<OpenRouterSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    transforms: '',
    models: '',
    route: undefined,
    include_reasoning: undefined,
    repetition_penalty: undefined,
    top_a: undefined,
    logprobs: false,
    top_logprobs: undefined,
    response_format: '',
    structured_outputs: false,
    parallel_tool_calls: true,
    reasoning_effort: undefined,
    reasoning_summary: undefined,
    image_generation: false,
    image_aspect_ratio: undefined,
    image_size: undefined,
    web_search: false,
    web_search_results: undefined,
    web_search_engine: undefined,
    web_search_prompt: '',
    web_search_context_size: undefined,
  });
  const [grokSettings, setGrokSettings] = useState<GrokSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    image_detail: 'auto',
    image_pixel_limit: undefined,
    fps: undefined,
    video_detail: 'auto',
    max_frames: undefined,
  });
  const [mistralSettings, setMistralSettings] = useState<MistralSettings>({
    temperature: 0.7,
    top_p: 1,
    max_tokens: undefined,
    safe_prompt: false,
    random_seed: undefined,
    stop: '',
    system_prompt: '',
    frequency_penalty: 0,
    presence_penalty: 0,
  });
  const [geminiSettings, setGeminiSettings] = useState<GeminiSettings>({
    frequency_penalty: 0,
    max_tokens: undefined,
    presence_penalty: 0,
    temperature: 1,
    top_p: 1,
    stop: '',
    system_prompt: '',
    top_k: undefined,
    seed: undefined,
    thinking_budget: undefined,
    safety_threshold: 'BLOCK_NONE',
    thinking_level: 'high',
    media_resolution: 'MEDIA_RESOLUTION_UNSPECIFIED',
    google_search: false,
    url_context: false,
    response_modalities: ['IMAGE', 'TEXT'],
    image_aspect_ratio: '1:1',
    image_size: undefined,
    imagen_number_of_images: 4,
    imagen_image_size: '1K',
    imagen_aspect_ratio: '1:1',
    imagen_person_generation: 'allow_adult',
  });

  const getCurrentSettings = useCallback((): ChatRequestSettings => {
    if (isSeedreamModel(selectedProvider, selectedModel)) {
      return { ...doubaoSeedreamSettings };
    }
    if (isSeedanceModel(selectedProvider, selectedModel)) {
      return { ...doubaoSeedanceSettings };
    }
    if (selectedProvider === 'doubao') {
      return { ...doubaoSettings, stop: parseStop(doubaoSettings.stop) };
    }
    if (selectedProvider === 'deepseek') {
      return { ...deepseekSettings, stop: parseStop(deepseekSettings.stop) };
    }
    if (selectedProvider === 'siliconflow') {
      return { ...siliconflowSettings, stop: parseStop(siliconflowSettings.stop) };
    }
    if (selectedProvider === 'cerebras') {
      return { ...cerebrasSettings, stop: parseStop(cerebrasSettings.stop) };
    }
    if (selectedProvider === 'groq') {
      return { ...groqSettings, stop: parseStop(groqSettings.stop) };
    }
    if (selectedProvider === 'grok') {
      return { ...grokSettings, stop: parseStop(grokSettings.stop) };
    }
    if (selectedProvider === 'nvidia') {
      return { ...nvidiaSettings, stop: parseStop(nvidiaSettings.stop) };
    }
    if (selectedProvider === 'openrouter') {
      return { ...openrouterSettings, stop: parseStop(openrouterSettings.stop) };
    }
    if (selectedProvider === 'mistral') {
      return { ...mistralSettings, stop: parseStop(mistralSettings.stop) };
    }
    if (selectedProvider === 'gemini') {
      return { ...geminiSettings, stop: parseStop(geminiSettings.stop) };
    }
    return { ...deepseekSettings, stop: parseStop(deepseekSettings.stop) };
  }, [
    cerebrasSettings,
    deepseekSettings,
    doubaoSeedanceSettings,
    doubaoSeedreamSettings,
    doubaoSettings,
    geminiSettings,
    grokSettings,
    groqSettings,
    nvidiaSettings,
    mistralSettings,
    openrouterSettings,
    selectedModel,
    selectedProvider,
    siliconflowSettings,
  ]);

  const activeSettings = useMemo(() => {
    if (isSeedreamModel(selectedProvider, selectedModel)) {
      return doubaoSeedreamSettings;
    }
    if (isSeedanceModel(selectedProvider, selectedModel)) {
      return doubaoSeedanceSettings;
    }
    if (selectedProvider === 'doubao') {
      return doubaoSettings;
    }
    if (selectedProvider === 'siliconflow') {
      return siliconflowSettings;
    }
    if (selectedProvider === 'cerebras') {
      return cerebrasSettings;
    }
    if (selectedProvider === 'groq') {
      return groqSettings;
    }
    if (selectedProvider === 'grok') {
      return grokSettings;
    }
    if (selectedProvider === 'nvidia') {
      return nvidiaSettings;
    }
    if (selectedProvider === 'openrouter') {
      return openrouterSettings;
    }
    if (selectedProvider === 'mistral') {
      return mistralSettings;
    }
    if (selectedProvider === 'gemini') {
      return geminiSettings;
    }
    return deepseekSettings;
  }, [
    cerebrasSettings,
    deepseekSettings,
    doubaoSeedanceSettings,
    doubaoSeedreamSettings,
    doubaoSettings,
    geminiSettings,
    grokSettings,
    groqSettings,    nvidiaSettings,    mistralSettings,
    openrouterSettings,
    selectedModel,
    selectedProvider,
    siliconflowSettings,
  ]);

  const handleSettingsChange = useCallback(
    (newSettings: unknown) => {
      if (isSeedreamModel(selectedProvider, selectedModel)) {
        setDoubaoSeedreamSettings(newSettings as DoubaoSeedreamSettings);
      } else if (isSeedanceModel(selectedProvider, selectedModel)) {
        setDoubaoSeedanceSettings(newSettings as DoubaoSeedanceSettings);
      } else if (selectedProvider === 'doubao') {
        setDoubaoSettings(newSettings as DoubaoSettings);
      } else if (selectedProvider === 'siliconflow') {
        setSiliconflowSettings(newSettings as SiliconFlowSettings);
      } else if (selectedProvider === 'cerebras') {
        setCerebrasSettings(newSettings as CerebrasSettings);
      } else if (selectedProvider === 'groq') {
        setGroqSettings(newSettings as GroqSettings);
      } else if (selectedProvider === 'grok') {
        setGrokSettings(newSettings as GrokSettings);
      } else if (selectedProvider === 'nvidia') {
        setNvidiaSettings(newSettings as NvidiaSettings);
      } else if (selectedProvider === 'openrouter') {
        setOpenrouterSettings(newSettings as OpenRouterSettings);
      } else if (selectedProvider === 'mistral') {
        setMistralSettings(newSettings as MistralSettings);
      } else if (selectedProvider === 'gemini') {
        setGeminiSettings(newSettings as GeminiSettings);
      } else {
        setDeepseekSettings(newSettings as DeepSeekSettings);
      }
    },
    [selectedModel, selectedProvider],
  );

  return {
    activeSettings,
    getCurrentSettings,
    handleSettingsChange,
  };
};

export default useChatSettings;
