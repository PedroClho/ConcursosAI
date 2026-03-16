'use client'

import { useState, Suspense } from 'react'
import ChatInterface from '@/components/ChatInterface'
import Header from '@/components/Header'

export default function Home() {
  const [resetTrigger, setResetTrigger] = useState(0)

  const handleReset = () => {
    if (confirm('Deseja reiniciar a conversa? Todo o histórico será perdido.')) {
      setResetTrigger(prev => prev + 1)
    }
  }

  return (
    <>
      <div className="flex flex-col h-screen">
        <Header
          onReset={handleReset}
          title="Chat Atlas"
          subtitle="Converse com seu assistente inteligente para OAB"
        />
        <main className="flex-1 overflow-hidden bg-background">
          <Suspense fallback={<div className="flex-1 flex w-full h-full items-center justify-center">Carregando Chat...</div>}>
            <ChatInterface key={resetTrigger} />
          </Suspense>
        </main>
      </div>
    </>
  )
}
