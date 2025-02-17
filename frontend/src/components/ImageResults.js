import React from 'react';
import { Grid, Card, CardMedia, CardContent, Typography, Skeleton } from '@mui/material';

const ImageResults = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <Grid container spacing={2}>
        {[...Array(6)].map((_, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card>
              <Skeleton variant="rectangular" height={200} />
              <CardContent>
                <Skeleton variant="text" width="60%" />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  if (!results?.length) {
    return (
      <Typography variant="body1" color="text.secondary" align="center">
        No results found. Try a different search term.
      </Typography>
    );
  }

  return (
    <Grid container spacing={2}>
      {results.map((result, index) => (
        <Grid item xs={12} sm={6} md={4} key={index}>
          <Card>
            <CardMedia
              component="img"
              height="200"
              image={result.url}
              alt={`Search result ${index + 1}`}
              sx={{ objectFit: 'cover' }}
            />
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                Match Score: {(result.score * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default ImageResults;
