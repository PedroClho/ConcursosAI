-- ====================================================================
-- ATUALIZAÇÃO DO SCHEMA: Adicionar Campos de Eixo
-- ====================================================================
-- Executar no SQL Editor do Supabase APÓS ter criado o schema principal
-- ====================================================================

-- 1. Adicionar colunas na tabela documents
ALTER TABLE documents ADD COLUMN IF NOT EXISTS eixo TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS peso_oab TEXT;

-- 2. Criar índice para eixo
CREATE INDEX IF NOT EXISTS idx_documents_eixo ON documents(eixo);

-- 3. Adicionar coluna eixo nas tabelas relacionadas
ALTER TABLE law_articles ADD COLUMN IF NOT EXISTS eixo TEXT;
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS eixo TEXT;

CREATE INDEX IF NOT EXISTS idx_law_articles_eixo ON law_articles(eixo);
CREATE INDEX IF NOT EXISTS idx_document_chunks_eixo ON document_chunks(eixo);

-- 4. Atualizar documentos já existentes
UPDATE documents SET eixo = 'fundamental' 
WHERE id IN ('lei_cf_1988', 'lei_cpp', 'lei_ctn', 'lei_cpc_2015');

UPDATE documents SET eixo = 'editais' 
WHERE kind IN ('edital', 'comunicado', 'normativo');

-- 5. Atualizar artigos de leis já processados
UPDATE law_articles 
SET eixo = 'fundamental'
WHERE document_id IN ('lei_cf_1988', 'lei_cpp', 'lei_ctn', 'lei_cpc_2015');

UPDATE document_chunks 
SET eixo = 'editais'
WHERE document_kind IN ('edital', 'comunicado', 'normativo');

-- 6. Atualizar view de estatísticas
CREATE OR REPLACE VIEW rag_stats_completo AS
SELECT
    (SELECT COUNT(*) FROM documents) AS total_documents,
    (SELECT COUNT(*) FROM documents WHERE eixo = 'etico') AS docs_etico,
    (SELECT COUNT(*) FROM documents WHERE eixo = 'fundamental') AS docs_fundamental,
    (SELECT COUNT(*) FROM documents WHERE eixo = 'administrativo') AS docs_administrativo,
    (SELECT COUNT(*) FROM documents WHERE eixo = 'editais') AS docs_editais,
    (SELECT COUNT(*) FROM law_articles) AS total_artigos,
    (SELECT COUNT(*) FROM law_articles WHERE eixo = 'etico') AS artigos_etico,
    (SELECT COUNT(*) FROM law_articles WHERE eixo = 'fundamental') AS artigos_fundamental,
    (SELECT COUNT(*) FROM law_articles WHERE eixo = 'administrativo') AS artigos_administrativo,
    (SELECT COUNT(*) FROM document_chunks) AS total_chunks_editais,
    (SELECT COUNT(*) FROM embeddings) AS total_embeddings,
    (SELECT COUNT(*) FROM questoes_oab) AS total_questoes;

-- ====================================================================
-- CONCLUÍDO!
-- ====================================================================
-- Agora você pode:
-- 1. Verificar: SELECT * FROM rag_stats_completo;
-- 2. Testar filtro por eixo: SELECT * FROM documents WHERE eixo = 'fundamental';
-- ====================================================================
