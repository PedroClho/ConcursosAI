# 💻 Frontend Castro - Next.js

## 📋 Sobre

Interface web moderna para o sistema Castro de preparação para OAB.

**Tecnologias:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Axios
- Lucide Icons

---

## 🚀 Como Executar

### **1. Instalar Dependências**

```bash
npm install
```

### **2. Configurar Variáveis de Ambiente**

Criar arquivo `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **3. Rodar em Desenvolvimento**

```bash
npm run dev
```

Acesse: http://localhost:3000

---

## 📁 Estrutura

```
frontend/
├── app/                    # App Router (Next.js 14)
│   ├── page.tsx            # Página principal (Chat)
│   ├── simulado/
│   │   └── page.tsx        # Página de simulado
│   ├── dashboard/
│   │   └── page.tsx        # Página de dashboard (em desenvolvimento)
│   ├── layout.tsx          # Layout raiz com sidebar
│   └── globals.css         # Estilos globais
│
├── components/             # Componentes React
│   ├── Sidebar.tsx         # Navegação lateral (3 abas)
│   ├── Header.tsx          # Cabeçalho de página
│   ├── ChatInterface.tsx   # Interface de chat
│   ├── MessageBubble.tsx   # Bolha de mensagem
│   ├── QuestionCard.tsx    # ✨ Card de questão completo
│   ├── RadioGroup.tsx      # ✨ Grupo de opções de rádio
│   ├── StatsCard.tsx       # ✨ Card de estatísticas
│   ├── ProgressBar.tsx     # ✨ Barra de progresso
│   ├── QuestionsTable.tsx  # ✨ Tabela de questões
│   └── README.md           # ✨ Documentação de componentes
│
├── lib/                    # Utilitários
│   └── api.ts              # Cliente da API
│
└── public/                 # Arquivos estáticos
```

---

## 📖 Páginas

### **1. Chat (`/`)**

- Conversa com agente tutor
- Respostas em markdown
- Sugestões de perguntas
- Botão de reset

**Funcionalidades:**
- Chat em tempo real
- Histórico de conversas
- Citação de fontes
- Busca em leis e editais
- Busca e explicação de questões (via agente)

---

### **2. Simulado (`/simulado`)** ✨ ATUALIZADO

- Prática com questões reais da OAB
- Filtros por matéria, ano, quantidade
- **Interface melhorada com QuestionCard**
- Gabarito ao final

**Funcionalidades:**
- Selecionar matéria (dropdown)
- Filtrar por ano (2010-2018)
- Escolher quantidade (5-30 questões)
- Marcar respostas com RadioGroup estilizado
- Ver gabarito com acertos/erros
- Percentual de aproveitamento
- Explicação do gabarito pelo agente
- **Cards visuais modernos para cada questão**
- **Feedback visual aprimorado**

---

### **3. Dashboard (`/dashboard`)** ✨ IMPLEMENTADO

- Página de estatísticas **funcional**
- Dados mockados para demonstração

**Funcionalidades implementadas:**
- ✅ Cards de estatísticas principais (4)
- ✅ Progresso por matéria com ProgressBars
- ✅ Cards secundários de métricas
- ✅ Tabela de questões recentes
- ✅ Recomendações personalizadas
- ✅ Indicadores de tendência
- ✅ Visual moderno e profissional

---

### **4. Componentes (`/componentes`)** ✨ NOVO

- Showcase de todos os componentes
- Página de demonstração e testes

**Exibe:**
- ✅ StatsCard (todos os tamanhos e cores)
- ✅ ProgressBar (animações e variações)
- ✅ RadioGroup (estados diferentes)
- ✅ QuestionCard (completo com exemplos)
- ✅ QuestionsTable (com dados de exemplo)

---

## 🎨 Design System

### **Cores (Tailwind)**

```
Dark Theme:
- Background: gray-950
- Cards: gray-900
- Borders: gray-800
- Text: white / gray-400

