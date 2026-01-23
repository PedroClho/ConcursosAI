'use client';

import { RefreshCw } from 'lucide-react';
import { usePathname } from 'next/navigation';

interface HeaderProps {
  onReset?: () => void;
  title?: string;
  subtitle?: string;
}

export default function Header({ onReset, title, subtitle }: HeaderProps) {
  const pathname = usePathname();
  
  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Título da página */}
        <div>
          {title && <h1 className="text-2xl font-bold text-white">{title}</h1>}
          {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
        </div>
        
        {/* Botão Reiniciar (apenas na página de chat) */}
        {onReset && pathname === '/' && (
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
            title="Reiniciar conversa"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Reiniciar</span>
          </button>
        )}
      </div>
    </header>
  );
}
