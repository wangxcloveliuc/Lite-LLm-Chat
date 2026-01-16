export interface Provider {
  id: string;
  name: string;
  description: string;
  supported?: boolean;
}

export interface Model {
  id: string;
  name: string;
  provider: string;
  description: string;
  context_length?: number;
}

export interface Message {
  id?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  images?: string[];
  videos?: string[];
  audios?: string[];
  created_at?: string;
  provider?: string;
  model?: string;
  thought_process?: string;
}

export interface Session {
  id: number;
  title: string;
  provider: string;
  model: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  messages?: Message[];
}

export interface DeepSeekSettings {
  frequency_penalty: number;
  max_tokens?: number;
  presence_penalty: number;
  temperature: number;
  top_p: number;
  stop: string;
  system_prompt: string;
  image_detail?: 'auto' | 'low' | 'high';
  image_pixel_limit?: {
    max_pixels?: number;
    min_pixels?: number;
  };
  fps?: number;
  video_detail?: 'auto' | 'low' | 'high';
  max_frames?: number;
}

export interface DoubaoSettings extends DeepSeekSettings {
  thinking?: boolean;
  reasoning_effort?: 'low' | 'medium' | 'high';
  max_completion_tokens?: number;
}

export interface DoubaoSeedreamSettings {
  size: string;
  seed?: number;
  sequential_image_generation: 'auto' | 'disabled';
  max_images?: number;
  watermark: boolean;
  prompt_optimize_mode: 'standard' | 'fast';
}

export interface DoubaoSeedanceSettings {
  resolution: '480p' | '720p' | '1080p';
  ratio: '16:9' | '4:3' | '1:1' | '3:4' | '9:16' | '21:9' | 'adaptive';
  duration: number;
  watermark: boolean;
  generate_audio: boolean;
  draft: boolean;
  seed?: number;
  camera_fixed: boolean;
}

export interface SiliconFlowSettings extends DeepSeekSettings {
  enable_thinking?: boolean;
  thinking_budget?: number;
  min_p?: number;
  top_k?: number;
}

export interface CerebrasSettings {
  max_tokens?: number;
  temperature: number;
  top_p: number;
  stop: string;
  system_prompt: string;
  reasoning_effort?: 'low' | 'medium' | 'high';
  disable_reasoning?: boolean;
}

export interface GroqSettings extends DeepSeekSettings {
  reasoning_format?: 'parsed' | 'raw' | 'hidden';
  include_reasoning?: boolean;
  reasoning_effort?: 'none' | 'default' | 'low' | 'medium' | 'high';
  max_completion_tokens?: number;
}

export type GrokSettings = DeepSeekSettings;

export interface NvidiaSettings extends DeepSeekSettings {
  thinking?: boolean;
  reasoning_effort?: 'low' | 'medium' | 'high';
}

export interface OpenRouterSettings extends DeepSeekSettings {
  transforms?: string;
  models?: string;
  route?: 'fallback' | 'sort';
  include_reasoning?: boolean;
  repetition_penalty?: number;
  top_a?: number;
  logprobs?: boolean;
  top_logprobs?: number;
  response_format?: string;
  structured_outputs?: boolean;
  parallel_tool_calls?: boolean;
  reasoning_effort?: 'xhigh' | 'high' | 'medium' | 'low' | 'minimal' | 'none';
  reasoning_summary?: 'auto' | 'concise' | 'detailed';
  image_generation?: boolean;
  image_aspect_ratio?: string;
  image_size?: '1K' | '2K' | '4K';
}

export interface GeminiSettings extends DeepSeekSettings {
  top_k?: number;
  seed?: number;
  thinking_budget?: number;
  safety_threshold?: 'BLOCK_NONE' | 'BLOCK_LOW_AND_ABOVE' | 'BLOCK_MED_AND_ABOVE' | 'BLOCK_ONLY_HIGH' | 'HARM_BLOCK_THRESHOLD_UNSPECIFIED';
}

export interface MistralSettings {
  temperature: number;
  top_p: number;
  max_tokens?: number;
  safe_prompt: boolean;
  random_seed?: number;
  stop: string;
  system_prompt: string;
  frequency_penalty: number;
  presence_penalty: number;
}

export interface ChatRequest {
  provider: string;
  model: string;
  messages: { role: string; content: string; images?: string[]; videos?: string[]; audios?: string[] }[];
  stream: boolean;
  temperature?: number;
  max_tokens?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  top_p?: number;
  stop?: string[] | null;
  session_id?: number;
  message_provider?: string;
  message_model?: string;
  title?: string;
  system_prompt?: string;
  // Extended settings
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
  image_detail?: string;
  image_pixel_limit?: {
    max_pixels?: number;
    min_pixels?: number;
  };
  fps?: number;
  video_detail?: string;
  max_frames?: number;
  // Mistral-specific settings
  safe_prompt?: boolean;
  random_seed?: number;
  // OpenRouter-specific
  transforms?: string[];
  models?: string[];
  route?: string;
  repetition_penalty?: number;
  top_a?: number;
  logprobs?: boolean;
  top_logprobs?: number;
  response_format?: Record<string, unknown>;
  structured_outputs?: boolean;
  parallel_tool_calls?: boolean;
  reasoning?: Record<string, unknown>;
  modalities?: string[];
  image_config?: {
    aspect_ratio?: string;
    image_size?: string;
  };
  // Gemini-specific
  seed?: number;
  safety_threshold?: string;
  // Doubao Seedream specific
  sequential_image_generation?: string;
  max_images?: number;
  watermark?: boolean;
  prompt_optimize_mode?: string;
  size?: string;
  // Doubao Seedance specific
  resolution?: string;
  ratio?: string;
  duration?: number;
  generate_audio?: boolean;
  draft?: boolean;
  camera_fixed?: boolean;
}

export interface StreamChunk {
  content?: string;
  reasoning?: string;
  session_id?: number;
  error?: string;
  done?: boolean;
}

export type SettingsUnion =
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
  | MistralSettings
  | GeminiSettings;

export type CommonSettingsUnion =
  | DeepSeekSettings
  | DoubaoSettings
  | SiliconFlowSettings
  | CerebrasSettings
  | GroqSettings
  | GrokSettings
  | NvidiaSettings
  | OpenRouterSettings
  | MistralSettings
  | GeminiSettings;
