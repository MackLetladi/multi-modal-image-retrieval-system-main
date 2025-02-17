import { useState, useCallback, useEffect } from 'react';

const STORAGE_KEYS = {
  HIGH_CONTRAST: 'accessibility_highContrast',
  FONT_SIZE: 'accessibility_fontSize',
  VOICE_SEARCH: 'accessibility_voiceSearch',
};

export const useAccessibility = () => {
  // Initialize state from localStorage or defaults
  const [highContrast, setHighContrast] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.HIGH_CONTRAST);
    return saved ? JSON.parse(saved) : false;
  });

  const [fontSize, setFontSize] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.FONT_SIZE);
    return saved ? parseInt(saved, 10) : 16;
  });

  const [voiceSearchEnabled, setVoiceSearchEnabled] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEYS.VOICE_SEARCH);
    return saved ? JSON.parse(saved) : false;
  });

  // Update localStorage when settings change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.HIGH_CONTRAST, JSON.stringify(highContrast));
  }, [highContrast]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.FONT_SIZE, fontSize.toString());
  }, [fontSize]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.VOICE_SEARCH, JSON.stringify(voiceSearchEnabled));
  }, [voiceSearchEnabled]);

  // Handler functions
  const toggleHighContrast = useCallback(() => {
    setHighContrast(prev => !prev);
  }, []);

  const increaseFontSize = useCallback(() => {
    setFontSize(prev => Math.min(prev + 1, 24));
  }, []);

  const decreaseFontSize = useCallback(() => {
    setFontSize(prev => Math.max(prev - 1, 12));
  }, []);

  const toggleVoiceSearch = useCallback(() => {
    setVoiceSearchEnabled(prev => !prev);
  }, []);

  const resetSettings = useCallback(() => {
    setHighContrast(false);
    setFontSize(16);
    setVoiceSearchEnabled(false);
  }, []);

  // CSS variables for theme
  const cssVariables = {
    '--font-size-base': `${fontSize}px`,
    '--background-color': highContrast ? '#000' : '#fff',
    '--text-color': highContrast ? '#fff' : '#000',
    '--primary-color': highContrast ? '#00ff00' : '#1976d2',
    '--secondary-color': highContrast ? '#ff0' : '#dc004e',
  };

  return {
    // States
    highContrast,
    fontSize,
    voiceSearchEnabled,
    cssVariables,

    // Actions
    toggleHighContrast,
    increaseFontSize,
    decreaseFontSize,
    toggleVoiceSearch,
    resetSettings,
  };
};
