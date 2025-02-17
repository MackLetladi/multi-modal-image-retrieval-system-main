import React from 'react';
import { Box } from '@mui/material';
import { useAccessibility } from '../hooks/useAccessibility';

const AccessibilityProvider = ({ children }) => {
  const { cssVariables } = useAccessibility();

  return (
    <Box sx={{ ...cssVariables }}>
      {children}
    </Box>
  );
};

export default AccessibilityProvider;
