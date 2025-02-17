import React from 'react';
import { Box, TextField, Button, Grid, Typography } from '@mui/material';
import { Search as SearchIcon, Mic as MicIcon } from '@mui/icons-material';
import { useImageSearch } from '../hooks/useImageSearch';
import { useVoiceSearch } from '../hooks/useVoiceSearch';
import ImageResults from './ImageResults';

const SearchPage = () => {
  const { results, isLoading, error, handleSearch, searchTerm } = useImageSearch();
  const { isListening, startListening, stopListening, isSupported } = useVoiceSearch(handleSearch);

  const handleSubmit = (event) => {
    event.preventDefault();
    handleSearch(searchTerm);
  };

  return (
    <Box>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2} alignItems="center" justifyContent="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Search images..."
              variant="outlined"
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              InputProps={{
                endAdornment: isSupported && (
                  <Button
                    color={isListening ? 'secondary' : 'primary'}
                    onClick={isListening ? stopListening : startListening}
                    startIcon={<MicIcon />}
                  >
                    {isListening ? 'Stop' : 'Voice'}
                  </Button>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              type="submit"
              variant="contained"
              color="primary"
              startIcon={<SearchIcon />}
              disabled={isLoading}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </form>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          Error: {error.message}
        </Typography>
      )}

      <Box sx={{ mt: 4 }}>
        <ImageResults results={results} isLoading={isLoading} />
      </Box>
    </Box>
  );
};

export default SearchPage;
