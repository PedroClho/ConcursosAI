'use client';

import { useState, useEffect } from 'react';
import { MessageSquare, BookOpen, BarChart3, Scale, ChevronLeft, ChevronRight, Settings, LogOut, Plus, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import { getUserChats, deleteChat } from '@/lib/chat';
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
  const searchParams = useSearchParams();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [chats, setChats] = useState<{ id: string, title: string }[]>([]);

  useEffect(() => {
    if (pathname !== '/login') {
      getUserChats().then(setChats);
    }
  }, [pathname, searchParams]);

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push('/login');
    router.refresh();
  };

  const handleDeleteChat = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (confirm('Deletar este chat?')) {
      await deleteChat(id);
      setChats(chats.filter((c: { id: string, title: string }) => c.id !== id));
      if (searchParams?.get('chat_id') === id) {
        router.push('/');
      }
    }
  };

  const handleNewChat = (e: React.MouseEvent) => {
    e.preventDefault();
    if (chats.length >= 3) {
      alert('Você atingiu o limite máximo de 3 chats permitidos. Por favor, exclua um chat existente para iniciar outro.');
      return;
    }
    router.push('/');
  };

  if (pathname === '/login') return null;

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
                <div className="flex-1 overflow-hidden">
                  <p className="font-medium truncate">{item.name}</p>
                  <p className="text-xs opacity-75 truncate">{item.description}</p>
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Meus Chats */}
      {!collapsed && (
        <div className="flex-1 overflow-y-auto px-3 py-2">
          <div className="flex items-center justify-between mb-2 px-3">
            <h3 className="text-xs font-semibold text-sidebar-foreground/50 uppercase tracking-wider">
              Meus Chats ({chats.length}/3)
            </h3>
            <Button onClick={handleNewChat} variant="ghost" size="icon" className="h-6 w-6 rounded-full hover:bg-sidebar-accent">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <div className="space-y-1">
            {chats.map((chat: { id: string, title: string }) => {
              const isActive = searchParams?.get('chat_id') === chat.id;
              return (
                <div key={chat.id} className="group flex items-center gap-2">
                  <Link
                    href={`/?chat_id=${chat.id}`}
                    className={cn(
                      'flex-1 flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors overflow-hidden group-hover:bg-sidebar-accent/50',
                      isActive ? 'bg-sidebar-accent text-sidebar-primary font-medium' : 'text-sidebar-foreground/70'
                    )}
                  >
                    <MessageSquare className={cn("h-4 w-4 shrink-0", isActive && "text-sidebar-primary")} />
                    <span className="truncate">{chat.title}</span>
                  </Link>
                  <Button
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-destructive/10 hover:text-destructive shrink-0"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              )
            })}
          </div>
        </div>
      )}

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
              <div className="flex gap-1">
                <Button variant="ghost" size="icon" className="size-8 text-muted-foreground">
                  <Settings className="size-4" />
                  <span className="sr-only">Configurações</span>
                </Button>
                <Button onClick={handleLogout} variant="ghost" size="icon" className="size-8 text-destructive hover:text-destructive hover:bg-destructive/10">
                  <LogOut className="size-4" />
                  <span className="sr-only">Sair</span>
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
