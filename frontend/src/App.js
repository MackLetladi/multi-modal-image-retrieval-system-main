import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import Header from './components/Header';
import SearchPage from './components/SearchPage';
import AccessibilityProvider from './components/AccessibilityProvider';

function App() {
  return (
    <AccessibilityProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
          <Routes>
            <Route path="/" element={<SearchPage />} />
          </Routes>
        </Container>
      </Box>
    </AccessibilityProvider>
  );
}

export default App;
