import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob } from '../lib/api.js';
import Toast from './Toast.jsx';

const UrlForm = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    if (!url) {
      setError('Informe uma URL pública.');
      return;
    }
    setLoading(true);
    try {
      const response = await createJob({ source_url: url });
      navigate(`/progress/${response.job_id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Falha ao criar job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium mb-2">
            URL do vídeo
          </label>
          <input
            id="url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full border border-slate-600 rounded p-3 bg-slate-900"
            placeholder="https://..."
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-500 hover:bg-indigo-400 disabled:opacity-50 py-3 rounded font-semibold"
        >
          {loading ? 'Enviando...' : 'Enviar URL'}
        </button>
      </form>
      <Toast message={error} type="error" />
    </div>
  );
};

export default UrlForm;
