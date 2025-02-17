import { useQuery, useQueryClient } from 'react-query';
import { searchImages } from '../services/api';
import { useState, useCallback } from 'react';

export const useImageSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const queryClient = useQueryClient();

  const {
    data: results,
    isLoading,
    error,
    isError,
  } = useQuery(
    ['search', searchTerm],
    () => searchImages(searchTerm),
    {
      enabled: Boolean(searchTerm),
      staleTime: 5 * 60 * 1000, // Consider results fresh for 5 minutes
      cacheTime: 30 * 60 * 1000, // Keep cache for 30 minutes
      retry: 2,
      onError: (error) => {
        console.error('Search failed:', error);
      },
    }
  );

  const handleSearch = useCallback((query) => {
    setSearchTerm(query.trim());
  }, []);

  const prefetchSearch = useCallback(
    async (query) => {
      if (query.trim()) {
        await queryClient.prefetchQuery(['search', query], () =>
          searchImages(query)
        );
      }
    },
    [queryClient]
  );

  const clearSearch = useCallback(() => {
    setSearchTerm('');
  }, []);

  return {
    results,
    isLoading,
    error,
    isError,
    searchTerm,
    handleSearch,
    prefetchSearch,
    clearSearch,
  };
};
