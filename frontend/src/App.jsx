import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import UploadPage from './routes/UploadPage.jsx';
import ProgressPage from './routes/ProgressPage.jsx';
import ResultsPage from './routes/ResultsPage.jsx';
import { QueryClientProvider } from '@tanstack/react-query';
import queryClient from './lib/queryClient.js';

const App = () => (
  <QueryClientProvider client={queryClient}>
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/progress/:jobId" element={<ProgressPage />} />
      <Route path="/results/:jobId" element={<ResultsPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </QueryClientProvider>
);

export default App;
