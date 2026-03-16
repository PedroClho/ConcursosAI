# 🎓 Atlas Concursos - Plataforma de Preparação para Concursos Públicos

> **Sistema inteligente com RAG, Agente Tutor, Autenticação e Banco de Questões para aprovação em concursos**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%2B%20DB-green.svg)](https://supabase.com)

---

## 📋 Sobre o Projeto

**Atlas Concursos** é uma plataforma completa de estudos para concursos públicos (OAB e outros), combinando:

- 🤖 **Agente Tutor Inteligente** (LangGraph + LangChain)
- 📚 **RAG com 17 Leis Brasileiras** organizadas por eixos
- 💾 **2.210 Questões Reais** (OAB 2010-2018)
- 🎯 **Simulados Personalizados**
- 📊 **Análise de Desempenho**
- ☁️ **Supabase PostgreSQL + pgvector**
- 🔐 **Autenticação Completa** (Email/Senha + Google OAuth)
- 💳 **Sistema de Planos** (Free, Pro, Premium) - Em breve

### 📖 Organização do Conteúdo

**Eixo Ético** (CRÍTICO): EAOAB, Código de Ética, Regulamento  
**Eixo Fundamental** (ALTO): CF, CC, CP, CPC, CPP, CLT, CTN, CDC  
**Eixo Administrativo** (MÉDIO): Licitações, Improbidade, Processo Adm, etc.

**Total**: ~8.100 artigos indexados | ~8.500 embeddings vetoriais

---

## 🆕 O Que Mudou Recentemente

### **v2.0 - Sistema de Autenticação Completo** (Março 2026)

#### ✨ Novas Funcionalidades
- **Supabase Auth**: Sistema completo de autenticação integrado
- **Login/Cadastro**: Interface moderna com email e senha
- **Proteção de Rotas**: Middleware automático para rotas privadas
- **Perfis de Usuário**: Criação automática com trigger
- **Sistema de Chats**: Persistência de conversas (limite de 3 por usuário)
- **Estatísticas**: Dashboard com métricas de estudo por usuário

#### 🗄️ Banco de Dados
- **Migração para Supabase PostgreSQL**: De ChromaDB local para cloud
- **5 Novas Tabelas**: `profiles`, `chats`, `messages`, `user_statistics`, `user_subject_statistics`
- **Row Level Security**: Isolamento de dados por usuário
- **pgvector**: Vector search para RAG (~8.500 embeddings)
- **Triggers**: Automação de criação de perfil e limites

#### 🔜 Próximos Passos
- **Google OAuth**: Login social (planejado)
- **Stripe**: Sistema de planos pagos (planejado)
- **3 Tiers**: Free, Pro (R$ 29,90/mês), Premium (R$ 59,90/mês)

📖 **Documentação completa**: `docs/AUTENTICACAO_E_PLANOS.md`

---

## 🚀 Quick Start

### **1. Clone e Instale**

```powershell
git clone <seu-repo>
cd castro_Castros

# Instalar dependências Python
pip install -r requirements.txt

# Configurar .env
copy env_template.txt .env
# Edite .env e adicione sua OPENAI_API_KEY
```

### **2. Verificar Configuração**

```powershell
python verificar_config.py
```

### **3. Configurar Banco de Dados (Supabase)**

```powershell
# 1. Criar projeto no Supabase (https://app.supabase.com)
# 2. Copiar URL e Keys para .env

# 3. Executar schema SQL no Supabase SQL Editor
# Copie todo o conteúdo de supabase_schema.sql e execute
```

**Schema inclui**:
- ✅ Tabelas: `profiles`, `chats`, `messages`, `user_statistics`, `user_subject_statistics`
- ✅ Row Level Security (RLS) em todas as tabelas
- ✅ Trigger automático de criação de perfil
- ✅ Limite de 3 chats por usuário
- ✅ Realtime habilitado para chats e mensagens

### **4. Processar RAG por Eixos (RECOMENDADO)**

```powershell
# Opção 1: Menu interativo
python scripts/processar_tudo.py

# Opção 2: Processar por etapas
python scripts/verify_files.py              # Verificar PDFs
python scripts/enrich_manifest_v2.py        # Extrair metadados

# Processar cada eixo
python scripts/ingest_eixo_etico.py
python scripts/ingest_eixo_fundamental_novos.py
python scripts/ingest_eixo_administrativo.py

# Migrar para Supabase
python scripts/migrate_to_supabase.py --eixo etico
python scripts/migrate_to_supabase.py --eixo fundamental
python scripts/migrate_to_supabase.py --eixo administrativo
```

**Guia completo**: Veja `GUIA_PROCESSAMENTO_EIXOS.md`

### **5. Rodar Backend**

```powershell
python backend/main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### **6. Rodar Frontend**

```powershell
cd frontend
npm install
npm run dev
# App: http://localhost:3000
```

---

## 🏗️ Arquitetura

### **Visão Geral**

```
                    ┌──────────────────────┐
                    │   Usuário (Browser)  │
                    └──────────┬───────────┘
                               │
                               ↓
        ┌──────────────────────────────────────────┐
        │      Frontend (Next.js 15 + SSR)         │
        │  ─────────────────────────────────────   │
        │  • App Router (React Server Components)  │
        │  • Middleware de Autenticação            │
        │  • Supabase Client (Auth + DB)           │
        │  • Tailwind + shadcn/ui                  │
        └────────┬─────────────────────┬───────────┘
                 │                     │
                 │ HTTP                │ Supabase Client
                 ↓                     ↓
    ┌────────────────────┐   ┌─────────────────────────┐
    │  Backend (FastAPI) │   │  Supabase Cloud         │
    │  ────────────────  │   │  ─────────────────────  │
    │  • JWT Validation  │   │  • PostgreSQL + RLS     │
    │  • CORS            │   │  • Auth (JWT + OAuth)   │
    │  • Protected APIs  │   │  • pgvector (RAG)       │
    └────────┬───────────┘   │  • Realtime             │
             │               │  • Storage              │
             │               └─────────────────────────┘
             │
             ├─→ 🤖 Agente Tutor (LangGraph)
             │       ├─→ OpenAI GPT-4o-mini
             │       └─→ Tools (Search RAG)
             │
             ├─→ 📚 RAG Pipeline (Supabase pgvector)
             │       ├─→ Law Processor
             │       ├─→ OpenAI Embeddings (1536D)
             │       └─→ Vector Search (cosine similarity)
             │
             └─→ 💾 Banco de Questões (SQLite)
                     ├─→ 2.210 questões OAB
                     └─→ Filtros avançados
```

### **Fluxo de Autenticação**

```
1. Usuário acessa /login
   ↓
2. Insere email/senha OU clica "Login com Google"
   ↓
3. Supabase Auth valida credenciais
   ↓
4. JWT token armazenado em cookie (httpOnly)
   ↓
5. Middleware verifica token em cada request
   ↓
6. Se válido → acessa rota protegida
   Se inválido → redireciona para /login
   ↓
7. Backend recebe token no header Authorization
   ↓
8. FastAPI valida token com Supabase
   ↓
9. Se válido → processa request
   Se inválido → retorna 401
```

---

## 📁 Estrutura do Projeto

```
castro_Castros/
├── agente/                 # 🤖 Agente Tutor (LangGraph)
├── rag/                    # 📚 RAG Pipeline (ChromaDB)
├── questoes/               # 💾 Banco de Questões
│   ├── data/               # Dados (JSON)
│   ├── database/           # SQLite
│   └── scripts/            # Processamento
├── backend/                # 🌐 API (FastAPI)
├── frontend/               # 💻 UI (Next.js)
├── data/                   # 📄 PDFs (leis, editais)
├── chroma_db/              # 💿 ChromaDB (persistente)
├── scripts/                # 🔧 Scripts gerais
└── docs/                   # 📖 Documentação
```

**Documentação detalhada**: `ESTRUTURA_PROJETO.md`

---

## 🎯 Funcionalidades

### ✅ Implementadas

#### **Core**
- [x] **RAG com Leis**: Busca semântica em 17 leis brasileiras (Supabase pgvector)
- [x] **Agente Tutor**: Conversa inteligente com citação de fontes (LangGraph)
- [x] **Chat Interface**: UI moderna com dark theme
- [x] **Editais**: Informações sobre datas, locais e regras
- [x] **Download de Questões**: 2.210 questões do Hugging Face
- [x] **Processamento**: Normalização e estruturação de dados

#### **Autenticação** 🔐
- [x] **Supabase Auth**: Sistema de autenticação completo
- [x] **Email/Senha**: Login e cadastro tradicional
- [x] **Middleware**: Proteção automática de rotas privadas
- [x] **JWT Validation**: Backend valida tokens do Supabase
- [x] **Perfil Automático**: Criado via trigger ao cadastrar
- [x] **Row Level Security**: Dados isolados por usuário

#### **Dashboard e Estatísticas**
- [x] **Estatísticas Gerais**: Questões respondidas, acertos, horas de estudo
- [x] **Estatísticas por Matéria**: Desempenho detalhado
- [x] **Sistema de Chats**: Até 3 conversas simultâneas com o tutor
- [x] **Histórico de Mensagens**: Persistido no Supabase

### 🔄 Em Desenvolvimento

- [ ] **Google OAuth**: Login com conta Google
- [ ] **Sistema de Planos**: Free, Pro (R$ 29,90), Premium (R$ 59,90)
- [ ] **Stripe Integration**: Pagamentos recorrentes
- [ ] **Limites por Plano**: Controle de uso de perguntas
- [ ] **Banco SQLite**: Armazenamento otimizado de questões
- [ ] **API de Questões**: Endpoints de busca/filtro
- [ ] **Simulados**: Página de prática com filtros
- [ ] **Explicações**: Agente comenta questões

### 🔮 Roadmap Futuro

- [ ] **Revisão Espaçada**: Sistema de memorização
- [ ] **Flashcards**: Artigos importantes
- [ ] **Plano de Estudos**: Cronograma personalizado
- [ ] **Multiplataforma**: Suporte a outros concursos (PF, PM, etc)
- [ ] **Portal de Pagamento**: Gerenciamento de assinatura
- [ ] **Análise com IA**: Recomendações personalizadas de estudo

---

## 🛠️ Tecnologias

### **Backend**
- **Python 3.10+**
- **FastAPI**: API REST
- **LangChain**: Framework para LLMs
- **LangGraph**: Workflow de agentes
- **Supabase**: PostgreSQL + pgvector + Auth
- **OpenAI API**: GPT-4o-mini + Embeddings
- **SQLite**: Banco relacional (questões)

### **Frontend**
- **Next.js 15**: React framework (App Router)
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **shadcn/ui**: Componentes UI
- **Supabase SSR**: Autenticação (`@supabase/ssr`)
- **React Markdown**: Rendering

### **Autenticação & Pagamentos**
- **Supabase Auth**: Email/Senha + OAuth
- **Google OAuth**: Login social (planejado)
- **Stripe**: Pagamentos e assinaturas (planejado)

### **Banco de Dados**
- **Supabase PostgreSQL**: Banco principal
- **pgvector**: Extensão para vector search (RAG)
- **Row Level Security**: Isolamento de dados por usuário
- **Realtime**: Sincronização automática de chats

---

## 📊 Banco de Dados (Supabase PostgreSQL)

### **Tabelas Implementadas**

#### **Autenticação e Perfil**
- **`auth.users`** (nativa Supabase): Usuários e credenciais
- **`profiles`**: Perfil do usuário (nome, avatar, objetivo)
  - RLS: Usuário só acessa próprio perfil
  - Criado automaticamente via trigger

#### **Chat com Tutor IA**
- **`chats`**: Conversas do usuário (limite de 3 por usuário)
  - RLS: Usuário só acessa próprios chats
- **`messages`**: Mensagens de cada chat (user/assistant)
  - RLS: Usuário só acessa mensagens de seus chats

#### **Estatísticas e Progresso**
- **`user_statistics`**: Estatísticas gerais (questões, acertos, horas de estudo, sequências)
- **`user_subject_statistics`**: Estatísticas por matéria
  - RLS: Usuário só acessa próprias estatísticas

#### **RAG (Vector Search)**
- **`oab_corpus`**: Embeddings das leis (pgvector)
  - ~8.500 chunks indexados
  - 17 leis brasileiras organizadas por eixos

### **Triggers e Automações**
- ✅ **`handle_new_user()`**: Cria perfil e estatísticas ao cadastrar
- ✅ **`enforce_chat_limit_trigger`**: Limita 3 chats por usuário
- ✅ **Realtime**: Habilitado para `chats` e `messages`

### **Schema Completo**
Veja: `supabase_schema.sql`

---

## 📊 Dados

### **RAG (Supabase pgvector)**
- ✅ Constituição Federal (CF)
- ✅ Código de Processo Civil (CPC)
- ✅ Código de Processo Penal (CPP)
- ✅ Código Tributário Nacional (CTN)
- ✅ Editais FGV (2025)
- ✅ Provimento CFOAB
- ✅ + 11 outras leis organizadas por eixos

### **Questões (Hugging Face)**
- **Dataset**: `eduagarcia/oab_exams`
- **Total**: 2.210 questões
- **Período**: 2010-2018
- **Fase**: 1ª fase
- **Matérias**: 17+ disciplinas

---

## 🗄️ Estrutura do Banco de Dados

### **Diagrama de Relacionamentos**

```
┌─────────────────┐
│   auth.users    │ (Supabase Auth - Nativa)
│  ─────────────  │
│  • id (UUID)    │
│  • email        │
│  • password     │
└────────┬────────┘
         │
         │ (1:1)
         ↓
┌─────────────────┐
│    profiles     │ Perfil do Usuário
│  ─────────────  │
│  • id           │ → FK: auth.users
│  • full_name    │
│  • avatar_url   │
│  • objective    │
└────────┬────────┘
         │
         ├─────────────────────┐
         │ (1:N)               │ (1:1)
         ↓                     ↓
┌─────────────────┐   ┌──────────────────────┐
│     chats       │   │  user_statistics     │
│  ─────────────  │   │  ──────────────────  │
│  • id           │   │  • user_id           │ → FK: auth.users
│  • user_id      │   │  • questoes_resp     │
│  • title        │   │  • acertos           │
│  • created_at   │   │  • horas_estudo      │
└────────┬────────┘   │  • sequencia_atual   │
         │            │  • melhor_sequencia  │
         │ (1:N)      │  • simulados_feitos  │
         ↓            └──────────────────────┘
┌─────────────────┐            │
│    messages     │            │ (1:N)
│  ─────────────  │            ↓
│  • id           │   ┌──────────────────────────┐
│  • chat_id      │   │ user_subject_statistics  │
│  • role         │   │  ──────────────────────  │
│  • content      │   │  • id                    │
│  • created_at   │   │  • user_id               │ → FK: auth.users
└─────────────────┘   │  • subject_name          │
                      │  • questoes_respondidas  │
                      │  • acertos               │
                      └──────────────────────────┘
```

### **Regras de Negócio Implementadas**

1. **Limite de Chats**: Máximo de 3 chats por usuário (trigger `enforce_chat_limit_trigger`)
2. **Criação Automática**: Perfil e estatísticas criados automaticamente ao cadastrar (trigger `handle_new_user`)
3. **Cascade Delete**: Ao deletar usuário, todos os dados relacionados são removidos
4. **Row Level Security**: Cada usuário só acessa seus próprios dados
5. **Realtime**: Chats e mensagens sincronizam em tempo real

### **Próximas Tabelas (Planejadas)**

```sql
-- Sistema de Planos (Stripe)
subscriptions (
  user_id, tier, status, stripe_customer_id,
  stripe_subscription_id, questions_limit,
  questions_used_this_month, current_period_end
)

-- Histórico de Pagamentos
payment_history (
  user_id, subscription_id, stripe_invoice_id,
  amount_paid, currency, status
)
```

Veja o plano completo em: `docs/AUTENTICACAO_E_PLANOS.md`

---

## 🔐 Configuração

### **`.env` (raiz)**
```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Supabase
SUPABASE_URL=https://[SEU_PROJETO].supabase.co
SUPABASE_SERVICE_KEY=eyJh...
SUPABASE_ANON_KEY=eyJh...
```

### **`frontend/.env.local`**
```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://[SEU_PROJETO].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJh...
SUPABASE_SERVICE_ROLE_KEY=eyJh... # Para webhooks

# Site
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Stripe (opcional - para planos pagos)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO=price_...
NEXT_PUBLIC_STRIPE_PRICE_ID_PREMIUM=price_...
```

---

## 📚 Documentação

### **Como Usar**
- **Início Rápido**: `COMO_EXECUTAR.md`
- **Guia de Início**: `GUIA_INICIO.md`

### **Autenticação e Planos** ⭐ NOVO
- **Autenticação e Planos**: `docs/AUTENTICACAO_E_PLANOS.md` - Guia completo de auth + Stripe

### **Migração Supabase**
- **Resumo Executivo**: `RESUMO_EXECUTIVO.md` - Leia isto primeiro!
- **Guia Rápido**: `GUIA_RAPIDO_MIGRACAO.md` - 20 minutos para migrar
- **Inventário RAG**: `INVENTARIO_RAG_COMPLETO.md` - Todo o conteúdo
- **Guia Completo**: `MIGRACAO_SUPABASE.md` - Documentação detalhada (800+ linhas)
- **Resumo Técnico**: `RESUMO_RAG_SUPABASE.md`

### **Estrutura e Técnica**
- **Estrutura**: `ESTRUTURA_PROJETO.md`
- **Questões**: `questoes/CAPTURA_QUESTOES.md`
- **Frontend**: `docs/FRONTEND_SETUP.md`
- **RAG**: `docs/rag/ESTRATEGIA_CHUNKING.md`
- **API**: `backend/README.md`

---

## 🧪 Testando

### **Backend**

```powershell
# Testar configuração
python verificar_config.py

# Testar busca no RAG
python scripts/test_search.py

# Testar agente (CLI)
python chat_tutor.py
```

### **Frontend**

```powershell
cd frontend
npm run build  # Verificar erros de build
npm run lint   # Verificar erros de linting
```

### **Banco de Dados (Supabase)**

```sql
-- Verificar se tabelas foram criadas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Verificar RLS
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public';

-- Verificar políticas RLS
SELECT * FROM pg_policies WHERE schemaname = 'public';

-- Contar usuários
SELECT COUNT(*) FROM auth.users;

-- Verificar perfis criados
SELECT p.*, u.email FROM profiles p
JOIN auth.users u ON u.id = p.id;

-- Verificar estatísticas
SELECT * FROM user_statistics;
```

---

## 📈 Status do Projeto

```
┌──────────────────────────┬──────────┐
│ Módulo                   │ Status   │
├──────────────────────────┼──────────┤
│ RAG Pipeline (Supabase)  │ ✅ 100%  │
│ Agente Tutor             │ ✅ 100%  │
│ Backend API              │ ✅ 90%   │
│ Frontend Chat            │ ✅ 100%  │
│ Autenticação (Email/PW)  │ ✅ 100%  │
│ Google OAuth             │ 📋 0%    │
│ Sistema de Planos        │ 📋 0%    │
│ Stripe Integration       │ 📋 0%    │
│ Download Questões        │ ✅ 100%  │
│ Banco de Questões        │ 🔄 30%   │
│ Simulados                │ ⏳ 0%    │
│ Estatísticas             │ 🔄 50%   │
└──────────────────────────┴──────────┘

Legenda: ✅ Completo | 🔄 Em Progresso | 📋 Planejado | ⏳ Não Iniciado
```

---

## 🤝 Contribuindo

Este é um projeto em desenvolvimento ativo. Sugestões e melhorias são bem-vindas!

### **Áreas para Contribuir**
- 📚 Adicionar mais conteúdos (leis, jurisprudência)
- 🎯 Melhorar estratégias de chunking
- 💡 Implementar novas features (flashcards, revisão espaçada)
- 🐛 Reportar bugs e problemas
- 📖 Melhorar documentação

---

## 📝 Licença

[Especifique sua licença aqui]

---

## 🆘 Suporte

### **Problemas Comuns**

1. **Erro de API Key**
   ```powershell
   python verificar_config.py
   ```

2. **Erro de autenticação no frontend**
   - Verifique se as variáveis `NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_ANON_KEY` estão corretas
   - Verifique se o schema SQL foi executado no Supabase
   - Confirme que RLS está habilitado nas tabelas

3. **Usuário não consegue fazer login**
   - Verifique se o email foi confirmado (check inbox)
   - Teste com `supabase.auth.getUser()` no console do navegador
   - Verifique logs no Supabase Dashboard → Authentication → Logs

4. **Erro "Chat limit reached"**
   - Usuário já tem 3 chats criados
   - Delete um chat existente antes de criar novo
   - Ou ajuste o limite no trigger `check_chat_limit()`

5. **Backend não valida token**
   - Verifique se `SUPABASE_SERVICE_KEY` está no `.env` da raiz
   - Confirme que o token está sendo enviado no header `Authorization: Bearer <token>`

6. **Frontend não conecta ao backend**
   - Verifique se backend está rodando (porta 8000)
   - Verifique `NEXT_PUBLIC_API_URL` em `frontend/.env.local`
   - Confirme CORS no backend (`main.py`)

---

## 🎓 Sobre

Desenvolvido para ajudar candidatos a passar no Exame de Ordem da OAB, combinando tecnologias modernas de IA com conteúdo jurídico de qualidade.

**Bons estudos e boa prova! 🚀**
