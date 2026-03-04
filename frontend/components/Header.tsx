'use client';

import { RefreshCw, Bell, HelpCircle, Search } from 'lucide-react';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface HeaderProps {
  onReset?: () => void;
  title?: string;
  subtitle?: string;
}

export default function Header({ onReset, title, subtitle }: HeaderProps) {
  const pathname = usePathname();
  
  return (
    <header className="flex flex-col gap-4 border-b border-border bg-card px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        {title && (
          <h1 className="text-xl font-bold text-foreground sm:text-2xl">
            {title}
          </h1>
        )}
        {subtitle && (
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        )}
      </div>
      
      <div className="flex items-center gap-3">
        {/* Botão Reiniciar (apenas na página de chat) */}
        {onReset && pathname === '/' && (
          <Button
            onClick={onReset}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Reiniciar</span>
          </Button>
        )}
        
        <Button variant="ghost" size="icon" className="relative shrink-0 text-muted-foreground hover:text-foreground">
          <Bell className="size-5" />
          <span className="sr-only">Notificações</span>
        </Button>
        
        <Button variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-foreground">
          <HelpCircle className="size-5" />
          <span className="sr-only">Ajuda</span>
        </Button>
      </div>
    </header>
  );
}
