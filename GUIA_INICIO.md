# 🚀 Guia de Início Rápido

## Passo a Passo para Rodar

### 1. Criar arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com sua chave da OpenAI:

```
OPENAI_API_KEY=sk-proj-...
```

### 2. Rodar a Ingestão

```bash
python scripts/ingest_corpus.py
```

Isso vai:
- ✅ Processar ~3,123 artigos das leis
- ✅ Processar editais e comunicados
- ✅ Criar o banco vetorial em `chroma_db/`
- ⏱️ Levar ~5-10 minutos

### 3. Testar a Busca

```bash
python scripts/test_search.py
```

## ⚠️ Se der erro

**Erro: "API Key não fornecida"**
→ Crie o arquivo `.env` conforme passo 1

**Erro: "cannot import LawProcessor"**
→ Execute: `pip install -r requirements.txt`

**Quero recomeçar do zero**
→ Delete a pasta `chroma_db/` e rode novamente

## 📊 O que você tem após a ingestão

- ✅ ~3,123 artigos indexados (CF, CPC, CPP, CTN)
- ✅ Busca semântica pronta
- ✅ Filtros por lei, tipo de documento, etc.

Pronto para usar!
