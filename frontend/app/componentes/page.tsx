'use client';

import {
  BookOpen,
  Target,
  Clock,
  Award,
  TrendingUp,
  CheckCircle,
  XCircle,
  Flame,
} from 'lucide-react';
import Header from '@/components/Header';
import StatsCard from '@/components/StatsCard';
import ProgressBar from '@/components/ProgressBar';
import RadioGroup from '@/components/RadioGroup';
import QuestionCard from '@/components/QuestionCard';
import QuestionsTable from '@/components/QuestionsTable';

export default function ComponentesPage() {
  // Dados de exemplo
  const questaoExemplo = {
    id: 'exemplo-1',
    exam_id: 'oab-xxxvi-2022-1',
    exame: 'OAB XXXVI',
    ano: 2022,
    fase: 1,
    numero_questao: 45,
    materia: 'Direito Constitucional',
    enunciado:
      'Sobre os direitos fundamentais previstos na Constituição Federal de 1988, assinale a alternativa CORRETA:',
    alternativas: [
      {
        letra: 'A',
        texto: 'Os direitos fundamentais são absolutos e não podem sofrer qualquer restrição.',
      },
      {
        letra: 'B',
        texto:
          'A dignidade da pessoa humana é fundamento da República Federativa do Brasil.',
      },
      {
        letra: 'C',
        texto: 'Apenas brasileiros natos podem invocar direitos fundamentais.',
      },
      {
        letra: 'D',
        texto: 'Direitos sociais não são considerados direitos fundamentais.',
      },
    ],
    gabarito: 'B',
    anulada: false,
  };

  const questoesTabela = [
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
      status: 'unanswered' as const,
      tempo: 0,
    },
  ];

  return (
    <div className="flex flex-col h-screen">
      <Header
        title="Showcase de Componentes"
        subtitle="Visualize todos os componentes disponíveis"
      />

      <div className="flex-1 overflow-y-auto bg-gray-950">
        <div className="max-w-7xl mx-auto px-4 py-8 space-y-12">
          {/* Seção 1: StatsCard */}
          <section>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">1. StatsCard 📊</h2>
              <p className="text-gray-400">
                Cards de estatísticas com ícones, valores e indicadores de tendência.
              </p>
            </div>

            <div className="space-y-8">
              {/* Tamanho Grande */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Tamanho Grande (lg)</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <StatsCard
                    title="Questões Respondidas"
                    value={256}
                    icon={BookOpen}
                    color="green"
                    size="lg"
                    trend={{ value: 15, direction: 'up', label: 'vs. semana passada' }}
                  />
                  <StatsCard
                    title="Taxa de Acerto"
                    value="72.5%"
                    icon={Target}
                    color="blue"
                    size="lg"
                    trend={{ value: 5.2, direction: 'up', label: 'melhoria este mês' }}
                  />
                </div>
              </div>

              {/* Tamanho Médio */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Tamanho Médio (md) - Padrão</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <StatsCard
                    title="Horas de Estudo"
                    value={18}
                    subtitle="esta semana"
                    icon={Clock}
                    color="purple"
                  />
                  <StatsCard
                    title="Sequência"
                    value={7}
                    subtitle="dias consecutivos"
                    icon={Flame}
                    color="orange"
                  />
                  <StatsCard
                    title="Conquistas"
                    value={12}
                    subtitle="desbloqueadas"
                    icon={Award}
                    color="yellow"
                  />
                  <StatsCard
                    title="Simulados"
                    value={15}
                    subtitle="completos"
                    icon={CheckCircle}
                    color="green"
                  />
                </div>
              </div>

              {/* Tamanho Pequeno */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Tamanho Pequeno (sm)</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <StatsCard
                    title="Acertos"
                    value={185}
                    icon={CheckCircle}
                    color="green"
                    size="sm"
                  />
                  <StatsCard
                    title="Erros"
                    value={71}
                    icon={XCircle}
                    color="red"
                    size="sm"
                  />
                  <StatsCard
                    title="Melhorias"
                    value={"+12%"}
                    icon={TrendingUp}
                    color="blue"
                    size="sm"
                  />
                </div>
              </div>

              {/* Todas as cores */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Todas as Cores</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                  <StatsCard title="Green" value="100" color="green" size="sm" />
                  <StatsCard title="Blue" value="100" color="blue" size="sm" />
                  <StatsCard title="Purple" value="100" color="purple" size="sm" />
                  <StatsCard title="Orange" value="100" color="orange" size="sm" />
                  <StatsCard title="Yellow" value="100" color="yellow" size="sm" />
                  <StatsCard title="Pink" value="100" color="pink" size="sm" />
                  <StatsCard title="Red" value="100" color="red" size="sm" />
                </div>
              </div>
            </div>
          </section>

          {/* Seção 2: ProgressBar */}
          <section>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">2. ProgressBar 📈</h2>
              <p className="text-gray-400">
                Barras de progresso animadas com diferentes cores e tamanhos.
              </p>
            </div>

            <div className="bg-gray-900 rounded-lg border border-gray-800 p-6 space-y-6">
              {/* Tamanhos */}
              <div className="space-y-4">
                <h3 className="text-lg text-gray-300">Tamanhos</h3>
                <ProgressBar value={75} max={100} label="Grande (lg)" size="lg" color="green" />
                <ProgressBar value={60} max={100} label="Médio (md) - Padrão" size="md" color="blue" />
                <ProgressBar value={45} max={100} label="Pequeno (sm)" size="sm" color="purple" />
              </div>

              {/* Cores */}
              <div className="space-y-4">
                <h3 className="text-lg text-gray-300">Cores Disponíveis</h3>
                <ProgressBar value={85} label="Direito Constitucional" color="green" animated />
                <ProgressBar value={70} label="Direito Administrativo" color="blue" animated />
                <ProgressBar value={60} label="Direito Civil" color="purple" animated />
                <ProgressBar value={55} label="Direito Penal" color="orange" animated />
                <ProgressBar value={40} label="Direito Processual" color="yellow" animated />
                <ProgressBar value={30} label="Direito Tributário" color="red" animated />
              </div>

              {/* Com e sem animação */}
              <div className="space-y-4">
                <h3 className="text-lg text-gray-300">Animação</h3>
                <ProgressBar value={70} label="Com animação" color="green" animated={true} />
                <ProgressBar value={70} label="Sem animação" color="green" animated={false} />
              </div>
            </div>
          </section>

          {/* Seção 3: RadioGroup */}
          <section>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">3. RadioGroup 📻</h2>
              <p className="text-gray-400">
                Grupo de opções de rádio com feedback visual para questões.
              </p>
            </div>

            <div className="bg-gray-900 rounded-lg border border-gray-800 p-6 space-y-8">
              {/* Normal */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Estado Normal (Selecionável)</h3>
                <RadioGroup
                  options={[
                    { value: 'A', label: 'Esta é a alternativa A - pode ser selecionada' },
                    { value: 'B', label: 'Esta é a alternativa B - pode ser selecionada' },
                    { value: 'C', label: 'Esta é a alternativa C - pode ser selecionada' },
                    { value: 'D', label: 'Esta é a alternativa D - pode ser selecionada' },
                  ]}
                  value="B"
                  onChange={(val) => console.log('Selecionado:', val)}
                />
              </div>

              {/* Com feedback */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">
                  Com Feedback (Gabarito Exibido)
                </h3>
                <RadioGroup
                  options={[
                    { value: 'A', label: 'Alternativa incorreta não selecionada' },
                    { value: 'B', label: 'Alternativa incorreta selecionada (erro do usuário)' },
                    { value: 'C', label: 'Alternativa correta (gabarito oficial)' },
                    { value: 'D', label: 'Alternativa não selecionada' },
                  ]}
                  value="B"
                  onChange={(val) => console.log('Selecionado:', val)}
                  disabled={true}
                  correctValue="C"
                />
              </div>
            </div>
          </section>

          {/* Seção 4: QuestionCard */}
          <section>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">4. QuestionCard 🎴</h2>
              <p className="text-gray-400">
                Card completo de questão com alternativas, gabarito e explicações.
              </p>
            </div>

            <div className="space-y-6">
              {/* Sem gabarito */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Estado: Respondendo</h3>
                <QuestionCard
                  questao={questaoExemplo}
                  index={0}
                  respostaUsuario="A"
                  mostrarGabarito={false}
                  onSelecionarResposta={(letra) => console.log('Resposta:', letra)}
                />
              </div>

              {/* Com gabarito correto */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Estado: Acertou</h3>
                <QuestionCard
                  questao={questaoExemplo}
                  index={0}
                  respostaUsuario="B"
                  mostrarGabarito={true}
                  onSelecionarResposta={(letra) => console.log('Resposta:', letra)}
                  onExplicar={() => console.log('Solicitar explicação')}
                />
              </div>

              {/* Com gabarito incorreto */}
              <div>
                <h3 className="text-lg text-gray-300 mb-4">Estado: Errou</h3>
                <QuestionCard
                  questao={questaoExemplo}
                  index={0}
                  respostaUsuario="A"
                  mostrarGabarito={true}
                  onSelecionarResposta={(letra) => console.log('Resposta:', letra)}
                  explicacao="A alternativa **B** está correta porque a dignidade da pessoa humana é expressamente prevista no art. 1º, III da Constituição Federal como fundamento da República Federativa do Brasil."
                />
              </div>
            </div>
          </section>

          {/* Seção 5: QuestionsTable */}
          <section>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">5. QuestionsTable 📋</h2>
              <p className="text-gray-400">
                Tabela de histórico de questões com status e métricas.
              </p>
            </div>

            <QuestionsTable
              questoes={questoesTabela}
              onViewQuestion={(id) => console.log('Ver questão:', id)}
            />
          </section>

          {/* Footer */}
          <div className="text-center py-8 border-t border-gray-800">
            <p className="text-gray-400 mb-2">
              ✨ Todos os componentes implementados e funcionando!
            </p>
            <p className="text-sm text-gray-600">
              Desenvolvido para Castro - Plataforma de Preparação para OAB
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