Accent (Green):
- Primary: green-500
- Hover: green-600
- Active: green-700
```

### **Componentes**

**Sidebar:**
- Logo Castro
- Navegação principal (3 abas):
  - Chat Tutor
  - Simulado
  - Dashboard
- Highlight da aba ativa
- Footer com versão

**Header:**
- Título da página
- Subtítulo
- Botão de reset (condicional)

**ChatInterface:**
- Input de mensagem
- Botão enviar
- Sugestões rápidas
- Loading state

**MessageBubble:**
- Suporte a markdown
- Estilo diferenciado por role (user/assistant)

**QuestionCard:** ✨ NOVO
- Card completo de questão
- Badges de matéria/ano/exame
- RadioGroup integrado
- Feedback visual (correto/incorreto)
- Explicação do agente com markdown
- Estados de loading

**RadioGroup:** ✨ NOVO
- Opções de rádio estilizadas
- Feedback visual automático
- Estados hover e active
- Acessibilidade nativa

**StatsCard:** ✨ NOVO
- 7 cores disponíveis
- 3 tamanhos (sm/md/lg)
- Ícones personalizáveis
- Indicador de tendência (↑↓)
- Subtítulos opcionais

**ProgressBar:** ✨ NOVO
- Barra de progresso animada
- Animação shimmer opcional
- 6 cores, 3 tamanhos
- Label e porcentagem
- Cálculo automático

**QuestionsTable:** ✨ NOVO
- Tabela responsiva
- Status visual (correto/incorreto/não respondida)
- Formatação de tempo
- Resumo no footer
- Ação de visualização

---

## 🔧 Scripts

```bash
npm run dev      # Desenvolvimento (localhost:3000)
npm run build    # Build para produção
npm run start    # Rodar produção
npm run lint     # Linter
```

---

## 🌐 Integração com API

### **Configuração**

Arquivo: `lib/api.ts`

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### **Endpoints Utilizados**

**Chat:**
- `POST /api/oab/chat` - Enviar mensagem

**Simulado:**
- `GET /api/questoes/materias` - Listar matérias
- `POST /api/questoes/filtrar` - Buscar questões
- `GET /api/questoes/{id}` - Detalhe de questão

---

## 📱 Responsividade

- **Desktop** (>= 1024px): Layout completo
- **Tablet** (768px - 1023px): Layout adaptado
- **Mobile** (< 768px): Layout mobile-first

**Breakpoints Tailwind:**
```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
```

---

## 🎯 Features Implementadas

### **Chat:**
- [x] Interface de mensagens
- [x] Suporte a markdown
- [x] Loading states
- [x] Reset de conversa
- [x] Sugestões de perguntas

### **Simulado:**
- [x] Filtros (matéria, ano, quantidade)
- [x] Busca de questões na API
- [x] Interface de questões
- [x] Marcar respostas
- [x] Ver gabarito
- [x] Cálculo de acertos/erros
- [x] Destacar alternativa correta
- [x] Destacar alternativa errada
- [x] Botão "Explicar com Agente"
- [x] Explicação do gabarito pelo agente (com citações de leis)

### **Navegação:**
- [x] Sidebar lateral com 3 abas
- [x] Highlight de aba ativa
- [x] Navegação entre Chat, Simulado e Dashboard
- [x] Layout responsivo com sidebar fixa
- [x] Logo e versão na sidebar

---

## 🔮 Próximas Features (Futuro)

### **Chat:**
- [ ] Histórico persistente (localStorage)
- [ ] Exportar conversa
- [ ] Compartilhar conversa

### **Simulado:**
- [ ] Timer de prova
- [ ] Salvar progresso
- [ ] Histórico de simulados
- [ ] Estatísticas de desempenho
- [ ] Modo revisão
- [ ] Comentários nas questões

---

## 🐛 Troubleshooting

### **Erro: Cannot connect to API**

**Verificar:**
1. Backend está rodando? (`python backend/main.py`)
2. `.env.local` configurado?
3. URL correta? (`http://localhost:8000`)

---

### **Erro: Module not found**

**Solução:**
```bash
npm install
```

---

### **Página em branco**

**Verificar:**
1. Console do navegador (F12)
2. Terminal do Next.js (erros de build)
3. Versão do Node.js (>= 18)

---

## 📚 Documentação Adicional

- **Next.js:** https://nextjs.org/docs
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Lucide Icons:** https://lucide.dev

---

## 🆘 Suporte

**Problemas comuns:**
- Backend não responde → Verificar se está rodando
- CORS error → Verificar configuração no backend
- Página não carrega → Verificar console do navegador

**Logs úteis:**
```bash
# Next.js
npm run dev

# Network requests
Abrir DevTools (F12) → Network tab
```

---

## ✅ Checklist de Setup

- [ ] Node.js instalado (>= 18)
- [ ] Dependências instaladas (`npm install`)
- [ ] `.env.local` configurado
- [ ] Backend rodando (porta 8000)
- [ ] Frontend rodando (`npm run dev`)
- [ ] Navegação funcionando
- [ ] API respondendo

---

---

## 🎨 Novos Componentes (v2.0)

### **📦 Biblioteca de Componentes**

Consulte `components/README.md` para documentação completa de cada componente.

**Implementados em 2026-01-23:**
1. ✅ QuestionCard - Card completo de questão
2. ✅ RadioGroup - Opções de rádio estilizadas
3. ✅ StatsCard - Cards de estatísticas
4. ✅ ProgressBar - Barras de progresso
5. ✅ QuestionsTable - Tabela de histórico

**Features:**
- Design system unificado
- 7 paletas de cores
- Múltiplos tamanhos
- Animações fluidas
- Totalmente tipados (TypeScript)
- Documentação completa

**Teste os componentes:**
```
http://localhost:3000/componentes
```

---

*Última atualização: 2026-01-23 - v2.0*
