# 🚀 Guia Rápido - Ingestão do Corpus OAB

## O que você precisa (ChromaDB)

**✅ Nada!** O ChromaDB funciona localmente sem configuração prévia. Ele vai criar automaticamente:
- O diretório `./chroma_db/` para persistir os dados
- A coleção `oab_corpus` na primeira execução

## Passo a Passo

### 1️⃣ Configurar API OpenAI

Crie um arquivo `.env` na raiz do projeto:

```bash
# No Windows PowerShell:
copy env_template.txt .env

# Ou crie manualmente e adicione:
OPENAI_API_KEY=sua-chave-aqui
```

**Como obter a chave:**
- Acesse: https://platform.openai.com/api-keys
- Crie uma nova chave
- Cole no arquivo `.env`

### 2️⃣ Executar Ingestão

```bash
python ingest_corpus.py
```

**O que vai acontecer:**
- ✅ Processa 4 leis (~3,123 artigos detectados)
- ✅ Processa 5 editais/comunicados/normativos
- ✅ Gera embeddings usando OpenAI
- ✅ Salva tudo no ChromaDB local
- ⏱️ Tempo estimado: 5-10 minutos (depende da API)

### 3️⃣ Testar Busca Semântica

```bash
python test_search.py
```

Testa 5 queries de exemplo:
- Direitos fundamentais (CF)
- Prazos processuais (CPC/CPP)
- Data da prova (Edital)
- Inscrição no exame (Provimento)
- Prisão em flagrante (CPP)

## 📊 Estrutura Gerada

```
castro_Castros/
├── chroma_db/              # ← Criado automaticamente
│   └── oab_corpus/         # Coleção com os dados
├── ingestion_log.json      # ← Log da ingestão
└── ...
```

## 🔍 Usando a Busca

```python
from rag_pipeline import LawProcessor

processor = LawProcessor(
    chroma_persist_directory="./chroma_db",
    collection_name="oab_corpus"
)

# Busca geral
results = processor.search("direitos fundamentais", top_k=5)

# Busca filtrada por tipo
results = processor.search(
    "data da prova",
    top_k=3,
    filter_metadata={"kind": "edital"}
)

# Busca filtrada por lei específica
results = processor.search(
    "prazo recurso",
    top_k=5,
    filter_metadata={"sigla": "CPC"}
)
```

## 🏷️ Filtros Disponíveis

Você pode filtrar por:
- `kind`: "lei", "edital", "comunicado", "normativo"
- `sigla`: "CF", "CPC", "CPP", "CTN"
- `banca`: "FGV"
- `fase`: 1
- `tags`: (use busca por string, ex: "direito_constitucional")

## 📈 Estatísticas

```python
from rag_pipeline import LawProcessor

processor = LawProcessor(collection_name="oab_corpus")
stats = processor.get_collection_stats()
print(stats)
```

## ❓ Troubleshooting

### Erro: "API Key da OpenAI não fornecida"
→ Crie o arquivo `.env` com `OPENAI_API_KEY=sua-chave`

### Erro: "No module named 'openai'"
→ Execute: `pip install -r requirements.txt`

### Extração de baixa qualidade
→ Alguns PDFs podem ser imagens/OCR ruim. O script avisa quais são.

### Quero reprocessar tudo
→ Delete a pasta `chroma_db/` e execute `ingest_corpus.py` novamente

## 💰 Custos OpenAI

**Estimativa para o corpus OAB completo:**
- ~2.1 milhões de caracteres
- Modelo: `text-embedding-3-small` ($0.02 / 1M tokens)
- **Custo estimado: ~$0.01 - $0.02** (muito barato!)

## ⏭️ Próximos Passos

1. ✅ Ingestão funcionando
2. 🔜 Criar o Agente Tutor (chat que responde baseado no corpus)
3. 🔜 Sistema de análise de pontos fracos
4. 🔜 Gerador de questões personalizadas
