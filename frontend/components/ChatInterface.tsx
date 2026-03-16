'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, GraduationCap } from 'lucide-react'
import MessageBubble from './MessageBubble'
import { sendMessage } from '@/lib/api'
import { getChatMessages, saveMessage, createNewChat } from '@/lib/chat'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useSearchParams, useRouter } from 'next/navigation'

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
  const router = useRouter()
  const searchParams = useSearchParams()
  const chatId = searchParams.get('chat_id')

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (chatId) {
      setLoading(true)
      getChatMessages(chatId)
        .then(setMessages)
        .finally(() => setLoading(false))
    } else {
      setMessages([])
    }
  }, [chatId])

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

    let activeChatId = chatId
    // Criar um novo chat se for a primeira mensagem e não estiver num chat existente
    if (!activeChatId) {
      setLoading(true)
      try {
        const title = input.length > 30 ? input.substring(0, 30) + '...' : input
        const newChat = await createNewChat(title)
        activeChatId = newChat.id
        router.push(`/?chat_id=${activeChatId}`)
      } catch (err: any) {
        setLoading(false)
        setError(err.message || 'Erro ao criar chat. Você já possui 3 chats abertos? Apague algum no menu lateral.')
        return
      }
    }

    const currentInput = input
    const userMessage: Message = {
      role: 'user',
      content: currentInput,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const validChatId = activeChatId as string
      // Salva a mensagem do usuário no supabase
      await saveMessage(validChatId, 'user', currentInput)

      const response = await sendMessage(currentInput, messages)

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp)
      }

      setMessages(prev => [...prev, assistantMessage])
      // Salva a resposta no db
      await saveMessage(validChatId, 'assistant', response.response)
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
    <div className="flex flex-col h-full">
      {/* Área de mensagens */}
      <div className="flex-1 overflow-y-auto px-4 py-6 scrollbar-thin max-w-5xl mx-auto w-full">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="bg-primary p-4 rounded-full mb-4">
              <GraduationCap className="w-12 h-12 text-primary-foreground" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">
              Olá! Sou o Atlas, seu Tutor OAB
            </h2>
            <p className="text-muted-foreground mb-6 max-w-md">
              Estou aqui para te ajudar com dúvidas sobre leis, editais e
              preparação para o Exame de Ordem.
            </p>

            <div className="w-full max-w-2xl">
              <p className="text-sm text-muted-foreground mb-3">Sugestões de perguntas:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {SUGESTOES.map((sugestao, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestion(sugestao)}
                    className="text-left p-3 bg-card hover:bg-accent rounded-lg text-sm text-foreground transition-colors border border-border"
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
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">O Atlas está pensando...</span>
              </div>
            )}
            {error && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 text-destructive text-sm">
                {error}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-border bg-card px-6 py-4 w-full">
        <div className="flex gap-3 w-full">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Faça sua pergunta sobre o Exame de Ordem..."
            disabled={loading}
            rows={1}
            className="flex-1 bg-background border border-input rounded-lg px-4 py-3 text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent resize-none disabled:opacity-50"
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            size="lg"
            className="px-6"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground text-center mt-2">
          Pressione Enter para enviar, Shift+Enter para nova linha
        </p>
      </div>
    </div>
  )
}
