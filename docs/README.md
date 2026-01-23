# 📚 Agente Tutor RAG para Concursos Brasileiros

Pipeline RAG (Retrieval-Augmented Generation) para processamento de leis e documentos jurídicos brasileiros, focado em preparação para concursos públicos.

## 🎯 Funcionalidades

- **Extração de PDF**: Lê arquivos PDF de leis brasileiras
- **Divisão por Artigos**: Usa regex para identificar e separar artigos
- **Embeddings OpenAI**: Gera vetores semânticos usando `text-embedding-3-small`
- **Armazenamento ChromaDB**: Persiste os dados localmente para busca rápida

## 📦 Instalação

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## ⚙️ Configuração

1. Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

2. Adicione sua chave da API OpenAI no arquivo `.env`:
```
OPENAI_API_KEY=sua-chave-aqui
```

## 🚀 Uso

### Uso Básico

```python
from rag_pipeline import LawProcessor

# Inicializar processador
processor = LawProcessor(
    openai_api_key="sua-chave",  # ou use variável de ambiente
    chroma_persist_directory="./chroma_db",
    collection_name="leis_brasileiras"
)

# Processar um PDF de lei
result = processor.process_law_pdf(
    pdf_path="constituicao_federal.pdf",
    law_name="Constituição Federal de 1988",
    additional_metadata={
        "banca": "CESPE",
        "relevancia": "alta",
        "ano_edital": "2024"
    }
)

print(f"Artigos processados: {result['articles_saved']}")
```

### Busca Semântica

```python
# Buscar artigos relevantes
results = processor.search(
    query="direitos e garantias fundamentais",
    top_k=5,
    filter_metadata={"law_name": "Constituição Federal de 1988"}
)

for r in results:
    print(f"Art. {r['metadata']['article_number']}")
    print(f"Relevância: {r['relevance_score']:.2%}")
    print(f"Texto: {r['document'][:200]}...")
    print("-" * 50)
```

### Linha de Comando

```bash
python -m rag_pipeline.law_processor caminho/para/lei.pdf "Nome da Lei"
```

## 📁 Estrutura do Projeto

```
castro_Castros/
├── rag_pipeline/
│   ├── __init__.py
│   └── law_processor.py    # Classe principal
├── chroma_db/              # Dados persistidos (criado automaticamente)
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 API da Classe LawProcessor

### Métodos Principais

| Método | Descrição |
|--------|-----------|
| `process_law_pdf(pdf_path, law_name, metadata)` | Processa PDF completo |
| `search(query, top_k, filter_metadata)` | Busca semântica |
| `get_collection_stats()` | Estatísticas da coleção |
| `delete_law(law_name)` | Remove uma lei |

### Métodos Auxiliares

| Método | Descrição |
|--------|-----------|
| `extract_text_from_pdf(pdf_path)` | Extrai texto do PDF |
| `split_by_articles(text)` | Divide texto em artigos |
| `generate_embedding(text)` | Gera embedding único |
| `generate_embeddings_batch(texts)` | Gera embeddings em lote |

## 📝 Padrões de Artigos Suportados

O regex reconhece os seguintes formatos:

- `Art. 1º` / `Art. 2º` / `Art. 10`
- `Artigo 1º` / `Artigo 2º`
- `Art 1º` (sem ponto)

## 🔜 Próximos Passos

- [ ] Suporte a parágrafos e incisos
- [ ] Identificação de bancas e temas
- [ ] Análise de pontos fracos do candidato
- [ ] Interface de chat com o tutor
- [ ] Geração de questões baseadas nos artigos

## 📄 Licença

Este projeto é para fins educacionais.
