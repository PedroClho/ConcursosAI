# 🗂️ Estrutura do Projeto Castro (OAB Tutor)

## 📋 Visão Geral

Sistema completo de preparação para OAB com:
- 🤖 **Agente Tutor** (LangGraph + LangChain)
- 📚 **RAG Pipeline** (ChromaDB + OpenAI)
- 💾 **Banco de Questões** (2.210 questões reais)
- 🌐 **API Backend** (FastAPI)
- 💻 **Frontend Web** (Next.js + Tailwind)

---

## 🏗️ Estrutura de Diretórios

```
castro_Castros/
│
├── 🤖 agente/                          # AGENTE TUTOR
│   ├── __init__.py                     # Exporta OABTutorAgent
│   ├── oab_agent.py                    # Agente principal (LangGraph)
│   └── tools.py                        # Ferramentas de busca (ChromaDB)
│
├── 📚 rag/                             # RAG PIPELINE
│   ├── __init__.py
│   └── law_processor.py                # Processador de PDFs de leis
│
├── 💾 questoes/                        # BANCO DE QUESTÕES OAB
│   ├── data/                           # Dados brutos e processados
│   │   ├── questoes_raw.json           # Dataset original (HF)
│   │   ├── questoes_processadas.json   # Formato normalizado
│   │   └── metadata.json               # Metadados do dataset
│   ├── database/                       # Banco SQLite (futuro)
│   │   └── oab_questoes.db
│   ├── scripts/                        # Scripts de ingestão
│   │   ├── download_questoes_hf.py     # Download do HF
│   │   ├── processar_questoes.py       # Normalização
│   │   └── criar_banco_questoes.py     # Criar banco SQLite
│   └── CAPTURA_QUESTOES.md             # Documentação
│
├── 🌐 backend/                         # API BACKEND (FastAPI)
│   ├── main.py                         # Servidor principal
│   └── README.md                       # Documentação da API
│
├── 💻 frontend/                        # FRONTEND (Next.js)
│   ├── app/                            # App Router (Next.js 14)
│   │   ├── page.tsx                    # Página principal (chat)
│   │   ├── layout.tsx                  # Layout raiz
│   │   └── globals.css                 # Estilos globais
│   ├── components/                     # Componentes React
│   │   ├── ChatInterface.tsx           # Interface de chat
│   │   ├── Header.tsx                  # Cabeçalho
│   │   └── MessageBubble.tsx           # Bolha de mensagem
│   ├── lib/                            # Utilitários
│   │   └── api.ts                      # Cliente da API
│   └── README.md                       # Setup do frontend
│
├── 📄 data/                            # CORPUS RAG (PDFs)
│   ├── conteudos/                      # Leis em PDF
│   │   ├── cf.pdf                      # Constituição Federal
│   │   ├── CPC_9ed_2016.pdf            # Código Processo Civil
│   │   ├── codigo_de_processo_penal_1ed.pdf
│   │   └── codigo_tributario_nacional_3ed.pdf
│   ├── editais/                        # Editais e regulamentos
│   │   ├── edital1.pdf
│   │   ├── comunicado1.pdf
│   │   └── Provimento_CFOAB.pdf
│   └── corpus_manifest.json            # Manifesto dos documentos
│
├── 💿 chroma_db/                       # CHROMADB (persistente)
│   └── oab_corpus/                     # Coleção com embeddings
│
├── 📜 scripts/                         # SCRIPTS GERAIS
│   ├── ingest_corpus.py                # Ingestão de PDFs no RAG
│   ├── enrich_manifest.py              # Enriquecer manifesto
│   ├── inspect_chunks.py               # Inspecionar chunks
│   └── test_search.py                  # Testar busca RAG
│
├── 📖 docs/                            # DOCUMENTAÇÃO
│   ├── api/                            # Docs da API
│   ├── rag/                            # Docs do RAG
│   │   └── ESTRATEGIA_CHUNKING.md      # Estratégia de chunking
│   ├── FRONTEND_SETUP.md               # Setup do frontend
│   ├── GUIA_RAPIDO.md                  # Guia rápido
│   └── README.md                       # README principal
│
├── 🔧 Arquivos de Configuração
│   ├── .env                            # Variáveis de ambiente
│   ├── .gitignore                      # Git ignore
│   ├── requirements.txt                # Dependências Python
│   ├── COMO_EXECUTAR.md                # Guia de execução
│   ├── ESTRUTURA_PROJETO.md            # Este arquivo
│   └── verificar_config.py             # Verificar configuração
│
└── 🧪 Arquivos de Teste
    ├── chat_tutor.py                   # Chat CLI com agente
    └── example_usage.py                # Exemplo de uso RAG
```

---

## 🔄 Fluxo de Dados

### **1. RAG Pipeline (Leis e Editais)**

```
PDFs (data/conteudos, data/editais)
    ↓
[law_processor.py] → Extrai texto, divide em chunks
    ↓
[OpenAI API] → Gera embeddings
    ↓
[ChromaDB] → Armazena chunks + embeddings
    ↓
[Agente] → Busca semântica
```

### **2. Banco de Questões**

```
Hugging Face (eduagarcia/oab_exams)
    ↓
[download_questoes_hf.py] → Baixa 2.210 questões
    ↓
[processar_questoes.py] → Normaliza estrutura
    ↓
[criar_banco_questoes.py] → SQLite
    ↓
[Backend API] → Endpoints de busca/filtro
    ↓
[Frontend] → Simulados e visualização
```

