import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob } from '../lib/api.js';
import Toast from './Toast.jsx';

const UploadForm = () => {
  const [file, setFile] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    if (!file) {
      setError('Selecione um arquivo de vídeo.');
      return;
    }
    const allowed = ['mp4', 'mov', 'mkv'];
    const ext = file.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
      setError('Formato inválido.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    try {
      const response = await createJob(formData);
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
          <label htmlFor="file" className="block text-sm font-medium mb-2">
            Arquivo de vídeo
          </label>
          <input
            id="file"
            name="file"
            type="file"
            accept="video/mp4,video/mov,video/x-matroska"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full border border-slate-600 rounded p-3 bg-slate-900"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-500 hover:bg-indigo-400 disabled:opacity-50 py-3 rounded font-semibold"
        >
          {loading ? 'Enviando...' : 'Enviar job'}
        </button>
      </form>
      <Toast message={error} type="error" />
    </div>
  );
};

export default UploadForm;
