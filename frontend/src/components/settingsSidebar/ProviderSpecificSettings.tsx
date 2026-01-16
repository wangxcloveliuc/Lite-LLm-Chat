import React from 'react';
import type {
  SettingsUnion,
  DoubaoSettings,
  DoubaoSeedreamSettings,
  DoubaoSeedanceSettings,
  SiliconFlowSettings,
  CerebrasSettings,
  GroqSettings,
  OpenRouterSettings,
  MistralSettings,
  GeminiSettings,
  NvidiaSettings,
} from '../../types';
import OpenRouterSettingsSection from './providerSpecific/OpenRouterSettingsSection';
import GrokSettingsSection from './providerSpecific/GrokSettingsSection';
import NvidiaSettingsSection from './providerSpecific/NvidiaSettingsSection';
import MistralSettingsSection from './providerSpecific/MistralSettingsSection';
import GeminiSettingsSection from './providerSpecific/GeminiSettingsSection';
import DoubaoSeedanceSettingsSection from './providerSpecific/DoubaoSeedanceSettingsSection';
import DoubaoSeedreamSettingsSection from './providerSpecific/DoubaoSeedreamSettingsSection';
import DoubaoSettingsSection from './providerSpecific/DoubaoSettingsSection';
import SiliconFlowSettingsSection from './providerSpecific/SiliconFlowSettingsSection';
import CerebrasSettingsSection from './providerSpecific/CerebrasSettingsSection';
import GroqSettingsSection from './providerSpecific/GroqSettingsSection';

type HandleChange = (field: string, value: unknown) => void;

interface ProviderSpecificSettingsProps {
  provider: string;
  modelId: string;
  settings: SettingsUnion;
  handleChange: HandleChange;
}

const ProviderSpecificSettings: React.FC<ProviderSpecificSettingsProps> = ({
  provider,
  modelId,
  settings,
  handleChange,
}) => {
  const isDoubao = provider === 'doubao';
  const isSiliconFlow = provider === 'siliconflow';
  const isCerebras = provider === 'cerebras';
  const isGroq = provider === 'groq';
  const isGrok = provider === 'grok';
  const isNvidia = provider === 'nvidia';
  const isOpenRouter = provider === 'openrouter';
  const isMistral = provider === 'mistral';
  const isGemini = provider === 'gemini';
  const isSeedream = isDoubao && modelId.toLowerCase().includes('seedream');
  const isSeedance = isDoubao && modelId.toLowerCase().includes('seedance');

  const doubaoSettings = settings as DoubaoSettings;
  const seedreamSettings = settings as DoubaoSeedreamSettings;
  const seedanceSettings = settings as DoubaoSeedanceSettings;
  const siliconflowSettings = settings as SiliconFlowSettings;
  const cerebrasSettings = settings as CerebrasSettings;
  const groqSettings = settings as GroqSettings;
  const nvidiaSettings = settings as NvidiaSettings;
  const openrouterSettings = settings as OpenRouterSettings;
  const mistralSettings = settings as MistralSettings;
  const geminiSettings = settings as GeminiSettings;

  if (!isDoubao && !isSiliconFlow && !isCerebras && !isGroq && !isGrok && !isNvidia && !isOpenRouter && !isMistral && !isGemini) return null;

  return (
    <>
      {isOpenRouter && (
        <OpenRouterSettingsSection settings={openrouterSettings} handleChange={handleChange} />
      )}

      {isGrok && <GrokSettingsSection />}

      {isNvidia && <NvidiaSettingsSection />}

      {isMistral && (
        <MistralSettingsSection settings={mistralSettings} handleChange={handleChange} />
      )}

      {isGemini && (
        <GeminiSettingsSection settings={geminiSettings} handleChange={handleChange} />
      )}

      {isSeedance && (
        <DoubaoSeedanceSettingsSection
          settings={seedanceSettings}
          modelId={modelId}
          handleChange={handleChange}
        />
      )}

      {isSeedream && (
        <DoubaoSeedreamSettingsSection settings={seedreamSettings} handleChange={handleChange} />
      )}

      {isDoubao && !isSeedream && (
        <DoubaoSettingsSection settings={doubaoSettings} modelId={modelId} handleChange={handleChange} />
      )}

      {isSiliconFlow && (
        <SiliconFlowSettingsSection settings={siliconflowSettings} handleChange={handleChange} />
      )}

      {isCerebras && (
        <CerebrasSettingsSection settings={cerebrasSettings} modelId={modelId} handleChange={handleChange} />
      )}

      {isGroq && (
        <GroqSettingsSection settings={groqSettings} modelId={modelId} handleChange={handleChange} />
      )}
    </>
  );
};

export default ProviderSpecificSettings;