### **3. Fluxo do Agente Tutor**

```
Usuário (Frontend)
    ↓
[FastAPI Backend] → Recebe pergunta
    ↓
[OABTutorAgent] → Decide qual ferramenta usar
    ↓
    ├─→ [search_laws] → Busca em leis (ChromaDB)
    ├─→ [search_edital] → Busca em editais
    ├─→ [search_provimento] → Busca em regulamentos
    └─→ [search_questoes] → Busca questões (SQLite)
    ↓
[OpenAI GPT-4o-mini] → Gera resposta contextualizada
    ↓
[Frontend] → Exibe resposta com fontes
```

---

## 🛠️ Tecnologias Utilizadas

### **Backend (Python)**
- **FastAPI**: API REST
- **LangChain**: Framework para LLMs
- **LangGraph**: Workflow do agente
- **ChromaDB**: Vector database
- **SQLite**: Banco relacional (questões)
- **PyPDF**: Extração de texto de PDFs
- **OpenAI API**: Embeddings + LLM

### **Frontend (TypeScript/JavaScript)**
- **Next.js 14**: Framework React
- **Tailwind CSS**: Estilização
- **Axios**: Cliente HTTP
- **React Markdown**: Renderização de markdown
- **Lucide React**: Ícones

---

## 📦 Módulos Principais

### **1. Agente (`agente/`)**

**Responsabilidade**: Orquestração do tutor inteligente

- `oab_agent.py`: Lógica principal do agente (LangGraph)
  - System prompt especializado
  - Workflow de decisão
  - Integração com LLM
  
- `tools.py`: Ferramentas de busca
  - `search_laws()`: Busca em leis por artigo
  - `search_edital()`: Busca em editais
  - `search_provimento()`: Busca em regulamentos
  - `get_database_stats()`: Estatísticas do RAG

### **2. RAG (`rag/`)**

**Responsabilidade**: Pipeline de processamento e busca em documentos

- `law_processor.py`: Classe principal
  - `process_law_pdf()`: Processa leis (divide por artigos)
  - `process_non_law_document()`: Processa editais/comunicados
  - `search()`: Busca semântica no ChromaDB
  - `add_documents()`: Adiciona documentos ao banco

### **3. Questões (`questoes/`)**

**Responsabilidade**: Gerenciamento do banco de questões

- **Scripts**:
  - `download_questoes_hf.py`: Download do Hugging Face
  - `processar_questoes.py`: Normalização de dados
  - `criar_banco_questoes.py`: Criação do banco SQLite

- **Dados**:
  - `questoes_raw.json`: Dados originais (2.210 questões)
  - `questoes_processadas.json`: Dados normalizados
  - `oab_questoes.db`: Banco SQLite

### **4. Backend (`backend/`)**

**Responsabilidade**: API REST para frontend

**Endpoints**:
- `POST /api/oab/chat`: Conversa com agente
- `POST /api/oab/search`: Busca direta no RAG
- `GET /api/oab/stats`: Estatísticas do sistema
- `GET /api/questoes`: Listar questões (futuro)
- `POST /api/questoes/filtrar`: Filtrar questões (futuro)

### **5. Frontend (`frontend/`)**

**Responsabilidade**: Interface web do usuário

**Páginas**:
- `/`: Chat com agente tutor
- `/simulado`: Simulado de questões (futuro)

**Componentes**:
- `ChatInterface`: Interface principal de chat
- `Header`: Cabeçalho com logo e reset
- `MessageBubble`: Bolha de mensagem

---

## 🚀 Como Executar

### **1. Setup Inicial**

```powershell
# Verificar configuração
python verificar_config.py

# Instalar dependências
pip install -r requirements.txt
```

### **2. Ingestão de Dados (RAG)**

```powershell
# Processar PDFs de leis e editais
python scripts/ingest_corpus.py
```

### **3. Download de Questões**

```powershell
# Baixar dataset do Hugging Face
python questoes/scripts/download_questoes_hf.py

# Processar questões
python questoes/scripts/processar_questoes.py
```

### **4. Rodar Backend**

```powershell
python backend/main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### **5. Rodar Frontend**

```powershell
cd frontend
npm install
npm run dev
# App: http://localhost:3000
```

---

## 📝 Próximas Implementações

- [ ] Criar banco SQLite de questões
- [ ] Endpoints de questões no backend
- [ ] Página de simulado no frontend
- [ ] Ferramenta do agente para explicar questões
- [ ] Filtros por matéria, ano, dificuldade
- [ ] Sistema de estatísticas de desempenho
- [ ] Modo de revisão espaçada

---

## 🔐 Variáveis de Ambiente

### **`.env` (raiz)**
```bash
OPENAI_API_KEY=sk-...
```

### **`frontend/.env.local`**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📚 Documentação Completa

- **Execução**: `COMO_EXECUTAR.md`
- **Questões**: `questoes/CAPTURA_QUESTOES.md`
- **Frontend**: `docs/FRONTEND_SETUP.md`
- **RAG**: `docs/rag/ESTRATEGIA_CHUNKING.md`
- **API**: `backend/README.md`

---

## 🆘 Problemas Comuns

Consulte `verificar_config.py` para diagnóstico automático de:
- ✅ Chave OpenAI configurada
- ✅ ChromaDB inicializado
- ✅ Dependências instaladas
- ✅ Estrutura de pastas correta
