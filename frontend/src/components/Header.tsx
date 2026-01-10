import { useState, useRef, useEffect } from 'react';
import type { Provider, Model } from '../types';

interface HeaderProps {
  providers: Provider[];
  models: Model[];
  selectedProvider: string;
  selectedModel: string;
  onProviderChange: (providerId: string) => void;
  onModelChange: (modelId: string) => void;
}

export default function Header({
  providers,
  models,
  selectedProvider,
  selectedModel,
  onProviderChange,
  onModelChange,
}: HeaderProps) {
  const [showProviderDropdown, setShowProviderDropdown] = useState(false);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [modelSearch, setModelSearch] = useState('');
  const providerRef = useRef<HTMLDivElement>(null);
  const modelRef = useRef<HTMLDivElement>(null);

  const selectedProviderObj = providers.find((p) => p.id === selectedProvider);
  const selectedModelObj = models.find((m) => m.id === selectedModel);

  const filteredModels = models.filter((model) =>
    model.name.toLowerCase().includes(modelSearch.toLowerCase())
  );

  useEffect(() => {
    if (!showModelDropdown) {
      setModelSearch('');
    }
  }, [showModelDropdown]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        providerRef.current &&
        !providerRef.current.contains(event.target as Node)
      ) {
        setShowProviderDropdown(false);
      }
      if (
        modelRef.current &&
        !modelRef.current.contains(event.target as Node)
      ) {
        setShowModelDropdown(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="header">
      <div className="dropdown-wrapper" ref={providerRef}>
        <div
          className="model-selector"
          onClick={() => setShowProviderDropdown(!showProviderDropdown)}
        >
          <span>{selectedProviderObj?.name || 'Provider'}</span>
          <svg
            className="chevron-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </div>
        {showProviderDropdown && (
          <div className="dropdown-menu">
            <div className="dropdown-list">
              {providers.map((provider) => (
                <div
                  key={provider.id}
                  className={`dropdown-item ${
                    provider.id === selectedProvider ? 'selected' : ''
                  }`}
                  onClick={() => {
                    onProviderChange(provider.id);
                    setShowProviderDropdown(false);
                  }}
                >
                  <div className="provider-content">
                    <img
                      src={`/${provider.id}.png`}
                      alt={provider.name}
                      className="provider-icon"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                    <span className="provider-name">{provider.name}</span>
                  </div>
                  {provider.id === selectedProvider && (
                    <svg
                      className="checkmark"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="dropdown-wrapper" ref={modelRef}>
        <div
          className="model-selector"
          onClick={() => setShowModelDropdown(!showModelDropdown)}
        >
          <span>{selectedModelObj?.name || 'Model'}</span>
          <svg
            className="chevron-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        </div>
        {showModelDropdown && (
          <div className="dropdown-menu">
            <div className="dropdown-search">
              <svg
                className="search-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
              <input
                type="text"
                placeholder="Search models..."
                value={modelSearch}
                onChange={(e) => setModelSearch(e.target.value)}
                autoFocus
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="dropdown-list">
              {filteredModels.map((model) => (
                <div
                  key={model.id}
                  className={`dropdown-item ${
                    model.id === selectedModel ? 'selected' : ''
                  }`}
                  onClick={() => {
                    onModelChange(model.id);
                    setShowModelDropdown(false);
                  }}
                >
                  <span className="provider-name">{model.name}</span>
                  {model.id === selectedModel && (
                    <svg
                      className="checkmark"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                  )}
                </div>
              ))}
              {filteredModels.length === 0 && (
                <div className="no-results">No models found</div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
