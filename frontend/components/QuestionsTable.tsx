'use client';

import { CheckCircle, XCircle, Clock, Eye } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Questao {
  id: string;
  exame: string;
  ano: number;
  numero_questao: number;
  materia: string;
  status?: 'correct' | 'incorrect' | 'unanswered';
  tempo?: number; // em segundos
}

interface QuestionsTableProps {
  questoes: Questao[];
  onViewQuestion?: (questaoId: string) => void;
}

export default function QuestionsTable({ questoes, onViewQuestion }: QuestionsTableProps) {
  const formatTempo = (segundos?: number) => {
    if (!segundos) return '-';
    const minutos = Math.floor(segundos / 60);
    const secs = segundos % 60;
    return `${minutos}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'correct':
        return (
          <Badge variant="default" className="bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20">
            <CheckCircle className="w-3 h-3" />
            Correta
          </Badge>
        );
      case 'incorrect':
        return (
          <Badge variant="destructive" className="bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20">
            <XCircle className="w-3 h-3" />
            Incorreta
          </Badge>
        );
      case 'unanswered':
        return (
          <Badge variant="secondary">
            <Clock className="w-3 h-3" />
            Não respondida
          </Badge>
        );
      default:
        return (
          <Badge variant="secondary">-</Badge>
        );
    }
  };

  if (questoes.length === 0) {
    return (
      <Card className="p-8 text-center">
        <p className="text-muted-foreground">Nenhuma questão encontrada</p>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden p-0">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="text-left px-6 py-4 text-sm font-semibold text-muted-foreground">
                #
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-muted-foreground">
                Exame
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-muted-foreground">
                Ano
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-muted-foreground">
                Matéria
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-muted-foreground">
                Status
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-muted-foreground">
                Tempo
              </th>
              {onViewQuestion && (
                <th className="text-right px-6 py-4 text-sm font-semibold text-muted-foreground">
                  Ações
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {questoes.map((questao, index) => (
              <tr
                key={questao.id}
                className="hover:bg-accent/50 transition-colors"
              >
                <td className="px-6 py-4 text-sm text-muted-foreground">
                  {index + 1}
                </td>
                <td className="px-6 py-4 text-sm text-foreground">
                  <div className="flex flex-col">
                    <span className="font-medium">{questao.exame}</span>
                    <span className="text-xs text-muted-foreground">
                      Q{questao.numero_questao}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-foreground">
                  {questao.ano}
                </td>
                <td className="px-6 py-4 text-sm">
                  <Badge variant="secondary">
                    {questao.materia}
                  </Badge>
                </td>
                <td className="px-6 py-4 text-sm">
                  {getStatusBadge(questao.status)}
                </td>
                <td className="px-6 py-4 text-sm text-muted-foreground">
                  {formatTempo(questao.tempo)}
                </td>
                {onViewQuestion && (
                  <td className="px-6 py-4 text-sm text-right">
                    <Button
                      onClick={() => onViewQuestion(questao.id)}
                      variant="outline"
                      size="sm"
                      className="gap-2"
                    >
                      <Eye className="w-4 h-4" />
                      Ver
                    </Button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer com resumo */}
      <div className="border-t border-border bg-muted/30 px-6 py-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Total: <span className="font-semibold text-foreground">{questoes.length}</span> questões
          </span>
          <div className="flex items-center gap-6">
            <span className="text-muted-foreground">
              <span className="text-green-600 dark:text-green-400 font-semibold">
                {questoes.filter((q) => q.status === 'correct').length}
              </span>{' '}
              corretas
            </span>
            <span className="text-muted-foreground">
              <span className="text-red-600 dark:text-red-400 font-semibold">
                {questoes.filter((q) => q.status === 'incorrect').length}
              </span>{' '}
              incorretas
            </span>
            <span className="text-muted-foreground">
              <span className="text-muted-foreground font-semibold">
                {questoes.filter((q) => q.status === 'unanswered').length}
              </span>{' '}
              não respondidas
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
