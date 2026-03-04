-- ====================================================================
-- SCHEMA DO SUPABASE PARA RAG DO TUTOR OAB
-- ====================================================================
-- Copiar e executar no SQL Editor do Supabase
-- ====================================================================

-- 1. HABILITAR EXTENSÕES
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ====================================================================
-- 2. TABELA: documents
-- ====================================================================
-- Catálogo de documentos (leis, editais, normativos)

CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    path TEXT,
    
    -- Metadados do concurso
    banca TEXT DEFAULT 'FGV',
    concurso TEXT DEFAULT 'OAB (Exame de Ordem)',
    fase INTEGER DEFAULT 1,
    
    -- Metadados do documento
    sigla TEXT,
    num_pages INTEGER,
    char_count INTEGER,
    file_size_mb DECIMAL(10,2),
    extraction_quality TEXT,
    document_date TEXT,
    
    -- Metadados de processamento
    extraction_status TEXT DEFAULT 'pending',
    extracted_at TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW(),
    
    -- Estatísticas
    total_articles INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    
    -- Tags e preview
    tags TEXT[],
    preview TEXT,
    
    -- Organização por eixo (NOVO)
    eixo TEXT,
    peso_oab TEXT,  -- 'critico', 'alto', 'medio', 'baixo'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para documents
CREATE INDEX idx_documents_kind ON documents(kind);
CREATE INDEX idx_documents_banca ON documents(banca);
CREATE INDEX idx_documents_sigla ON documents(sigla);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_eixo ON documents(eixo);

-- ====================================================================
-- 3. TABELA: law_articles
-- ====================================================================
-- Chunks de leis por artigo (granularidade fina)

