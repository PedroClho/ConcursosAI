# 📜 Scripts - Processamento RAG por Eixos

## 🎯 Script Master

### `processar_tudo.py`
**Menu interativo para processar tudo ou por partes**

```bash
python scripts/processar_tudo.py
```

Menu permite:
- [0] Executar tudo automaticamente
- [1-4] Processar por fase/eixo
- [5] Apenas testes

---

## 🔧 Scripts de Preparação

### `verify_files.py`
Verifica se todos os PDFs existem

```bash
python scripts/verify_files.py
```

Mostra:
- ✓ Arquivos encontrados
- ✗ Arquivos faltando
- Tamanho de cada PDF

### `enrich_manifest_v2.py`
Extrai metadados dos PDFs

```bash
python scripts/enrich_manifest_v2.py
```

Extrai:
- Número de páginas
- Número de artigos detectados
- Tamanho do arquivo
- Qualidade da extração

---

## 📚 Scripts de Ingestão (ChromaDB)

### `ingest_eixo_etico.py`
Processa documentos do Eixo Ético

```bash
python scripts/ingest_eixo_etico.py
```

Documentos:
- EAOAB (Lei 8.906/94)
- Código de Ética e Disciplina
- Regulamento Geral

### `ingest_eixo_fundamental_novos.py`
Processa NOVOS documentos do Eixo Fundamental

```bash
python scripts/ingest_eixo_fundamental_novos.py
```

Documentos (novos):
- Código Civil (CC)
- Código Penal (CP)
- CLT
- CDC

**Não reprocessa**: CF, CPP, CTN, CPC (já processados)

### `ingest_eixo_administrativo.py`
Processa documentos do Eixo Administrativo

```bash
python scripts/ingest_eixo_administrativo.py
```

Documentos:
- Lei 14.133 (Licitações)
- Lei 8.429 (Improbidade)
- Lei 9.784 (Processo Adm)
- Lei 8.112 (Servidores)
- Lei 4.717 (Ação Popular)
- Lei 12.016 (Mandado de Segurança)

---

## ☁️ Scripts de Migração (Supabase)

### `migrate_to_supabase.py`
Migra dados do ChromaDB para Supabase

```bash
# Migrar tudo
python scripts/migrate_to_supabase.py

# Migrar apenas um eixo
python scripts/migrate_to_supabase.py --eixo etico
python scripts/migrate_to_supabase.py --eixo fundamental
python scripts/migrate_to_supabase.py --eixo administrativo
```

Migra:
- Metadados dos documentos
- Artigos de leis
- Embeddings vetoriais
- Questões OAB

---

## 🧪 Scripts de Teste

### `test_search_by_eixo.py`
Testa busca vetorial por eixo

```bash
# Testar tudo
python scripts/test_search_by_eixo.py

# Testar apenas um eixo
python scripts/test_search_by_eixo.py --eixo etico
python scripts/test_search_by_eixo.py --eixo fundamental
python scripts/test_search_by_eixo.py --eixo administrativo
```

Testa:
- Busca vetorial em cada eixo
- Queries específicas por matéria
- Estatísticas consolidadas

### `test_supabase_search.py`
Teste geral de busca no Supabase (método antigo)

```bash
python scripts/test_supabase_search.py
```

---

## 🗄️ Scripts SQL

### `supabase_schema.sql`
Schema completo do banco Supabase

**Executar no Supabase SQL Editor**

Cria:
- Tabelas (documents, law_articles, embeddings, questoes_oab)
- Índices otimizados
- Funções de busca vetorial
- Views de estatísticas
- RLS policies

### `supabase_update_eixos.sql`
Atualização para adicionar campos de eixo

**Executar no Supabase SQL Editor APÓS criar schema**

Adiciona:
- Campos `eixo` e `peso_oab`
- Índices por eixo
- Atualização de documentos já existentes
- View atualizada de estatísticas

---

## 📊 Scripts Antigos (Compatibilidade)

### `ingest_corpus.py`
Ingestão no método antigo (sem organização por eixo)

```bash
python scripts/ingest_corpus.py
```

**Usa**: `data/corpus_manifest.json`  
**Recomendado**: Use `processar_tudo.py` ao invés

---

## 🔄 Fluxo Completo

```
1. verify_files.py          → Verificar PDFs existem
2. enrich_manifest_v2.py    → Extrair metadados
3. [SQL Editor]             → Executar supabase_update_eixos.sql
4. ingest_eixo_*.py         → Processar no ChromaDB
5. migrate_to_supabase.py   → Migrar para Supabase
6. test_search_by_eixo.py   → Validar busca
```

**Ou simplesmente**:
```bash
python scripts/processar_tudo.py
```

---

## 📂 Estrutura de Dados

```
data/
├── corpus_manifest.json        # V1 (antigo)
├── corpus_manifest_v2.json     # V2 (com eixos) ← USAR
├── eixo_etico/
│   ├── EAOAB-2024.pdf
│   ├── Codigo_etica_disciplina_oab.pdf
│   └── Regulamento_Geral.pdf
├── eixo_fundamental/
│   ├── cf.pdf
│   ├── codigo_penal_1ed.pdf
│   ├── Código Civil 2 ed.pdf
│   └── ...
└── eixo_adiministrativo/
    ├── L14133.pdf
    ├── L8429.pdf
    └── ...
```

---

## 🆘 Troubleshooting

### Erro: "Arquivo não encontrado"
```bash
python scripts/verify_files.py
```
Verifique se PDFs estão nas pastas corretas

### Erro: "OPENAI_API_KEY não definida"
```bash
# Verificar .env
cat .env | grep OPENAI

# Adicionar
export OPENAI_API_KEY=sk-...
```

### Erro: "ChromaDB não encontrado"
```bash
mkdir chroma_db
```

### Erro: "Nenhum artigo encontrado"
PDF pode estar escaneado ou ter estrutura diferente.  
Verifique `extraction_quality` no manifest.

---

## 📚 Documentação

- **Guia Completo**: `../GUIA_PROCESSAMENTO_EIXOS.md`
- **Status**: `../IMPLEMENTACAO_COMPLETA.md`
- **Inventário**: `../INVENTARIO_RAG_COMPLETO.md`
- **Início Rápido**: `../INICIO_RAPIDO_EIXOS.md`

---

**Última atualização**: 2026-03-02
