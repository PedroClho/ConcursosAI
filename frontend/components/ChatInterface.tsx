'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import MessageBubble from './MessageBubble'
import { sendMessage } from '@/lib/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const SUGESTOES = [
  'O que diz o Art. 5º da CF sobre direitos fundamentais?',
  'Qual o prazo para recurso no CPC?',
  'Quando é a prova do Exame de Ordem?',
  'Explique sobre prisão em flagrante no CPP',
]

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus no input ao montar
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const response = await sendMessage(input, messages)
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp)
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err: any) {
      setError(err.message || 'Erro ao enviar mensagem')
      console.error('Erro:', err)
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestion = (suggestion: string) => {
    setInput(suggestion)
    inputRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto">
      {/* Área de mensagens */}
      <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="bg-primary-600 p-4 rounded-full mb-4">
              <GraduationCapIcon className="w-12 h-12 text-white" />
            </div>
            <h2 className="text-2xl text-dark-900 mb-2" style={{ fontWeight: 400, letterSpacing: '-0.02em' }}>
              Olá! Sou seu Tutor OAB
            </h2>
            <p className="text-dark-600 mb-6 max-w-md">
              Estou aqui para te ajudar com dúvidas sobre leis, editais e 
              preparação para o Exame de Ordem.
            </p>
            
            <div className="w-full max-w-2xl">
              <p className="text-sm text-dark-500 mb-3">Sugestões de perguntas:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {SUGESTOES.map((sugestao, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestion(sugestao)}
                    className="text-left p-3 bg-dark-100 hover:bg-dark-200 rounded-lg text-sm text-dark-800 transition-colors"
                  >
                    {sugestao}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-dark-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">O tutor está pensando...</span>
              </div>
            )}
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
                {error}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-dark-200 bg-dark-100 px-4 py-4">
        <div className="max-w-4xl mx-auto flex gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Faça sua pergunta sobre o Exame de Ordem..."
            disabled={loading}
            rows={1}
            className="flex-1 bg-dark-50 border border-dark-200 rounded-lg px-4 py-3 text-dark-900 placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent resize-none disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="bg-primary-600 hover:bg-primary-700 disabled:bg-dark-300 text-white rounded-lg px-6 py-3 transition-colors disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <p className="text-xs text-dark-500 text-center mt-2">
          Pressione Enter para enviar, Shift+Enter para nova linha
        </p>
      </div>
    </div>
  )
}

// Componente simples de ícone
function GraduationCapIcon({ className }: { className?: string }) {
  return (
    <svg 
      className={className}
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      <path 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        strokeWidth={2} 
        d="M12 14l9-5-9-5-9 5 9 5z M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z M12 14l-9-5v7.5a9 9 0 0018 0V9l-9 5z"
      />
    </svg>
  )
}