CREATE TABLE law_articles (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Identificação do artigo
    article_number TEXT NOT NULL,
    full_reference TEXT NOT NULL,
    
    -- Conteúdo
    content TEXT NOT NULL,
    full_text TEXT NOT NULL,
    
    -- Metadados herdados
    law_name TEXT NOT NULL,
    law_sigla TEXT,
    banca TEXT,
    concurso TEXT,
    fase INTEGER,
    
    -- Metadados específicos
    chunk_type TEXT DEFAULT 'article',
    char_count INTEGER,
    
    -- Tags e busca
    tags TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para law_articles
CREATE INDEX idx_law_articles_document ON law_articles(document_id);
CREATE INDEX idx_law_articles_number ON law_articles(article_number);
CREATE INDEX idx_law_articles_law ON law_articles(law_name);
CREATE INDEX idx_law_articles_sigla ON law_articles(law_sigla);
CREATE INDEX idx_law_articles_tags ON law_articles USING GIN(tags);

-- Full-text search (busca textual complementar)
CREATE INDEX idx_law_articles_content_fts ON law_articles 
    USING GIN(to_tsvector('portuguese', content));

-- ====================================================================
-- 4. TABELA: document_chunks
-- ====================================================================
-- Chunks de editais, comunicados, normativos

CREATE TABLE document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    
    -- Identificação do chunk
    chunk_type TEXT NOT NULL,
    chunk_index INTEGER,
    
    -- Conteúdo
    content TEXT NOT NULL,
    
    -- Metadados de página (se aplicável)
    page_number INTEGER,
    page_range TEXT,
    
    -- Metadados herdados
    document_name TEXT NOT NULL,
    document_kind TEXT NOT NULL,
    banca TEXT,
    concurso TEXT,
    fase INTEGER,
    
    -- Metadados específicos
    char_count INTEGER,
    document_date TEXT,
    
    -- Tags
    tags TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para document_chunks
CREATE INDEX idx_document_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_kind ON document_chunks(document_kind);
CREATE INDEX idx_document_chunks_type ON document_chunks(chunk_type);
CREATE INDEX idx_document_chunks_tags ON document_chunks USING GIN(tags);

-- Full-text search
CREATE INDEX idx_document_chunks_content_fts ON document_chunks 
    USING GIN(to_tsvector('portuguese', content));

-- ====================================================================
-- 5. TABELA: embeddings
-- ====================================================================
-- Armazenar embeddings com busca vetorial (pgvector)

CREATE TABLE embeddings (
    id TEXT PRIMARY KEY,
    
    -- Referência genérica (polimórfica)
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    
    -- Embedding vector (OpenAI text-embedding-3-small = 1536 dimensões)
    embedding vector(1536) NOT NULL,
    
    -- Metadados para filtragem
    document_id TEXT,
    law_name TEXT,
    document_kind TEXT,
    tags TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para busca vetorial (HNSW = Hierarchical Navigable Small World)
-- Usando cosine distance para similaridade
CREATE INDEX idx_embeddings_vector ON embeddings 
    USING hnsw (embedding vector_cosine_ops);

-- Índices auxiliares
CREATE INDEX idx_embeddings_source ON embeddings(source_type, source_id);
CREATE INDEX idx_embeddings_document ON embeddings(document_id);
CREATE INDEX idx_embeddings_kind ON embeddings(document_kind);
CREATE INDEX idx_embeddings_tags ON embeddings USING GIN(tags);

-- ====================================================================
-- 6. FUNÇÃO: search_embeddings
-- ====================================================================
-- Busca vetorial com filtros

CREATE OR REPLACE FUNCTION search_embeddings(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_kind TEXT DEFAULT NULL,
    filter_tags TEXT[] DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    source_type TEXT,
    source_id TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.source_type,
        e.source_id,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM embeddings e
    WHERE
        (filter_kind IS NULL OR e.document_kind = filter_kind)
        AND (filter_tags IS NULL OR e.tags && filter_tags)
        AND (1 - (e.embedding <=> query_embedding)) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ====================================================================
-- 7. TABELA: questoes_oab
-- ====================================================================
-- Banco de questões para simulados e explicações

CREATE TABLE questoes_oab (
    id TEXT PRIMARY KEY,
    exam_id TEXT NOT NULL,
    exame TEXT NOT NULL,
    
    -- Identificação
    ano INTEGER NOT NULL,
    fase INTEGER NOT NULL DEFAULT 1,
    numero_questao INTEGER NOT NULL,
    
    -- Classificação
    materia TEXT NOT NULL,
    materia_original TEXT,
    assunto TEXT,
    
    -- Conteúdo
    enunciado TEXT NOT NULL,
    alternativas JSONB NOT NULL,
    gabarito TEXT NOT NULL,
    justificativa TEXT,
    
    -- Status e dificuldade
    anulada BOOLEAN DEFAULT FALSE,
    dificuldade TEXT DEFAULT 'media',
    
    -- Relações com RAG
    artigos_relacionados JSONB DEFAULT '[]',
    tags TEXT[],
    
    -- Estatísticas (futuro)
    vezes_respondida INTEGER DEFAULT 0,
    taxa_acerto DECIMAL(5,2),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para questoes_oab
CREATE INDEX idx_questoes_exam ON questoes_oab(exam_id);
CREATE INDEX idx_questoes_ano ON questoes_oab(ano);
CREATE INDEX idx_questoes_materia ON questoes_oab(materia);
CREATE INDEX idx_questoes_anulada ON questoes_oab(anulada);
CREATE INDEX idx_questoes_dificuldade ON questoes_oab(dificuldade);
CREATE INDEX idx_questoes_tags ON questoes_oab USING GIN(tags);
CREATE INDEX idx_questoes_alternativas ON questoes_oab USING GIN(alternativas);

-- Full-text search no enunciado
CREATE INDEX idx_questoes_enunciado_fts ON questoes_oab 
    USING GIN(to_tsvector('portuguese', enunciado));

-- ====================================================================
-- 8. ROW LEVEL SECURITY (RLS)
-- ====================================================================
-- Configurar políticas de acesso

-- Habilitar RLS em todas as tabelas
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE law_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE questoes_oab ENABLE ROW LEVEL SECURITY;

-- Permitir leitura pública (para app frontend com anon key)
CREATE POLICY "Enable read access for all users" ON documents
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON law_articles
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON document_chunks
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON questoes_oab
    FOR SELECT USING (true);

-- Embeddings: apenas backend pode ler (service_role key)
-- Não criar política pública para embeddings por segurança

-- ====================================================================
-- 9. TRIGGERS PARA UPDATED_AT
-- ====================================================================

-- Função genérica para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger em todas as tabelas
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_law_articles_updated_at
    BEFORE UPDATE ON law_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_chunks_updated_at
    BEFORE UPDATE ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_embeddings_updated_at
    BEFORE UPDATE ON embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questoes_oab_updated_at
    BEFORE UPDATE ON questoes_oab
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ====================================================================
-- 10. VIEWS ÚTEIS
-- ====================================================================

-- View de estatísticas gerais
CREATE OR REPLACE VIEW rag_stats AS
SELECT
    (SELECT COUNT(*) FROM documents) AS total_documents,
    (SELECT COUNT(*) FROM law_articles) AS total_law_articles,
    (SELECT COUNT(*) FROM document_chunks) AS total_document_chunks,
    (SELECT COUNT(*) FROM embeddings) AS total_embeddings,
    (SELECT COUNT(*) FROM questoes_oab) AS total_questoes,
    (SELECT COUNT(DISTINCT law_name) FROM law_articles) AS unique_laws,
    (SELECT COUNT(*) FROM questoes_oab WHERE anulada = true) AS questoes_anuladas;

-- View de documentos com estatísticas
CREATE OR REPLACE VIEW documents_with_stats AS
SELECT
    d.*,
    COALESCE(la.article_count, 0) AS article_count,
    COALESCE(dc.chunk_count, 0) AS chunk_count
FROM documents d
LEFT JOIN (
    SELECT document_id, COUNT(*) AS article_count
    FROM law_articles
    GROUP BY document_id
) la ON d.id = la.document_id
LEFT JOIN (
    SELECT document_id, COUNT(*) AS chunk_count
    FROM document_chunks
    GROUP BY document_id
) dc ON d.id = dc.document_id;

-- ====================================================================
-- SCHEMA CRIADO COM SUCESSO!
-- ====================================================================
-- Próximo passo: executar scripts/migrate_to_supabase.py
-- ====================================================================
