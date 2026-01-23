# Setup do Frontend - Plataforma de Ensino para Concursos

## 🎯 Stack Escolhido: Next.js 14 + FastAPI

---

## 📁 Estrutura de Pastas Sugerida

```
castro_frontend/
├── app/
│   ├── layout.tsx                    # Layout global
│   ├── page.tsx                      # Landing page
│   ├── (auth)/
│   │   ├── login/
│   │   └── cadastro/
│   ├── concursos/
│   │   ├── oab/
│   │   │   ├── page.tsx             # Dashboard OAB
│   │   │   ├── chat/
│   │   │   │   └── page.tsx         # Chat com Tutor
│   │   │   ├── questoes/
│   │   │   │   └── page.tsx         # Banco de questões
│   │   │   └── simulado/
│   │   │       └── page.tsx         # Simulados
│   │   ├── pf/                       # Polícia Federal (futuro)
│   │   └── layout.tsx                # Layout de concursos
│   └── dashboard/
│       └── page.tsx                  # Progresso do aluno
├── components/
│   ├── ui/                           # shadcn/ui components
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   └── QuestionCard.tsx
│   └── layout/
│       ├── Navbar.tsx
│       └── Sidebar.tsx
├── lib/
│   ├── api.ts                        # Cliente API (FastAPI)
│   └── utils.ts
├── hooks/
│   ├── useChat.ts                    # Hook para chat
│   └── useProgress.ts
└── types/
    └── index.ts                      # TypeScript types
```

---

## 🚀 Comandos de Instalação

### 1. Criar projeto Next.js

```bash
# Na pasta raiz do projeto
npx create-next-app@latest castro_frontend

# Durante instalação, escolha:
# ✓ TypeScript: Yes
# ✓ ESLint: Yes
# ✓ Tailwind CSS: Yes
# ✓ src/ directory: No
# ✓ App Router: Yes
# ✓ Import alias: No
```

### 2. Instalar dependências

```bash
cd castro_frontend

# UI Components
npx shadcn-ui@latest init

# State management & API
npm install @tanstack/react-query zustand axios

# Markdown & syntax highlight (para exibir respostas)
npm install react-markdown remark-gfm rehype-highlight

# Autenticação (futuro)
npm install next-auth

# Ícones
npm install lucide-react
```

---

## 📝 Exemplo de Componente: Chat Interface

### `components/chat/ChatInterface.tsx`

```typescript
'use client'

import { useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { MessageBubble } from './MessageBubble'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim()) return

    // Adicionar mensagem do usuário
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      // Chamar API FastAPI
      const response = await fetch('http://localhost:8000/api/oab/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversation_history: messages
        })
      })

      const data = await response.json()

      // Adicionar resposta do tutor
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Lista de mensagens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && <div className="text-gray-500">Tutor está pensando...</div>}
      </div>

      {/* Input */}
      <div className="border-t p-4 flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Faça sua pergunta..."
          disabled={loading}
        />
        <Button onClick={sendMessage} disabled={loading}>
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}
```

### `components/chat/MessageBubble.tsx`

```typescript
import ReactMarkdown from 'react-markdown'
import { cn } from '@/lib/utils'

interface MessageBubbleProps {
  message: {
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
  }
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn(
      'flex',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'max-w-[80%] rounded-lg px-4 py-2',
        isUser
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100 text-gray-900'
      )}>
        <ReactMarkdown className="prose prose-sm">
          {message.content}
        </ReactMarkdown>
        <div className={cn(
          'text-xs mt-1',
          isUser ? 'text-blue-100' : 'text-gray-500'
        )}>
          {message.timestamp.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </div>
  )
}
```

---

## 🔌 Backend FastAPI

### `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
sys.path.insert(0, 'src')

from agent.oab_agent import OABTutorAgent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Castro - API de Tutores")

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar agente (singleton)
oab_agent = OABTutorAgent(
    model="gpt-4o-mini",
    chroma_persist_directory="./chroma_db",
    collection_name="oab_corpus"
)


class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []


class ChatResponse(BaseModel):
    response: str
    sources: list = []


@app.post("/api/oab/chat", response_model=ChatResponse)
async def oab_chat(request: ChatRequest):
    """Endpoint de chat com o Tutor OAB"""
    try:
        # Converter histórico para formato do agente
        # (simplificado, adaptar conforme necessário)
        
        response = oab_agent.chat(
            user_message=request.message,
            conversation_history=None  # Implementar conversão
        )
        
        return ChatResponse(
            response=response,
            sources=[]  # Adicionar fontes citadas
        )
    
    except Exception as e:
        return ChatResponse(
            response=f"Erro ao processar: {str(e)}",
            sources=[]
        )


@app.get("/api/health")
async def health():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Executar backend:

```bash
# Terminal 1: Backend
python backend/main.py

# Terminal 2: Frontend
cd castro_frontend
npm run dev
```

---

## 🎨 Páginas Principais

### 1. **Landing Page** (`app/page.tsx`)
- Hero com call-to-action
- Lista de concursos disponíveis
- Depoimentos (futuro)

### 2. **Dashboard OAB** (`app/concursos/oab/page.tsx`)
- Cards: "Chat com Tutor", "Resolver Questões", "Simulado"
- Progresso do aluno
- Últimas atividades

### 3. **Chat** (`app/concursos/oab/chat/page.tsx`)
- Interface de chat (componente acima)
- Sugestões de perguntas
- Histórico de conversas

### 4. **Questões** (`app/concursos/oab/questoes/page.tsx`)
- Banco de questões filtráveis (por lei, tema)
- Geração de questões com IA
- Feedback detalhado

---

## 🔐 Autenticação (Fase 2)

```bash
npm install next-auth @auth/prisma-adapter prisma
```

Usar **Supabase** ou **Clerk** para acelerar:
- Supabase: Auth + PostgreSQL + Storage
- Clerk: Auth completo com UI pronta

---

## 📊 Features Futuras

### Curto prazo:
- [ ] Sistema de progresso/estatísticas
- [ ] Gerador de questões personalizadas
- [ ] Modo simulado (cronômetro, score)
- [ ] Histórico de estudos

### Médio prazo:
- [ ] Gamificação (badges, ranking)
- [ ] Planos de estudo personalizados
- [ ] Análise de pontos fracos (via IA)
- [ ] Comunidade (fórum)

### Longo prazo:
- [ ] App mobile (React Native / Expo)
- [ ] Integração com calendário
- [ ] Videoaulas (se expandir)
- [ ] Marketplace de materiais

---

## 💡 Dica: MVP Rápido com Streamlit

Se quiser testar MUITO rápido (1-2 dias):

```python
# streamlit_app.py
import streamlit as st
from agent.oab_agent import OABTutorAgent

st.set_page_config(page_title="Castro - Tutor OAB", page_icon="📚")

# Inicializar agente
if 'agent' not in st.session_state:
    st.session_state.agent = OABTutorAgent()

# Chat
st.title("💬 Tutor OAB - Chat")

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Faça sua pergunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = st.session_state.agent.chat(prompt)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
```

Execute: `streamlit run streamlit_app.py`

---

## 📚 Recursos de Aprendizado

### Next.js:
- [Documentação oficial](https://nextjs.org/docs)
- [Tutorial: Learn Next.js](https://nextjs.org/learn)

### shadcn/ui:
- [Componentes](https://ui.shadcn.com/docs)
- [Exemplos](https://ui.shadcn.com/examples)

### FastAPI + Next.js:
- [Tutorial: FastAPI + React](https://fastapi.tiangolo.com/advanced/custom-response/)
