import React from 'react';

const ClipCard = ({ clip }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-4 shadow-lg flex flex-col">
      <video controls className="rounded mb-3" src={clip.video_url} />
      <h3 className="text-lg font-semibold">{clip.title}</h3>
      <p className="text-sm text-slate-300 flex-1">{clip.description}</p>
      <div className="mt-3 space-y-2">
        <a className="block text-indigo-400 hover:text-indigo-300" href={clip.video_url} download>
          Baixar vídeo
        </a>
        <a className="block text-indigo-400 hover:text-indigo-300" href={clip.srt_url} download>
          Baixar SRT
        </a>
        <a className="block text-indigo-400 hover:text-indigo-300" href={clip.vtt_url} download>
          Baixar VTT
        </a>
        <a className="block text-indigo-400 hover:text-indigo-300" href={clip.thumbnail_url} target="_blank" rel="noreferrer">
          Ver miniatura
        </a>
      </div>
    </div>
  );
};

export default ClipCard;
