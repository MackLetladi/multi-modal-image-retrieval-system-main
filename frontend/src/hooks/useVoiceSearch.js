import { useState, useCallback, useEffect } from 'react';

export const useVoiceSearch = (onSearch) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);

  // Initialize speech recognition
  const recognition = useCallback(() => {
    if (!('webkitSpeechRecognition' in window)) {
      throw new Error('Speech recognition is not supported in this browser.');
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    return recognition;
  }, []);

  // Start listening
  const startListening = useCallback(() => {
    setError(null);
    setTranscript('');
    
    try {
      const recognitionInstance = recognition();
      
      recognitionInstance.onstart = () => {
        setIsListening(true);
      };

      recognitionInstance.onresult = (event) => {
        const current = event.resultIndex;
        const transcript = event.results[current][0].transcript;
        setTranscript(transcript);
      };

      recognitionInstance.onerror = (event) => {
        setError(event.error);
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
        if (transcript) {
          onSearch(transcript);
        }
      };

      recognitionInstance.start();
    } catch (err) {
      setError(err.message);
      setIsListening(false);
    }
  }, [recognition, onSearch, transcript]);

  // Stop listening
  const stopListening = useCallback(() => {
    try {
      const recognitionInstance = recognition();
      recognitionInstance.stop();
      setIsListening(false);
    } catch (err) {
      setError(err.message);
    }
  }, [recognition]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (isListening) {
        stopListening();
      }
    };
  }, [isListening, stopListening]);

  return {
    isListening,
    transcript,
    error,
    startListening,
    stopListening,
    isSupported: 'webkitSpeechRecognition' in window,
  };
};
