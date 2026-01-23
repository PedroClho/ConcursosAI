'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Filter, RotateCcw, CheckCircle, XCircle, Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import Header from '@/components/Header';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Alternativa {
  letra: string;
  texto: string;
}

interface Questao {
  id: string;
  exam_id: string;
  exame: string;
  ano: number;
  fase: number;
  numero_questao: number;
  materia: string;
  enunciado: string;
  alternativas: Alternativa[];
  gabarito: string;
  anulada: boolean;
}

interface Materia {
  nome: string;
  total: number;
}

export default function SimuladoPage() {
  // Estado
  const [materias, setMaterias] = useState<Materia[]>([]);
  const [materiaSelecionada, setMateriaSelecionada] = useState<string>('');
  const [anoSelecionado, setAnoSelecionado] = useState<number | null>(null);
  const [quantidade, setQuantidade] = useState<number>(10);
  const [questoes, setQuestoes] = useState<Questao[]>([]);
  const [respostas, setRespostas] = useState<{ [key: string]: string }>({});
  const [mostrarGabarito, setMostrarGabarito] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMaterias, setLoadingMaterias] = useState(true);
  const [explicacoes, setExplicacoes] = useState<{ [key: string]: string }>({});
  const [loadingExplicacao, setLoadingExplicacao] = useState<{ [key: string]: boolean }>({});

  // Carregar matérias ao montar
  useEffect(() => {
    carregarMaterias();
  }, []);

  const carregarMaterias = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/questoes/materias`);
      setMaterias(response.data);
      setLoadingMaterias(false);
    } catch (error) {
      console.error('Erro ao carregar matérias:', error);
      setLoadingMaterias(false);
    }
  };

  const buscarQuestoes = async () => {
    if (!materiaSelecionada) {
      alert('Selecione uma matéria');
      return;
    }

    setLoading(true);
    setMostrarGabarito(false);
    setRespostas({});

    try {
      const response = await axios.post(`${API_URL}/api/questoes/filtrar`, {
        materia: materiaSelecionada,
        ano: anoSelecionado,
        fase: 1,
        limit: quantidade,
        offset: 0,
        incluir_anuladas: false,
      });

      setQuestoes(response.data.questoes);
    } catch (error) {
      console.error('Erro ao buscar questões:', error);
      alert('Erro ao buscar questões. Verifique se o backend está rodando.');
    } finally {
      setLoading(false);
    }
  };

  const selecionarResposta = (questaoId: string, letra: string) => {
    if (!mostrarGabarito) {
      setRespostas({ ...respostas, [questaoId]: letra });
    }
  };

  const calcularResultado = () => {
    if (questoes.length === 0) return { acertos: 0, erros: 0, percentual: 0 };

    const acertos = questoes.filter(q => respostas[q.id] === q.gabarito).length;
    const erros = questoes.filter(q => respostas[q.id] && respostas[q.id] !== q.gabarito).length;
    const percentual = ((acertos / questoes.length) * 100).toFixed(1);

    return { acertos, erros, percentual: parseFloat(percentual) };
  };

  const reiniciar = () => {
    setQuestoes([]);
    setRespostas({});
    setMostrarGabarito(false);
    setExplicacoes({});
    setLoadingExplicacao({});
  };

  const explicarComAgente = async (questao: Questao) => {
    setLoadingExplicacao({ ...loadingExplicacao, [questao.id]: true });

    try {
      // Formatar a mensagem para o agente
      const alternativasTexto = questao.alternativas
        .map((alt) => `${alt.letra}) ${alt.texto}`)
        .join('\n');

      const mensagem = `Explique a questão ${questao.id} do ${questao.exame}:

ENUNCIADO:
${questao.enunciado}

ALTERNATIVAS:
${alternativasTexto}

GABARITO OFICIAL: ${questao.gabarito}

