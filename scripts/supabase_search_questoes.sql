-- ====================================================================
-- FUNÇÕES RPC PARA BUSCA DE QUESTÕES COM EMBEDDINGS
-- ====================================================================
-- Execute este script no SQL Editor do Supabase após vetorizar as questões
-- ====================================================================

-- ====================================================================
-- 1. FUNÇÃO: Buscar questões por similaridade semântica
-- ====================================================================

CREATE OR REPLACE FUNCTION search_questoes(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 10,
    filter_materia TEXT DEFAULT NULL,
    filter_ano INTEGER DEFAULT NULL,
    filter_tags TEXT[] DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    questao_id TEXT,
    materia TEXT,
    ano INTEGER,
    exam_id TEXT,
    numero_questao INTEGER,
    enunciado TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.source_id as questao_id,
        q.materia,
        q.ano,
        q.exam_id,
        q.numero_questao,
        q.enunciado,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM embeddings e
    INNER JOIN questoes_oab q ON e.source_id = q.id
    WHERE
        e.source_type = 'questao'
        AND (filter_materia IS NULL OR q.materia = filter_materia)
        AND (filter_ano IS NULL OR q.ano = filter_ano)
        AND (filter_tags IS NULL OR e.tags && filter_tags)
        AND (1 - (e.embedding <=> query_embedding)) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ====================================================================
-- 2. FUNÇÃO: Buscar questões similares a uma questão específica
-- ====================================================================

CREATE OR REPLACE FUNCTION search_questoes_similares(
    questao_id TEXT,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id TEXT,
    questao_id_result TEXT,
    materia TEXT,
    ano INTEGER,
    enunciado TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
DECLARE
    questao_embedding vector(1536);
BEGIN
    -- Buscar embedding da questão de referência
    SELECT embedding INTO questao_embedding
    FROM embeddings
    WHERE source_type = 'questao' AND source_id = questao_id
    LIMIT 1;
    
    IF questao_embedding IS NULL THEN
        RAISE EXCEPTION 'Questão não encontrada ou sem embedding: %', questao_id;
    END IF;
    
    -- Buscar questões similares
    RETURN QUERY
    SELECT
        e.id,
        e.source_id as questao_id_result,
        q.materia,
        q.ano,
        q.enunciado,
        1 - (e.embedding <=> questao_embedding) AS similarity
    FROM embeddings e
    INNER JOIN questoes_oab q ON e.source_id = q.id
    WHERE
        e.source_type = 'questao'
        AND e.source_id != questao_id  -- Excluir a própria questão
        AND (1 - (e.embedding <=> questao_embedding)) > match_threshold
    ORDER BY e.embedding <=> questao_embedding
    LIMIT match_count;
END;
$$;

-- ====================================================================
-- 3. FUNÇÃO: Buscar questões relacionadas a artigos de lei
-- ====================================================================

CREATE OR REPLACE FUNCTION search_questoes_por_artigo(
    artigo_id TEXT,
    match_threshold FLOAT DEFAULT 0.6,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    questao_id TEXT,
    materia TEXT,
    ano INTEGER,
    enunciado TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
DECLARE
    artigo_embedding vector(1536);
BEGIN
    -- Buscar embedding do artigo
    SELECT embedding INTO artigo_embedding
    FROM embeddings
    WHERE source_type = 'law_article' AND source_id = artigo_id
    LIMIT 1;
    
    IF artigo_embedding IS NULL THEN
        RAISE EXCEPTION 'Artigo não encontrado ou sem embedding: %', artigo_id;
    END IF;
    
    -- Buscar questões relacionadas
    RETURN QUERY
    SELECT
        e.source_id as questao_id,
        q.materia,
        q.ano,
        q.enunciado,
        1 - (e.embedding <=> artigo_embedding) AS similarity
    FROM embeddings e
    INNER JOIN questoes_oab q ON e.source_id = q.id
    WHERE
        e.source_type = 'questao'
        AND (1 - (e.embedding <=> artigo_embedding)) > match_threshold
    ORDER BY e.embedding <=> artigo_embedding
    LIMIT match_count;
END;
$$;

-- ====================================================================
-- 4. FUNÇÃO: Buscar questões e artigos relacionados (híbrido)
-- ====================================================================

CREATE OR REPLACE FUNCTION search_rag_completo(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.5,
    match_count_questoes INT DEFAULT 5,
    match_count_artigos INT DEFAULT 5,
    filter_materia TEXT DEFAULT NULL
)
RETURNS TABLE (
    tipo TEXT,
    id TEXT,
    source_id TEXT,
    titulo TEXT,
    conteudo TEXT,
    materia TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    -- Buscar questões
    SELECT
        'questao'::TEXT as tipo,
        e.id,
        e.source_id,
        ('Questão ' || q.numero_questao::TEXT || ' - ' || q.exam_id)::TEXT as titulo,
        q.enunciado as conteudo,
        q.materia,
        (1 - (e.embedding <=> query_embedding))::FLOAT AS similarity
    FROM embeddings e
    INNER JOIN questoes_oab q ON e.source_id = q.id
    WHERE
        e.source_type = 'questao'
        AND (filter_materia IS NULL OR q.materia = filter_materia)
        AND (1 - (e.embedding <=> query_embedding)) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count_questoes
    
    UNION ALL
    
    -- Buscar artigos de lei
    SELECT
        'artigo'::TEXT as tipo,
        e.id,
        e.source_id,
        la.full_reference as titulo,
        la.full_text as conteudo,
        la.law_name as materia,
        (1 - (e.embedding <=> query_embedding))::FLOAT AS similarity
    FROM embeddings e
    INNER JOIN law_articles la ON e.source_id = la.id
    WHERE
        e.source_type = 'law_article'
        AND (1 - (e.embedding <=> query_embedding)) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count_artigos
    
    ORDER BY similarity DESC;
END;
$$;

-- ====================================================================
-- 5. FUNÇÃO: Estatísticas de embeddings por tipo
-- ====================================================================

CREATE OR REPLACE FUNCTION get_embeddings_stats()
RETURNS TABLE (
    source_type TEXT,
    total BIGINT,
    materias_unicas BIGINT
)
LANGUAGE sql
AS $$
    SELECT 
        source_type,
        COUNT(*) as total,
        COUNT(DISTINCT (metadata->>'materia')) as materias_unicas
    FROM embeddings
    GROUP BY source_type
    ORDER BY total DESC;
$$;

-- ====================================================================
-- 6. VIEW: Questões com embeddings
-- ====================================================================

CREATE OR REPLACE VIEW questoes_com_embeddings AS
SELECT 
    q.id,
    q.exam_id,
    q.exame,
    q.ano,
    q.materia,
    q.numero_questao,
    q.enunciado,
    q.gabarito,
    q.dificuldade,
    q.tags,
    e.id as embedding_id,
    CASE 
        WHEN e.id IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END as tem_embedding
FROM questoes_oab q
LEFT JOIN embeddings e ON e.source_id = q.id AND e.source_type = 'questao';

-- ====================================================================
-- 7. FUNÇÃO: Contar questões sem embedding
-- ====================================================================

CREATE OR REPLACE FUNCTION count_questoes_sem_embedding()
RETURNS BIGINT
LANGUAGE sql
AS $$
    SELECT COUNT(*)
    FROM questoes_oab q
    LEFT JOIN embeddings e ON e.source_id = q.id AND e.source_type = 'questao'
    WHERE e.id IS NULL;
$$;

-- ====================================================================
-- COMENTÁRIOS
-- ====================================================================

COMMENT ON FUNCTION search_questoes IS 'Busca questões por similaridade semântica com filtros opcionais';
COMMENT ON FUNCTION search_questoes_similares IS 'Encontra questões similares a uma questão específica';
COMMENT ON FUNCTION search_questoes_por_artigo IS 'Busca questões relacionadas a um artigo de lei específico';
COMMENT ON FUNCTION search_rag_completo IS 'Busca híbrida que retorna questões e artigos relacionados';
COMMENT ON FUNCTION get_embeddings_stats IS 'Estatísticas de embeddings por tipo de fonte';
COMMENT ON FUNCTION count_questoes_sem_embedding IS 'Conta quantas questões ainda não têm embedding';
COMMENT ON VIEW questoes_com_embeddings IS 'View com todas as questões e status de embedding';

-- ====================================================================
-- FIM
-- ====================================================================
