'use client';

import { BarChart3, TrendingUp, Target, Award, Clock, BookOpen } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-400">Acompanhe seu progresso e desempenho</p>
      </div>

      {/* Em construção */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-900 rounded-lg border border-gray-800 p-12 text-center">
          <div className="inline-block p-4 bg-green-600/10 rounded-full mb-6">
            <BarChart3 className="w-16 h-16 text-green-500" />
          </div>
          
          <h2 className="text-2xl font-bold mb-4">Dashboard em Desenvolvimento</h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Em breve você poderá acompanhar suas estatísticas, histórico de simulados, 
            taxa de acerto por matéria e muito mais!
          </p>

          {/* Preview de features futuras */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-8">
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <TrendingUp className="w-8 h-8 text-green-500 mb-3 mx-auto" />
              <h3 className="font-semibold mb-2">Taxa de Acerto</h3>
              <p className="text-sm text-gray-400">Acompanhe sua evolução por matéria</p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <Target className="w-8 h-8 text-blue-500 mb-3 mx-auto" />
              <h3 className="font-semibold mb-2">Pontos Fracos</h3>
              <p className="text-sm text-gray-400">Identifique áreas para melhorar</p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <Award className="w-8 h-8 text-yellow-500 mb-3 mx-auto" />
              <h3 className="font-semibold mb-2">Conquistas</h3>
              <p className="text-sm text-gray-400">Desbloqueie medalhas e marcos</p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <Clock className="w-8 h-8 text-purple-500 mb-3 mx-auto" />
              <h3 className="font-semibold mb-2">Histórico</h3>
              <p className="text-sm text-gray-400">Revise simulados anteriores</p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <BookOpen className="w-8 h-8 text-orange-500 mb-3 mx-auto" />
              <h3 className="font-semibold mb-2">Recomendações</h3>
              <p className="text-sm text-gray-400">Sugestões personalizadas</p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <BarChart3 className="w-8 h-8 text-pink-500 mb-3 mx-auto" />
              <h3 className="font-semibold mb-2">Gráficos</h3>
              <p className="text-sm text-gray-400">Visualize seu desempenho</p>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-gray-700">
            <p className="text-sm text-gray-500">
              <strong>Fase 3</strong> - Estatísticas e Analytics (Em breve)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
