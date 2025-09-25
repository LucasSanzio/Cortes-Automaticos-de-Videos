import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
});

api.interceptors.request.use((config) => {
  const apiKey = import.meta.env.VITE_API_KEY || 'changeme';
  config.headers['X-API-Key'] = apiKey;
  return config;
});

export const createJob = async (formData) => {
  const response = await api.post('/jobs', formData, {
    headers: {
      'Content-Type': formData instanceof FormData ? 'multipart/form-data' : 'application/json'
    }
  });
  return response.data;
};

export const getJobStatus = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

export default api;
