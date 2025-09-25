import React from 'react';

const Toast = ({ message, type = 'info' }) => {
  if (!message) return null;
  const colors = {
    success: 'bg-emerald-500',
    error: 'bg-red-500',
    info: 'bg-blue-500'
  };
  return (
    <div className={`fixed top-4 right-4 px-4 py-2 rounded shadow-lg text-white ${colors[type]}`} role="status">
      {message}
    </div>
  );
};

export default Toast;
