import React from 'react';

const steps = ['QUEUED', 'TRANSCRIBING', 'ANALYZING', 'CUTTING', 'DONE'];

const JobStatus = ({ status, progress, step }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-xl">
      <p className="text-lg font-semibold mb-4">Status atual: {step || status}</p>
      <div className="space-y-2">
        {steps.map((current) => (
          <div key={current} className="flex items-center gap-3">
            <div
              className={`h-3 w-3 rounded-full ${
                steps.indexOf(current) <= steps.indexOf(status) ? 'bg-emerald-400' : 'bg-slate-600'
              }`}
            />
            <span className="text-sm">{current}</span>
          </div>
        ))}
      </div>
      <div className="mt-4">
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${progress}%` }} />
        </div>
        <p className="mt-2 text-sm text-slate-300">{progress.toFixed(0)}% concluído</p>
      </div>
    </div>
  );
};

export default JobStatus;
