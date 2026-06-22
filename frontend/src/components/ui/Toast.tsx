import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';
import { useState, useEffect } from 'react';


export type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

const listeners: Function[] = [];
const toasts: Toast[] = [];

export const toast = {
  success: (msg: string) => notify(msg, 'success'),
  error: (msg: string) => notify(msg, 'error'),
  info: (msg: string) => notify(msg, 'info'),
};

function notify(message: string, type: ToastType) {
  const id = Math.random().toString(36).substr(2, 9);
  toasts.push({ id, message, type });
  listeners.forEach(l => l([...toasts]));
  setTimeout(() => remove(id), 3000); // Auto-dismiss
}

function remove(id: string) {
  const idx = toasts.findIndex(t => t.id === id);
  if (idx > -1) toasts.splice(idx, 1);
  listeners.forEach(l => l([...toasts]));
}


export function ToastContainer() {
  const [items, setItems] = useState<Toast[]>([]);

  useEffect(() => {
    listeners.push(setItems);
    return () => {
      const idx = listeners.indexOf(setItems);
      if (idx > -1) listeners.splice(idx, 1);
    };
  }, []);

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      {items.map(t => (
        <div key={t.id} className={`
          flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border text-sm font-medium
          ${t.type === 'success' ? 'bg-green-50 border-green-200 text-green-800' : ''}
          ${t.type === 'error' ? 'bg-red-50 border-red-200 text-red-800' : ''}
          ${t.type === 'info' ? 'bg-blue-50 border-blue-200 text-blue-800' : ''}
          animate-in slide-in-from-right-full
        `}>
          {t.type === 'success' && <CheckCircle className="w-4 h-4" />}
          {t.type === 'error' && <AlertCircle className="w-4 h-4" />}
          {t.type === 'info' && <Info className="w-4 h-4" />}
          <span>{t.message}</span>
          <button onClick={() => remove(t.id)} className="ml-2 opacity-50 hover:opacity-100">
            <X className="w-3 h-3" />
          </button>
        </div>
      ))}
    </div>
  );
}