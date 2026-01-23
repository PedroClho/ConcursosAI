# Estratégia de Chunking e Embeddings do RAG

## 📋 Visão Geral

O pipeline RAG usa **estratégias diferentes** de chunking baseadas no **tipo de documento**:

---

## 1️⃣ LEIS (CF, CPC, CPP, CTN)

### Estratégia: **Divisão por Artigos**

**Como funciona:**
- Usa **Regex** para identificar e dividir o texto por artigos
- Cada **artigo individual** vira um chunk separado
- Pattern usado: `r'(Art\.?\s*\d+[º°]?[\.\s\-])'`

**Estrutura de cada chunk:**
```python
{
    "text": "Art. 5º Todos são iguais perante a lei...",
    "metadata": {
        "law_name": "Constituição Federal (CF/88)",
        "article_number": "5",
        "full_reference": "Art. 5º",
        "sigla": "CF",
        "kind": "lei",
        "banca": "FGV",
        "fase": 1,
        # ... outros metadados
    },
    "chunk_id": "Constituicao_Federal_CF_88_art_5_0"
}
```

**Resultados:**
- **CF/88**: ~376 artigos = ~376 embeddings
- **CPC**: ~1.620 artigos = ~1.620 embeddings
- **CPP**: ~911 artigos = ~911 embeddings
- **CTN**: ~216 artigos = ~216 embeddings

**Total de embeddings de leis: ~3.123**

---

## 2️⃣ EDITAIS E COMUNICADOS

### Estratégia: **Baseada no tamanho**

#### Documentos PEQUENOS (≤ 5 páginas)
**Mantém COMPLETO** (1 chunk único)

Exemplo: Comunicado 01 (1 página)
```python
{
    "text": "[TEXTO COMPLETO DO COMUNICADO]",
    "metadata": {
        "document_name": "Comunicado 01 (OAB 1ª fase)",
        "kind": "comunicado",
        "chunk_type": "complete",
        "page_range": "1-1",
        "num_pages": 1,
        # ...
    },
    "chunk_id": "oab_fase1_comunicado_01_complete"
}
```

#### Documentos GRANDES (> 5 páginas)
**Divide POR PÁGINA** (1 página = 1 chunk)

Exemplo: Edital principal (7 páginas)
```python
# Chunk 1 (página 1):
{
    "text": "[TEXTO DA PÁGINA 1]",
    "metadata": {
        "document_name": "Edital (OAB 1ª fase)",
        "kind": "edital",
        "chunk_type": "page",
        "page_number": 1,
        # ...
    },
    "chunk_id": "oab_fase1_edital_01_page_1"
}

# Chunk 2 (página 2):
{
    "chunk_id": "oab_fase1_edital_01_page_2"
    # ...
}
# ... até página 7
```

**Resultados dos seus documentos:**
- **Edital 1** (7 páginas): 7 embeddings
- **Edital Locais** (7 páginas): 7 embeddings
- **Comunicado 1** (1 página): 1 embedding (completo)
- **Comunicado 2** (1 página): 1 embedding (completo)

---

## 3️⃣ NORMATIVOS (Provimento CFOAB)

### Estratégia: **Baseada no tamanho** (igual editais)

Provimento CFOAB (4 páginas):
- ≤ 5 páginas → **1 chunk completo**

```python
{
    "text": "[TEXTO COMPLETO DO PROVIMENTO]",
    "metadata": {
        "document_name": "Provimento CFOAB (regras gerais do Exame de Ordem)",
        "kind": "normativo",
        "chunk_type": "complete",
        "page_range": "1-4",
        "num_pages": 4,
        "document_date": "13 de junho de 2011",
        # ...
    },
    "chunk_id": "oab_norma_provimento_cfoab_complete"
}
```

**Resultado:**
- **Provimento**: 1 embedding (completo)

---

## 📊 Resumo Total de Embeddings

| Tipo | Documentos | Estratégia | Chunks/Embeddings |
|------|-----------|------------|-------------------|
| **Leis** | 4 (CF, CPC, CPP, CTN) | Por artigo | ~3.123 |
| **Editais** | 2 (7 páginas cada) | Por página | 14 |
| **Comunicados** | 2 (1 página cada) | Completo | 2 |
| **Normativos** | 1 (4 páginas) | Completo | 1 |
| **TOTAL** | **9 documentos** | — | **~3.140** |

---

## 🔍 Por que o Edital falhou?

Você está **100% correto**! O edital contém:

```
"A prova objetiva terá a duração de 5 (cinco) horas e será aplicada 
no dia 21 de dezembro de 2025, com início às 13 horas..."
```

**Problema:**
- A data é **dezembro de 2025**
- Estamos em **janeiro de 2026**
- O agente interpretou "próxima prova" como **futura** (2026+)
- Como só tem dados de 2025, respondeu que não encontrou

**Solução:**
1. Ajustar o prompt do agente para considerar datas recentes
2. Adicionar lógica de interpretação temporal
3. Ou buscar por "45º Exame" ao invés de "próxima"

---

## 🎯 Vantagens da Estratégia Atual

### Leis (por artigo):
✅ **Precisão**: Busca retorna o artigo exato
✅ **Citação fácil**: Já tem a referência "Art. Xº"
✅ **Granularidade**: Evita chunks gigantes

### Editais/Comunicados (por página/completo):
✅ **Contexto preservado**: Não quebra informações relacionadas
✅ **Eficiência**: Documentos pequenos mantêm contexto total
✅ **Flexibilidade**: Páginas grandes não misturam tópicos

---

## 🔧 Melhorias Possíveis

1. **Chunking semântico** (por seções/tópicos) em editais grandes
2. **Overlap** entre chunks para preservar contexto entre páginas
3. **Chunk adaptativo** baseado em tokens (limite do modelo)
4. **Metadados mais ricos** (extrair tópicos, datas, locais automaticamente)

---

## 💡 Como visualizar seus chunks?

Execute este script:

```python
from rag_pipeline import LawProcessor

processor = LawProcessor(collection_name="oab_corpus")

# Ver todos os chunks de editais
results = processor.collection.get(
    where={"kind": "edital"},
    limit=50
)

print(f"Total de chunks de editais: {len(results['ids'])}")
for i, (id, doc, meta) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
    print(f"\n[{i+1}] ID: {id}")
    print(f"    Tipo: {meta.get('chunk_type', 'N/A')}")
    print(f"    Página: {meta.get('page_number', meta.get('page_range', 'N/A'))}")
    print(f"    Preview: {doc[:100]}...")
```
