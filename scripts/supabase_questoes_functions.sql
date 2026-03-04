-- ====================================================================
-- FUNÇÕES RPC PARA QUESTÕES OAB NO SUPABASE
-- ====================================================================
-- Execute este script no SQL Editor do Supabase após criar a tabela questoes_oab
-- ====================================================================

-- ====================================================================
-- 1. FUNÇÃO: Buscar questões por filtros
-- ====================================================================

CREATE OR REPLACE FUNCTION buscar_questoes(
    p_materia TEXT DEFAULT NULL,
    p_ano INTEGER DEFAULT NULL,
    p_anulada BOOLEAN DEFAULT NULL,
    p_dificuldade TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 20,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id TEXT,
    exam_id TEXT,
    exame TEXT,
    ano INTEGER,
    fase INTEGER,
    numero_questao INTEGER,
    materia TEXT,
    assunto TEXT,
    enunciado TEXT,
    alternativas JSONB,
    gabarito TEXT,
    anulada BOOLEAN,
    dificuldade TEXT,
    tags TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.exam_id,
        q.exame,
        q.ano,
        q.fase,
        q.numero_questao,
        q.materia,
        q.assunto,
        q.enunciado,
        q.alternativas,
        q.gabarito,
        q.anulada,
        q.dificuldade,
        q.tags
    FROM questoes_oab q
    WHERE
        (p_materia IS NULL OR q.materia = p_materia)
        AND (p_ano IS NULL OR q.ano = p_ano)
        AND (p_anulada IS NULL OR q.anulada = p_anulada)
        AND (p_dificuldade IS NULL OR q.dificuldade = p_dificuldade)
    ORDER BY q.ano DESC, q.exam_id, q.numero_questao
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;

-- ====================================================================
-- 2. FUNÇÃO: Buscar questão por ID
-- ====================================================================

CREATE OR REPLACE FUNCTION buscar_questao_por_id(p_id TEXT)
RETURNS TABLE (
    id TEXT,
    exam_id TEXT,
    exame TEXT,
    ano INTEGER,
    fase INTEGER,
    numero_questao INTEGER,
    materia TEXT,
    materia_original TEXT,
    assunto TEXT,
    enunciado TEXT,
    alternativas JSONB,
    gabarito TEXT,
    justificativa TEXT,
    anulada BOOLEAN,
    dificuldade TEXT,
    tags TEXT[],
    artigos_relacionados JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.exam_id,
        q.exame,
        q.ano,
        q.fase,
        q.numero_questao,
        q.materia,
        q.materia_original,
        q.assunto,
        q.enunciado,
        q.alternativas,
        q.gabarito,
        q.justificativa,
        q.anulada,
        q.dificuldade,
        q.tags,
        q.artigos_relacionados
    FROM questoes_oab q
    WHERE q.id = p_id;
END;
$$;

-- ====================================================================
-- 3. FUNÇÃO: Buscar questões aleatórias (para simulados)
-- ====================================================================

CREATE OR REPLACE FUNCTION buscar_questoes_aleatorias(
    p_materia TEXT DEFAULT NULL,
    p_ano INTEGER DEFAULT NULL,
    p_quantidade INTEGER DEFAULT 10,
    p_incluir_anuladas BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    id TEXT,
    exam_id TEXT,
    exame TEXT,
    ano INTEGER,
    numero_questao INTEGER,
    materia TEXT,
    enunciado TEXT,
    alternativas JSONB,
    gabarito TEXT,
    dificuldade TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.exam_id,
        q.exame,
        q.ano,
        q.numero_questao,
        q.materia,
        q.enunciado,
        q.alternativas,
        q.gabarito,
        q.dificuldade
    FROM questoes_oab q
    WHERE
        (p_materia IS NULL OR q.materia = p_materia)
        AND (p_ano IS NULL OR q.ano = p_ano)
        AND (p_incluir_anuladas OR q.anulada = FALSE)
    ORDER BY RANDOM()
    LIMIT p_quantidade;
END;
$$;

-- ====================================================================
-- 4. FUNÇÃO: Estatísticas - Questões por matéria
-- ====================================================================

CREATE OR REPLACE FUNCTION get_questoes_por_materia()
RETURNS TABLE (
    materia TEXT,
    total BIGINT
)
LANGUAGE sql
AS $$
    SELECT 
        materia,
        COUNT(*) as total
    FROM questoes_oab
    GROUP BY materia
    ORDER BY total DESC;
$$;

-- ====================================================================
-- 5. FUNÇÃO: Estatísticas - Questões por ano
-- ====================================================================

CREATE OR REPLACE FUNCTION get_questoes_por_ano()
RETURNS TABLE (
    ano INTEGER,
    total BIGINT
)
LANGUAGE sql
AS $$
    SELECT 
        ano,
        COUNT(*) as total
    FROM questoes_oab
    GROUP BY ano
    ORDER BY ano;
$$;

-- ====================================================================
-- 6. FUNÇÃO: Estatísticas - Questões por dificuldade
-- ====================================================================

CREATE OR REPLACE FUNCTION get_questoes_por_dificuldade()
RETURNS TABLE (
    dificuldade TEXT,
    total BIGINT
)
LANGUAGE sql
AS $$
    SELECT 
        dificuldade,
        COUNT(*) as total
    FROM questoes_oab
    GROUP BY dificuldade
    ORDER BY 
        CASE dificuldade
            WHEN 'facil' THEN 1
            WHEN 'media' THEN 2
            WHEN 'dificil' THEN 3
            ELSE 4
        END;
$$;

-- ====================================================================
-- 7. FUNÇÃO: Busca full-text no enunciado
-- ====================================================================

CREATE OR REPLACE FUNCTION buscar_questoes_por_texto(
    p_texto TEXT,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id TEXT,
    exam_id TEXT,
    ano INTEGER,
    materia TEXT,
    enunciado TEXT,
    relevancia REAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        q.id,
        q.exam_id,
        q.ano,
        q.materia,
        q.enunciado,
        ts_rank(to_tsvector('portuguese', q.enunciado), plainto_tsquery('portuguese', p_texto)) as relevancia
    FROM questoes_oab q
    WHERE to_tsvector('portuguese', q.enunciado) @@ plainto_tsquery('portuguese', p_texto)
    ORDER BY relevancia DESC
    LIMIT p_limit;
END;
$$;

-- ====================================================================
-- 8. FUNÇÃO: Estatísticas gerais
-- ====================================================================

CREATE OR REPLACE FUNCTION get_estatisticas_questoes()
RETURNS TABLE (
    total_questoes BIGINT,
    total_anuladas BIGINT,
    total_materias BIGINT,
    ano_mais_antigo INTEGER,
    ano_mais_recente INTEGER
)
LANGUAGE sql
AS $$
    SELECT 
        COUNT(*) as total_questoes,
        COUNT(*) FILTER (WHERE anulada = TRUE) as total_anuladas,
        COUNT(DISTINCT materia) as total_materias,
        MIN(ano) as ano_mais_antigo,
        MAX(ano) as ano_mais_recente
    FROM questoes_oab;
$$;

-- ====================================================================
-- 9. VIEW: Resumo de questões por exame
-- ====================================================================

CREATE OR REPLACE VIEW resumo_exames AS
SELECT 
    exam_id,
    exame,
    ano,
    COUNT(*) as total_questoes,
    COUNT(*) FILTER (WHERE anulada = TRUE) as questoes_anuladas,
    COUNT(DISTINCT materia) as total_materias
FROM questoes_oab
GROUP BY exam_id, exame, ano
ORDER BY ano DESC, exam_id;

-- ====================================================================
-- COMENTÁRIOS
-- ====================================================================

COMMENT ON FUNCTION buscar_questoes IS 'Busca questões com filtros opcionais (matéria, ano, anulada, dificuldade)';
COMMENT ON FUNCTION buscar_questao_por_id IS 'Busca uma questão específica pelo ID';
COMMENT ON FUNCTION buscar_questoes_aleatorias IS 'Retorna questões aleatórias para simulados';
COMMENT ON FUNCTION get_questoes_por_materia IS 'Retorna contagem de questões por matéria';
COMMENT ON FUNCTION get_questoes_por_ano IS 'Retorna contagem de questões por ano';
COMMENT ON FUNCTION get_questoes_por_dificuldade IS 'Retorna contagem de questões por dificuldade';
COMMENT ON FUNCTION buscar_questoes_por_texto IS 'Busca full-text no enunciado das questões';
COMMENT ON FUNCTION get_estatisticas_questoes IS 'Retorna estatísticas gerais do banco de questões';
COMMENT ON VIEW resumo_exames IS 'Resumo de questões agrupadas por exame';

-- ====================================================================
-- FIM
-- ====================================================================
