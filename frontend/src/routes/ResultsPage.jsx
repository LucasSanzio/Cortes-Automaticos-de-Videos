import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getJobStatus } from '../lib/api.js';
import ClipCard from '../components/ClipCard.jsx';

const ResultsPage = () => {
  const { jobId } = useParams();
  const { data } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJobStatus(jobId)
  });

  if (!data) {
    return (
      <main className="min-h-screen flex items-center justify-center text-slate-200">
        Carregando resultados...
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8 bg-slate-900 text-white">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Clipes gerados</h1>
          <p className="text-slate-300">Job {jobId}</p>
        </div>
        <Link to="/" className="text-indigo-400 hover:text-indigo-300">
          Criar novo job
        </Link>
      </header>
      {data.clips.length === 0 ? (
        <p>Nenhum clipe foi gerado.</p>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {data.clips.map((clip) => (
            <ClipCard key={clip.id} clip={clip} />
          ))}
        </div>
      )}
    </main>
  );
};

export default ResultsPage;