Por favor, explique por que a alternativa ${questao.gabarito} é a correta, citando os artigos de lei relevantes se houver.`;

      const response = await axios.post(`${API_URL}/api/oab/chat`, {
        message: mensagem,
      });

      setExplicacoes({ ...explicacoes, [questao.id]: response.data.response });
    } catch (error) {
      console.error('Erro ao buscar explicação:', error);
      setExplicacoes({
        ...explicacoes,
        [questao.id]: 'Erro ao buscar explicação. Verifique se o backend está rodando.',
      });
    } finally {
      setLoadingExplicacao({ ...loadingExplicacao, [questao.id]: false });
    }
  };

  const resultado = calcularResultado();

  return (
    <div className="flex flex-col h-screen">
      <Header
        title="Simulado OAB"
        subtitle="Pratique com questões reais"
      />

      <div className="flex-1 overflow-y-auto bg-gray-950">
        <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Botão Novo Simulado */}
        {questoes.length > 0 && (
          <div className="mb-6 flex justify-end">
            <button
              onClick={reiniciar}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition text-white"
            >
              <RotateCcw className="w-4 h-4" />
              Novo Simulado
            </button>
          </div>
        )}

        {/* Filtros */}
        {questoes.length === 0 && (
          <div className="bg-gray-900 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Filter className="w-5 h-5 text-green-500" />
              <h2 className="text-xl font-semibold">Configurar Simulado</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              {/* Matéria */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Matéria *</label>
                <select
                  value={materiaSelecionada}
                  onChange={(e) => setMateriaSelecionada(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  disabled={loadingMaterias}
                >
                  <option value="">Selecione...</option>
                  {materias.map((m) => (
                    <option key={m.nome} value={m.nome}>
                      {m.nome} ({m.total})
                    </option>
                  ))}
                </select>
              </div>

              {/* Ano */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Ano (opcional)</label>
                <select
                  value={anoSelecionado || ''}
                  onChange={(e) => setAnoSelecionado(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                >
                  <option value="">Todos</option>
                  {Array.from({ length: 9 }, (_, i) => 2010 + i).map((ano) => (
                    <option key={ano} value={ano}>
                      {ano}
                    </option>
                  ))}
                </select>
              </div>

              {/* Quantidade */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Quantidade</label>
                <select
                  value={quantidade}
                  onChange={(e) => setQuantidade(parseInt(e.target.value))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                >
                  <option value={5}>5 questões</option>
                  <option value={10}>10 questões</option>
                  <option value={20}>20 questões</option>
                  <option value={30}>30 questões</option>
                </select>
              </div>
            </div>

            <button
              onClick={buscarQuestoes}
              disabled={loading || !materiaSelecionada}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white py-3 rounded-lg font-semibold transition"
            >
              {loading ? 'Carregando...' : 'Iniciar Simulado'}
            </button>
          </div>
        )}

        {/* Questões */}
        {questoes.length > 0 && (
          <>
            {/* Info do simulado */}
            <div className="bg-gray-900 rounded-lg p-4 mb-6 flex items-center justify-between">
              <div>
                <p className="text-gray-400">
                  <span className="font-semibold text-white">{materiaSelecionada}</span>
                  {anoSelecionado && ` • Ano ${anoSelecionado}`}
                </p>
                <p className="text-sm text-gray-500">{questoes.length} questões</p>
              </div>

              {mostrarGabarito && (
                <div className="flex gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Acertos: {resultado.acertos}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <XCircle className="w-5 h-5 text-red-500" />
                    <span>Erros: {resultado.erros}</span>
                  </div>
                  <div className="font-semibold text-green-400">
                    {resultado.percentual}%
                  </div>
                </div>
              )}
            </div>

            {/* Lista de questões */}
            <div className="space-y-6">
              {questoes.map((questao, index) => {
                const respostaUsuario = respostas[questao.id];
                const acertou = mostrarGabarito && respostaUsuario === questao.gabarito;
                const errou = mostrarGabarito && respostaUsuario && respostaUsuario !== questao.gabarito;

                return (
                  <div key={questao.id} className="bg-gray-900 rounded-lg p-6">
                    {/* Cabeçalho da questão */}
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <span className="text-green-500 font-semibold">Questão {index + 1}</span>
                        <span className="text-gray-600 text-sm ml-2">
                          {questao.exame} • Q{questao.numero_questao}
                        </span>
                      </div>
                      {mostrarGabarito && (
                        <div>
                          {acertou && (
                            <div className="flex items-center gap-2 text-green-500">
                              <CheckCircle className="w-5 h-5" />
                              <span className="font-semibold">Correto!</span>
                            </div>
                          )}
                          {errou && (
                            <div className="flex items-center gap-2 text-red-500">
                              <XCircle className="w-5 h-5" />
                              <span className="font-semibold">Incorreto</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Enunciado */}
                    <p className="text-gray-300 mb-6 leading-relaxed">{questao.enunciado}</p>

                    {/* Alternativas */}
                    <div className="space-y-3">
                      {questao.alternativas.map((alt) => {
                        const selecionada = respostaUsuario === alt.letra;
                        const correta = mostrarGabarito && alt.letra === questao.gabarito;
                        const incorreta = mostrarGabarito && selecionada && alt.letra !== questao.gabarito;

                        let className = 'border-2 rounded-lg p-4 cursor-pointer transition ';
                        
                        if (correta) {
                          className += 'border-green-500 bg-green-500/10';
                        } else if (incorreta) {
                          className += 'border-red-500 bg-red-500/10';
                        } else if (selecionada) {
                          className += 'border-green-500 bg-green-500/5';
                        } else {
                          className += 'border-gray-700 hover:border-gray-600';
                        }

                        return (
                          <div
                            key={alt.letra}
                            onClick={() => selecionarResposta(questao.id, alt.letra)}
                            className={className}
                          >
                            <div className="flex gap-3">
                              <span className="font-bold text-gray-400">{alt.letra})</span>
                              <span className="flex-1">{alt.texto}</span>
                              {correta && <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />}
                              {incorreta && <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />}
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Gabarito */}
                    {mostrarGabarito && (
                      <div className="mt-4 space-y-3">
                        <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                          <p className="text-sm text-gray-400">
                            <span className="font-semibold text-white">Gabarito:</span> {questao.gabarito}
                          </p>
                        </div>

                        {/* Botão Explicar com Agente */}
                        {!explicacoes[questao.id] && (
                          <button
                            onClick={() => explicarComAgente(questao)}
                            disabled={loadingExplicacao[questao.id]}
                            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition font-semibold"
                          >
                            {loadingExplicacao[questao.id] ? (
                              <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Analisando...</span>
                              </>
                            ) : (
                              <>
                                <Bot className="w-5 h-5" />
                                <span>Explicar com Agente</span>
                              </>
                            )}
                          </button>
                        )}

                        {/* Explicação do Agente */}
                        {explicacoes[questao.id] && (
                          <div className="p-4 bg-green-900/20 border border-green-800 rounded-lg">
                            <div className="flex items-center gap-2 mb-3">
                              <Bot className="w-5 h-5 text-green-500" />
                              <span className="font-semibold text-green-400">Explicação do Agente</span>
                            </div>
                            <div className="prose prose-invert prose-sm max-w-none">
                              <ReactMarkdown>{explicacoes[questao.id]}</ReactMarkdown>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Botão de finalizar/ver gabarito */}
            {!mostrarGabarito && (
              <div className="mt-8 flex justify-center">
                <button
                  onClick={() => setMostrarGabarito(true)}
                  disabled={Object.keys(respostas).length === 0}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg font-semibold transition"
                >
                  Ver Gabarito
                </button>
              </div>
            )}
          </>
        )}
        </div>
      </div>
    </div>
  );
}
