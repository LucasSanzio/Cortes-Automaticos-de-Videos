import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getJobStatus } from '../lib/api.js';
import JobStatus from '../components/JobStatus.jsx';

const ProgressPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();

  const { data, refetch } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJobStatus(jobId),
    refetchInterval: 5000
  });

  useEffect(() => {
    if (data?.status === 'DONE') {
      navigate(`/results/${jobId}`);
    }
  }, [data, jobId, navigate]);

  if (!data) {
    return (
      <main className="min-h-screen flex items-center justify-center text-slate-200">
        Carregando status...
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-xl w-full">
        <JobStatus status={data.status} progress={data.progress} step={data.step} />
      </div>
    </main>
  );
};

export default ProgressPage;
