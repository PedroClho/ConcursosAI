# 🎓 Castro - Plataforma de Preparação para OAB

> **Sistema inteligente com RAG, Agente Tutor e Banco de Questões para aprovação na OAB**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com)

---

## 📋 Sobre o Projeto

**Castro** é uma plataforma completa de estudos para o Exame de Ordem da OAB, combinando:

- 🤖 **Agente Tutor Inteligente** (LangGraph + LangChain)
- 📚 **RAG com Leis Brasileiras** (CF, CPC, CPP, CTN)
- 💾 **2.210 Questões Reais** (OAB 2010-2018)
- 🎯 **Simulados Personalizados**
- 📊 **Análise de Desempenho**

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

### **3. Ingestão de Dados**

```powershell
# RAG: Processar leis e editais
python scripts/ingest_corpus.py

# Questões: Baixar dataset do Hugging Face
python questoes/scripts/download_questoes_hf.py
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

## 🏗️ Arquitetura

```
┌─────────────┐
│   Frontend  │ Next.js + Tailwind
│  (Next.js)  │
└──────┬──────┘
       │ HTTP
       ↓
┌─────────────┐
│   Backend   │ FastAPI + CORS
│  (FastAPI)  │
└──────┬──────┘
       │
       ├─→ 🤖 Agente Tutor (LangGraph)
       │       ├─→ OpenAI GPT-4o-mini
       │       └─→ Tools (Search)
       │
       ├─→ 📚 RAG Pipeline (ChromaDB)
       │       ├─→ Law Processor
       │       ├─→ OpenAI Embeddings
       │       └─→ Vector Search
       │
       └─→ 💾 Banco de Questões (SQLite)
               ├─→ 2.210 questões
               └─→ Filtros avançados
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

- [x] **RAG com Leis**: Busca semântica em CF, CPC, CPP, CTN
- [x] **Agente Tutor**: Conversa inteligente com citação de fontes
- [x] **Chat Interface**: UI moderna com dark theme
- [x] **Editais**: Informações sobre datas, locais e regras
- [x] **Download de Questões**: 2.210 questões do Hugging Face
- [x] **Processamento**: Normalização e estruturação de dados

### 🔄 Em Desenvolvimento

- [ ] **Banco SQLite**: Armazenamento otimizado de questões
- [ ] **API de Questões**: Endpoints de busca/filtro
- [ ] **Simulados**: Página de prática com filtros
- [ ] **Explicações**: Agente comenta questões
- [ ] **Estatísticas**: Análise de desempenho

### 🔮 Roadmap

- [ ] **Revisão Espaçada**: Sistema de memorização
- [ ] **Flashcards**: Artigos importantes
- [ ] **Plano de Estudos**: Cronograma personalizado
- [ ] **Multiplataforma**: Suporte a outros concursos

---

## 🛠️ Tecnologias

### **Backend**
- **Python 3.10+**
- **FastAPI**: API REST
- **LangChain**: Framework para LLMs
- **LangGraph**: Workflow de agentes
- **ChromaDB**: Vector database
- **OpenAI API**: GPT-4o-mini + Embeddings
- **SQLite**: Banco relacional

### **Frontend**
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **React Markdown**: Rendering

---

## 📊 Dados

### **RAG (ChromaDB)**
- ✅ Constituição Federal (CF)
- ✅ Código de Processo Civil (CPC)
- ✅ Código de Processo Penal (CPP)
- ✅ Código Tributário Nacional (CTN)
- ✅ Editais FGV (2025)
- ✅ Provimento CFOAB

### **Questões (Hugging Face)**
- **Dataset**: `eduagarcia/oab_exams`
- **Total**: 2.210 questões
- **Período**: 2010-2018
- **Fase**: 1ª fase
- **Matérias**: 17+ disciplinas

---

## 🔐 Configuração

### **`.env` (raiz)**
```bash
OPENAI_API_KEY=sk-...
```

### **`frontend/.env.local`**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📚 Documentação

- **Início Rápido**: `COMO_EXECUTAR.md`
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

---

## 📈 Status do Projeto

```
┌─────────────────────┬──────────┐
│ Módulo              │ Status   │
├─────────────────────┼──────────┤
│ RAG Pipeline        │ ✅ 100%  │
│ Agente Tutor        │ ✅ 100%  │
│ Backend API         │ ✅ 90%   │
│ Frontend Chat       │ ✅ 100%  │
│ Download Questões   │ ✅ 100%  │
│ Banco de Questões   │ 🔄 30%   │
│ Simulados           │ ⏳ 0%    │
│ Estatísticas        │ ⏳ 0%    │
└─────────────────────┴──────────┘
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

2. **ChromaDB vazio**
   ```powershell
   python scripts/ingest_corpus.py
   ```

3. **Frontend não conecta**
   - Verifique se backend está rodando (porta 8000)
   - Verifique `frontend/.env.local`

---

## 🎓 Sobre

Desenvolvido para ajudar candidatos a passar no Exame de Ordem da OAB, combinando tecnologias modernas de IA com conteúdo jurídico de qualidade.

**Bons estudos e boa prova! 🚀**
