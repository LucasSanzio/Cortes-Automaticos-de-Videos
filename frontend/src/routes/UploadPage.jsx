import React from 'react';
import UploadForm from '../components/UploadForm.jsx';
import UrlForm from '../components/UrlForm.jsx';

const UploadPage = () => {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-10 p-8">
      <header className="text-center space-y-4 max-w-2xl">
        <h1 className="text-3xl font-bold">Plataforma de Cortes Automáticos</h1>
        <p className="text-slate-300">
          Faça upload ou informe uma URL pública de vídeo. Nosso backend cuida da transcrição, seleção de destaques e geração dos
          clipes prontos para download.
        </p>
      </header>
      <section className="grid md:grid-cols-2 gap-8 w-full max-w-4xl">
        <UploadForm />
        <UrlForm />
      </section>
    </main>
  );
};

export default UploadPage;
