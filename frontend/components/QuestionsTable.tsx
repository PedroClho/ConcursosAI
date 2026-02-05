'use client';

import { CheckCircle, XCircle, Clock, Eye } from 'lucide-react';

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
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-600/20 text-green-400 rounded-full text-xs font-semibold">
            <CheckCircle className="w-3 h-3" />
            Correta
          </span>
        );
      case 'incorrect':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-600/20 text-red-400 rounded-full text-xs font-semibold">
            <XCircle className="w-3 h-3" />
            Incorreta
          </span>
        );
      case 'unanswered':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-600/20 text-gray-400 rounded-full text-xs font-semibold">
            <Clock className="w-3 h-3" />
            Não respondida
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-600/20 text-gray-400 rounded-full text-xs font-semibold">
            -
          </span>
        );
    }
  };

  if (questoes.length === 0) {
    return (
      <div className="bg-gray-900 rounded-lg border border-gray-800 p-8 text-center">
        <p className="text-gray-400">Nenhuma questão encontrada</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
      {/* Header */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-800 bg-gray-800/50">
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-400">
                #
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-400">
                Exame
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-400">
                Ano
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-400">
                Matéria
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-400">
                Status
              </th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-400">
                Tempo
              </th>
              {onViewQuestion && (
                <th className="text-right px-6 py-4 text-sm font-semibold text-gray-400">
                  Ações
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {questoes.map((questao, index) => (
              <tr
                key={questao.id}
                className="hover:bg-gray-800/30 transition-colors"
              >
                <td className="px-6 py-4 text-sm text-gray-400">
                  {index + 1}
                </td>
                <td className="px-6 py-4 text-sm text-gray-300">
                  <div className="flex flex-col">
                    <span className="font-medium">{questao.exame}</span>
                    <span className="text-xs text-gray-500">
                      Q{questao.numero_questao}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-300">
                  {questao.ano}
                </td>
                <td className="px-6 py-4 text-sm">
                  <span className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full text-xs">
                    {questao.materia}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm">
                  {getStatusBadge(questao.status)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">
                  {formatTempo(questao.tempo)}
                </td>
                {onViewQuestion && (
                  <td className="px-6 py-4 text-sm text-right">
                    <button
                      onClick={() => onViewQuestion(questao.id)}
                      className="inline-flex items-center gap-2 px-3 py-1 bg-green-600/20 hover:bg-green-600/30 text-green-400 rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      Ver
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer com resumo */}
      <div className="border-t border-gray-800 bg-gray-800/30 px-6 py-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">
            Total: <span className="font-semibold text-white">{questoes.length}</span> questões
          </span>
          <div className="flex items-center gap-6">
            <span className="text-gray-400">
              <span className="text-green-400 font-semibold">
                {questoes.filter((q) => q.status === 'correct').length}
              </span>{' '}
              corretas
            </span>
            <span className="text-gray-400">
              <span className="text-red-400 font-semibold">
                {questoes.filter((q) => q.status === 'incorrect').length}
              </span>{' '}
              incorretas
            </span>
            <span className="text-gray-400">
              <span className="text-gray-500 font-semibold">
                {questoes.filter((q) => q.status === 'unanswered').length}
              </span>{' '}
              não respondidas
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
