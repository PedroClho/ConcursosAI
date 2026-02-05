'use client';

import { CheckCircle, XCircle, Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import RadioGroup from './RadioGroup';

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

interface QuestionCardProps {
  questao: Questao;
  index: number;
  respostaUsuario?: string;
  mostrarGabarito: boolean;
  onSelecionarResposta: (letra: string) => void;
  explicacao?: string;
  loadingExplicacao?: boolean;
  onExplicar?: () => void;
}

export default function QuestionCard({
  questao,
  index,
  respostaUsuario,
  mostrarGabarito,
  onSelecionarResposta,
  explicacao,
  loadingExplicacao,
  onExplicar,
}: QuestionCardProps) {
  const acertou = mostrarGabarito && respostaUsuario === questao.gabarito;
  const errou = mostrarGabarito && respostaUsuario && respostaUsuario !== questao.gabarito;

  return (
    <div className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-all shadow-lg">
      {/* Cabeçalho da questão */}
      <div className="flex items-start justify-between mb-4 pb-4 border-b border-gray-800">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-600/20 text-green-400 font-bold text-sm">
              {index + 1}
            </span>
            <span className="text-gray-500 text-sm">
              {questao.exame} • Questão {questao.numero_questao}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span className="px-3 py-1 bg-gray-800 rounded-full text-xs text-gray-400">
              {questao.materia}
            </span>
            <span className="px-3 py-1 bg-gray-800 rounded-full text-xs text-gray-400">
              {questao.ano}
            </span>
          </div>
        </div>
        {mostrarGabarito && (
          <div>
            {acertou && (
              <div className="flex items-center gap-2 text-green-500 bg-green-500/10 px-4 py-2 rounded-lg border border-green-500/30">
                <CheckCircle className="w-5 h-5" />
                <span className="font-semibold">Correto!</span>
              </div>
            )}
            {errou && (
              <div className="flex items-center gap-2 text-red-500 bg-red-500/10 px-4 py-2 rounded-lg border border-red-500/30">
                <XCircle className="w-5 h-5" />
                <span className="font-semibold">Incorreto</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Enunciado */}
      <div className="mb-6">
        <p className="text-gray-300 leading-relaxed text-base">{questao.enunciado}</p>
      </div>

      {/* Alternativas usando RadioGroup */}
      <RadioGroup
        options={questao.alternativas.map((alt) => ({
          value: alt.letra,
          label: alt.texto,
        }))}
        value={respostaUsuario}
        onChange={onSelecionarResposta}
        disabled={mostrarGabarito}
        correctValue={mostrarGabarito ? questao.gabarito : undefined}
      />

      {/* Gabarito e Explicação */}
      {mostrarGabarito && (
        <div className="mt-6 space-y-3">
          <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
            <p className="text-sm text-gray-400">
              <span className="font-semibold text-white">Gabarito Oficial:</span>{' '}
              <span className="text-green-400 font-bold">{questao.gabarito}</span>
            </p>
          </div>

          {/* Botão Explicar com Agente */}
          {!explicacao && onExplicar && (
            <button
              onClick={onExplicar}
              disabled={loadingExplicacao}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-all font-semibold shadow-lg hover:shadow-green-600/20"
            >
              {loadingExplicacao ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Analisando...</span>
                </>
              ) : (
                <>
                  <Bot className="w-5 h-5" />
                  <span>Explicar com Agente Tutor</span>
                </>
              )}
            </button>
          )}

          {/* Explicação do Agente */}
          {explicacao && (
            <div className="p-6 bg-gradient-to-br from-green-900/30 to-blue-900/20 border-2 border-green-700/50 rounded-lg shadow-xl">
              <div className="flex items-center gap-2 mb-4">
                <Bot className="w-6 h-6 text-green-400" />
                <span className="text-green-300 text-lg font-medium">
                  Explicação do Agente Tutor
                </span>
              </div>
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown
                  components={{
                    h1: ({ children, ...props }) => (
                      <h1
                        className="text-2xl text-green-400 mb-4 mt-2 flex items-center gap-2"
                        {...props}
                      >
                        📚 {children}
                      </h1>
                    ),
                    h2: ({ children, ...props }) => (
                      <h2 className="text-xl text-blue-400 mt-6 mb-3" {...props}>
                        {children}
                      </h2>
                    ),
                    h3: ({ children, ...props }) => (
                      <h3 className="text-lg text-purple-400 mt-4 mb-2" {...props}>
                        {children}
                      </h3>
                    ),
                    blockquote: ({ children, ...props }) => (
                      <blockquote
                        className="bg-yellow-900/20 border-l-4 border-yellow-500 pl-4 py-3 my-4 rounded-r-lg shadow-lg"
                        {...props}
                      >
                        <div className="text-yellow-200 font-semibold">{children}</div>
                      </blockquote>
                    ),
                    li: ({ children, ...props }) => {
                      const content = String(children);
                      const isCorrect = content.includes('✅');
                      const isIncorrect = content.includes('❌');

                      return (
                        <li
                          className={
                            isCorrect
                              ? 'bg-green-900/30 border-2 border-green-500 p-4 rounded-lg font-semibold text-green-300 shadow-lg shadow-green-900/50 mb-3 transition-all hover:shadow-green-700/50 hover:scale-[1.02]'
                              : isIncorrect
                              ? 'bg-red-900/20 border border-red-700/30 p-3 rounded-lg text-red-300/80 mb-2 opacity-75'
                              : 'text-gray-300 mb-2 p-2'
                          }
                          {...props}
                        >
                          {children}
                        </li>
                      );
                    },
                    p: ({ children, ...props }) => (
                      <p className="text-gray-300 leading-relaxed mb-3" {...props}>
                        {children}
                      </p>
                    ),
                    hr: ({ ...props }) => <hr className="border-gray-700 my-6" {...props} />,
                    strong: ({ children, ...props }) => (
                      <strong className="text-white font-bold" {...props}>
                        {children}
                      </strong>
                    ),
                    em: ({ children, ...props }) => (
                      <em className="text-gray-400 italic" {...props}>
                        {children}
                      </em>
                    ),
                  }}
                >
                  {explicacao}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
