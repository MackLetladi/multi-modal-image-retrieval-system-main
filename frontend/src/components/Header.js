import React from 'react';
import { AppBar, Toolbar, Typography, IconButton, Box } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { useAccessibility } from '../hooks/useAccessibility';

const Header = () => {
  const { highContrast, toggleHighContrast } = useAccessibility();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Image Retrieval System
        </Typography>
        <Box>
          <IconButton
            color="inherit"
            onClick={toggleHighContrast}
            aria-label="toggle high contrast mode"
          >
            {highContrast ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
