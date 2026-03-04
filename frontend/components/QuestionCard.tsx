'use client';

import { CheckCircle, XCircle, Bot, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import RadioGroup from './RadioGroup';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

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
    <Card className="hover:border-primary/50 transition-all shadow-lg">
      {/* Cabeçalho da questão */}
      <CardHeader className="border-b border-border">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 text-primary font-bold text-sm">
                {index + 1}
              </span>
              <span className="text-muted-foreground text-sm">
                {questao.exame} • Questão {questao.numero_questao}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="secondary">
                {questao.materia}
              </Badge>
              <Badge variant="secondary">
                {questao.ano}
              </Badge>
            </div>
          </div>
          {mostrarGabarito && (
            <div>
              {acertou && (
                <div className="flex items-center gap-2 text-green-600 dark:text-green-400 bg-green-500/10 px-4 py-2 rounded-lg border border-green-500/30">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Correto!</span>
                </div>
              )}
              {errou && (
                <div className="flex items-center gap-2 text-red-600 dark:text-red-400 bg-red-500/10 px-4 py-2 rounded-lg border border-red-500/30">
                  <XCircle className="w-5 h-5" />
                  <span className="font-semibold">Incorreto</span>
                </div>
              )}
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {/* Enunciado */}
        <div className="mb-6">
          <p className="text-foreground leading-relaxed text-base">{questao.enunciado}</p>
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
            <div className="p-4 bg-accent/50 rounded-lg border border-border">
              <p className="text-sm text-muted-foreground">
                <span className="font-semibold text-foreground">Gabarito Oficial:</span>{' '}
                <span className="text-primary font-bold">{questao.gabarito}</span>
              </p>
            </div>

            {/* Botão Explicar com Agente */}
            {!explicacao && onExplicar && (
              <Button
                onClick={onExplicar}
                disabled={loadingExplicacao}
                className="w-full gap-2"
                size="lg"
              >
                {loadingExplicacao ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Analisando...</span>
                  </>
                ) : (
                  <>
                    <Bot className="w-5 h-5" />
                    <span>Explicar com Atlas</span>
                  </>
                )}
              </Button>
            )}

            {/* Explicação do Agente */}
            {explicacao && (
              <div className="p-6 bg-primary/5 border-2 border-primary/30 rounded-lg shadow-xl">
                <div className="flex items-center gap-2 mb-4">
                  <Bot className="w-6 h-6 text-primary" />
                  <span className="text-primary text-lg font-medium">
                    Explicação do Atlas
                  </span>
                </div>
                <div className="prose prose-sm max-w-none explicacao-agente">
                  <ReactMarkdown
                    components={{
                      h1: ({ children, ...props }) => (
                        <h1
                          className="text-2xl text-primary mb-4 mt-2 flex items-center gap-2"
                          {...props}
                        >
                          📚 {children}
                        </h1>
                      ),
                      h2: ({ children, ...props }) => (
                        <h2 className="text-xl text-primary/80 mt-6 mb-3" {...props}>
                          {children}
                        </h2>
                      ),
                      h3: ({ children, ...props }) => (
                        <h3 className="text-lg text-primary/60 mt-4 mb-2" {...props}>
                          {children}
                        </h3>
                      ),
                      blockquote: ({ children, ...props }) => (
                        <blockquote
                          className="bg-accent border-l-4 border-primary pl-4 py-3 my-4 rounded-r-lg shadow-lg"
                          {...props}
                        >
                          <div className="text-primary font-semibold">{children}</div>
                        </blockquote>
                      ),
                      li: ({ children, ...props }) => {
                        const content = String(children);
                        const isCorrect = content.includes('✅');
                        const isIncorrect = content.includes('❌');

                        return (
                          <li
                            className={cn(
                              isCorrect && 'bg-primary/10 border-2 border-primary p-4 rounded-lg font-semibold text-primary shadow-lg mb-3',
                              isIncorrect && 'bg-destructive/10 border border-destructive/30 p-3 rounded-lg text-destructive/80 mb-2 opacity-75',
                              !isCorrect && !isIncorrect && 'text-foreground mb-2 p-2'
                            )}
                            {...props}
                          >
                            {children}
                          </li>
                        );
                      },
                      p: ({ children, ...props }) => (
                        <p className="text-foreground leading-relaxed mb-3" {...props}>
                          {children}
                        </p>
                      ),
                      hr: ({ ...props }) => <hr className="border-border my-6" {...props} />,
                      strong: ({ children, ...props }) => (
                        <strong className="text-foreground font-bold" {...props}>
                          {children}
                        </strong>
                      ),
                      em: ({ children, ...props }) => (
                        <em className="text-muted-foreground italic" {...props}>
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
      </CardContent>
    </Card>
  );
}
