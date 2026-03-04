'use client';

import { useState } from 'react';
import { MessageSquare, BookOpen, BarChart3, Scale, ChevronLeft, ChevronRight, Settings } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';

const navigation = [
  {
    name: 'Chat Atlas',
    href: '/',
    icon: MessageSquare,
    description: 'Converse com o Atlas'
  },
  {
    name: 'Simulado',
    href: '/simulado',
    icon: BookOpen,
    description: 'Pratique questões'
  },
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: BarChart3,
    description: 'Estatísticas e progresso'
  }
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  
  return (
    <aside
      className={cn(
        'flex h-screen flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300',
        collapsed ? 'w-[72px]' : 'w-[260px]'
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-sidebar-border">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-xl overflow-hidden">
          <img 
            src="/atlas-logo.png" 
            alt="Atlas Logo" 
            className="w-full h-full object-contain"
          />
        </div>
        {!collapsed && (
          <div>
            <h1 className="text-lg font-bold text-sidebar-foreground">Atlas</h1>
            <p className="text-xs text-muted-foreground">Tutor OAB</p>
          </div>
        )}
      </div>

      {/* Navegação */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-primary'
                  : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
              )}
            >
              <Icon className={cn('size-5 shrink-0', isActive && 'text-sidebar-primary')} />
              {!collapsed && (
                <div className="flex-1">
                  <p className="font-medium">{item.name}</p>
                  <p className="text-xs opacity-75">{item.description}</p>
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="px-3 pb-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className="w-full justify-center text-muted-foreground"
        >
          {collapsed ? (
            <ChevronRight className="size-4" />
          ) : (
            <ChevronLeft className="size-4" />
          )}
        </Button>
      </div>

      {/* User profile */}
      <div className="border-t border-sidebar-border px-3 py-4">
        <div className="flex items-center gap-3">
          <Avatar className="size-9">
            <AvatarImage src="" alt="Usuário" />
            <AvatarFallback className="bg-primary/15 text-primary text-xs font-semibold">
              US
            </AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="flex flex-1 items-center justify-between">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-sidebar-foreground">
                  Usuário
                </p>
                <p className="truncate text-xs text-muted-foreground">
                  Versão 2.0
                </p>
              </div>
              <Button variant="ghost" size="icon" className="size-8 text-muted-foreground">
                <Settings className="size-4" />
                <span className="sr-only">Configurações</span>
              </Button>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
