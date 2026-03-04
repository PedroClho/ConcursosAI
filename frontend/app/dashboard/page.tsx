'use client';

import {
  BarChart3,
  TrendingUp,
  Target,
  Award,
  Clock,
  BookOpen,
  CheckCircle,
  XCircle,
  Brain,
  Flame,
} from 'lucide-react';
import StatsCard from '@/components/StatsCard';
import ProgressBar from '@/components/ProgressBar';
import QuestionsTable from '@/components/QuestionsTable';
import Header from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function DashboardPage() {
  // Dados mockados para demonstração - em produção viriam da API
  const stats = {
    questoesRespondidas: 156,
    taxaAcerto: 72.5,
    horasEstudo: 18,
    sequenciaAtual: 5,
    melhorSequencia: 12,
    simuladosFeitos: 8,
  };

  const materias = [
    { nome: 'Direito Constitucional', acertos: 85, total: 120, cor: 'green' as const },
    { nome: 'Direito Administrativo', acertos: 65, total: 90, cor: 'blue' as const },
    { nome: 'Direito Civil', acertos: 50, total: 100, cor: 'purple' as const },
    { nome: 'Direito Penal', acertos: 70, total: 95, cor: 'orange' as const },
    { nome: 'Direito Processual Civil', acertos: 40, total: 80, cor: 'yellow' as const },
  ];

  const questoesRecentes = [
    {
      id: '1',
      exame: 'OAB XXXVI',
      ano: 2022,
      numero_questao: 45,
      materia: 'Direito Constitucional',
      status: 'correct' as const,
      tempo: 180,
    },
    {
      id: '2',
      exame: 'OAB XXXVI',
      ano: 2022,
      numero_questao: 46,
      materia: 'Direito Civil',
      status: 'incorrect' as const,
      tempo: 240,
    },
    {
      id: '3',
      exame: 'OAB XXXVI',
      ano: 2022,
      numero_questao: 47,
      materia: 'Direito Penal',
      status: 'correct' as const,
      tempo: 120,
    },
  ];

  return (
    <div className="flex flex-col h-screen">
      <Header title="Dashboard" subtitle="Acompanhe seu progresso e desempenho" />

      <div className="flex-1 overflow-y-auto bg-background">
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Cards de Estatísticas Principais */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              title="Questões Respondidas"
              value={stats.questoesRespondidas}
              icon={BookOpen}
              color="green"
              trend={{ value: 15, direction: 'up', label: 'vs. semana passada' }}
            />
            <StatsCard
              title="Taxa de Acerto"
              value={`${stats.taxaAcerto}%`}
              icon={Target}
              color="blue"
              trend={{ value: 5.2, direction: 'up', label: 'melhoria este mês' }}
            />
            <StatsCard
              title="Horas de Estudo"
              value={stats.horasEstudo}
              subtitle="esta semana"
              icon={Clock}
              color="purple"
            />
            <StatsCard
              title="Sequência Atual"
              value={stats.sequenciaAtual}
              subtitle={`recorde: ${stats.melhorSequencia} dias`}
              icon={Flame}
              color="orange"
            />
          </div>

          {/* Progresso por Matéria */}
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Brain className="w-6 h-6 text-primary" />
                <CardTitle>Progresso por Matéria</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {materias.map((materia) => (
                  <div key={materia.nome}>
                    <ProgressBar
                      value={materia.acertos}
                      max={materia.total}
                      label={materia.nome}
                      color={materia.cor}
                      showPercentage
                      animated
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Cards de Desempenho */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <StatsCard
              title="Simulados Completos"
              value={stats.simuladosFeitos}
              icon={Award}
              color="yellow"
              size="sm"
            />
            <StatsCard
              title="Acertos Totais"
              value={113}
              subtitle="de 156 questões"
              icon={CheckCircle}
              color="green"
              size="sm"
            />
            <StatsCard
              title="Erros Totais"
              value={43}
              subtitle="áreas para revisar"
              icon={XCircle}
              color="red"
              size="sm"
            />
          </div>

          {/* Questões Recentes */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold">Questões Recentes</h2>
            </div>
            <QuestionsTable questoes={questoesRecentes} />
          </div>

          {/* Recomendações */}
          <Card className="bg-primary/5 border-primary/30">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="bg-primary/20 p-3 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-primary mb-2">
                    Recomendações de Estudo
                  </h3>
                  <ul className="space-y-2 text-foreground">
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>
                        Foque em <strong className="text-foreground">Direito Processual Civil</strong> -
                        sua taxa de acerto é 50%
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>
                        Continue praticando <strong className="text-foreground">Direito Constitucional</strong> -
                        você está indo muito bem!
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary mt-1">•</span>
                      <span>
                        Tente manter sua sequência de estudos por mais{' '}
                        <strong className="text-foreground">{stats.melhorSequencia - stats.sequenciaAtual} dias</strong>{' '}
                        para bater seu recorde!
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
