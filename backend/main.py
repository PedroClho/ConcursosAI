"""
API Backend para Plataforma Castro - Tutores para Concursos
FastAPI + LangGraph + ChromaDB
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from datetime import datetime
import sqlite3
import json

# Adicionar raiz ao path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from agente.oab_agent import OABTutorAgent
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env na raiz do projeto
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Criar aplicação FastAPI
app = FastAPI(
    title="Castro API",
    description="API para tutores inteligentes de concursos públicos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:5173",  # Vite dev
        "https://castro.vercel.app",  # Produção (ajustar)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# MODELOS DE DADOS
# =====================================================================

class MessageModel(BaseModel):
    """Mensagem individual no chat"""
    role: str  # 'user' ou 'assistant'
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request para endpoint de chat"""
    message: str
    conversation_history: List[MessageModel] = []
    concurso: str = "oab"  # oab, pf, etc


class ChatResponse(BaseModel):
    """Response do endpoint de chat"""
    response: str
    sources: List[dict] = []
    timestamp: datetime = datetime.now()


class SearchRequest(BaseModel):
    """Request para busca em documentos"""
    query: str
    kind: Optional[str] = None  # lei, edital, normativo
    law_filter: Optional[str] = None  # CF, CPC, CPP, CTN
    top_k: int = 5


class SearchResult(BaseModel):
    """Resultado de busca"""
    document: str
    metadata: dict
    relevance_score: float


class StatsResponse(BaseModel):
    """Estatísticas da base de dados"""
    total_items: int
    laws_count: int
    available_laws: List[str]
    collection_name: str


class AlternativaModel(BaseModel):
    """Alternativa de questão"""
    letra: str
    texto: str


class QuestaoModel(BaseModel):
    """Modelo de questão OAB"""
    id: str
    exam_id: str
    exame: str
    ano: int
    fase: int
    numero_questao: int
    materia: str
    materia_original: Optional[str]
    assunto: Optional[str]
    enunciado: str
    alternativas: List[AlternativaModel]
    gabarito: str
    justificativa: Optional[str]
    anulada: bool
    dificuldade: str
    tags: List[str]


class FiltroQuestoesRequest(BaseModel):
    """Request para filtrar questões"""
    materia: Optional[str] = None
    ano: Optional[int] = None
    fase: Optional[int] = 1
    limit: int = 20
    offset: int = 0
    incluir_anuladas: bool = False


class ListarQuestoesResponse(BaseModel):
    """Response da listagem de questões"""
    questoes: List[QuestaoModel]
    total: int
    offset: int
    limit: int


# =====================================================================
# CONEXÃO COM BANCO DE QUESTÕES
# =====================================================================

DB_PATH = os.path.join(root_dir, "questoes", "database", "oab_questoes.db")

def get_db_connection():
    """Cria conexão com banco SQLite"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=500,
            detail="Banco de questões não encontrado. Execute: python questoes/scripts/criar_banco_questoes.py"
        )
    return sqlite3.connect(DB_PATH)


def questao_from_row(row: tuple) -> QuestaoModel:
    """Converte row do SQLite para QuestaoModel"""
    return QuestaoModel(
        id=row[0],
        exam_id=row[1],
        exame=row[2],
        ano=row[3],
        fase=row[4],
        numero_questao=row[5],
        materia=row[6],
        materia_original=row[7],
        assunto=row[8],
        enunciado=row[9],
        alternativas=[AlternativaModel(**alt) for alt in json.loads(row[10])],
        gabarito=row[11],
        justificativa=row[12],
        anulada=bool(row[13]),
        dificuldade=row[14],
        tags=json.loads(row[15]) if row[15] else []
    )


# =====================================================================
# INICIALIZAÇÃO DOS AGENTES
# =====================================================================

print("Inicializando agentes...")

# Obter API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[ERRO] OPENAI_API_KEY não encontrada no .env")
    oab_agent = None
else:
    # Agente OAB
    try:
        oab_agent = OABTutorAgent(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4o-mini",
            chroma_persist_directory="./chroma_db",
            collection_name="oab_corpus"
        )
        print("[OK] Agente OAB inicializado")
    except Exception as e:
        print(f"[ERRO] Falha ao inicializar agente OAB: {e}")
        oab_agent = None

# Futuro: outros agentes
# pf_agent = PFTutorAgent(...)
# pm_agent = PMTutorAgent(...)

# =====================================================================
# ENDPOINTS
# =====================================================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Castro API - Tutores para Concursos",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "oab": oab_agent is not None,
        }
    }


@app.post("/api/oab/chat", response_model=ChatResponse)
async def oab_chat(request: ChatRequest):
    """
    Chat com o Tutor OAB.
    
    Recebe uma mensagem e o histórico de conversação,
    retorna a resposta do agente.
    """
    if not oab_agent:
        raise HTTPException(
            status_code=503,
            detail="Agente OAB não está disponível"
        )
    
    try:
        # Converter histórico (simplificado por enquanto)
        # Você pode implementar conversão para formato LangChain
        
        response = oab_agent.chat(
            user_message=request.message,
            conversation_history=None  # TODO: converter histórico
        )
        
        return ChatResponse(
            response=response,
            sources=[],  # TODO: extrair fontes citadas
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar chat: {str(e)}"
        )


@app.post("/api/oab/search", response_model=List[SearchResult])
async def oab_search(request: SearchRequest):
    """
    Busca direta em documentos OAB (sem chat).
    
    Útil para implementar funcionalidades como:
    - Pesquisa no banco de leis
    - Filtros por tipo de documento
    - Exploração de conteúdo
    """
    if not oab_agent:
        raise HTTPException(
            status_code=503,
            detail="Agente OAB não está disponível"
        )
    
    try:
        # Montar filtros com sintaxe correta do ChromaDB
        filters = None
        if request.kind and request.law_filter:
            # Múltiplos filtros: usar $and
            filters = {
                "$and": [
                    {"kind": request.kind},
                    {"sigla": request.law_filter.upper()}
                ]
            }
        elif request.kind:
            filters = {"kind": request.kind}
        elif request.law_filter:
            filters = {"sigla": request.law_filter.upper()}
        
        # Buscar
        results = oab_agent.search_tools.processor.search(
            query=request.query,
            top_k=request.top_k,
            filter_metadata=filters
        )
        
        # Converter para modelo de resposta
        return [
            SearchResult(
                document=result['document'],
                metadata=result['metadata'],
                relevance_score=result['relevance_score']
            )
            for result in results
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar: {str(e)}"
        )


@app.get("/api/oab/stats", response_model=StatsResponse)
async def oab_stats():
    """
    Retorna estatísticas da base de dados OAB.
    
    Útil para mostrar ao usuário:
    - Quantos documentos estão disponíveis
    - Quais leis estão indexadas
    - Etc
    """
    if not oab_agent:
        raise HTTPException(
            status_code=503,
            detail="Agente OAB não está disponível"
        )
    
    try:
        stats = oab_agent.search_tools.processor.get_collection_stats()
        
        return StatsResponse(
            total_items=stats['total_articles'],
            laws_count=stats['laws_count'],
            available_laws=stats['laws'],
            collection_name=stats['collection_name']
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )


# =====================================================================
# ENDPOINTS DE QUESTÕES
# =====================================================================

@app.get("/api/questoes/materias")
async def listar_materias():
    """Lista todas as matérias disponíveis no banco de questões"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT materia, COUNT(*) as total
            FROM questoes
            WHERE anulada = 0
            GROUP BY materia
            ORDER BY total DESC
        """)
        
        materias = [
            {"nome": row[0], "total": row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return materias
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar matérias: {str(e)}")


@app.post("/api/questoes/filtrar", response_model=ListarQuestoesResponse)
async def filtrar_questoes(filtros: FiltroQuestoesRequest):
    """
    Filtra questões por matéria, ano, fase, etc.
    
    Usado na página de simulados para buscar questões específicas.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Montar query
        where_clauses = []
        params = []
        
        if filtros.materia:
            where_clauses.append("materia = ?")
            params.append(filtros.materia)
        
        if filtros.ano:
            where_clauses.append("ano = ?")
            params.append(filtros.ano)
        
        if filtros.fase:
            where_clauses.append("fase = ?")
            params.append(filtros.fase)
        
        if not filtros.incluir_anuladas:
            where_clauses.append("anulada = 0")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Contar total
        count_query = f"SELECT COUNT(*) FROM questoes WHERE {where_sql}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Buscar questões
        query = f"""
            SELECT id, exam_id, exame, ano, fase, numero_questao,
                   materia, materia_original, assunto, enunciado,
                   alternativas, gabarito, justificativa, anulada,
                   dificuldade, tags
            FROM questoes
            WHERE {where_sql}
            ORDER BY RANDOM()
            LIMIT ? OFFSET ?
        """
        
        cursor.execute(query, params + [filtros.limit, filtros.offset])
        
        questoes = [questao_from_row(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return ListarQuestoesResponse(
            questoes=questoes,
            total=total,
            offset=filtros.offset,
            limit=filtros.limit
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao filtrar questões: {str(e)}")


@app.get("/api/questoes/{questao_id}", response_model=QuestaoModel)
async def detalhar_questao(questao_id: str):
    """Retorna detalhes de uma questão específica"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, exam_id, exame, ano, fase, numero_questao,
                   materia, materia_original, assunto, enunciado,
                   alternativas, gabarito, justificativa, anulada,
                   dificuldade, tags
            FROM questoes
            WHERE id = ?
        """, (questao_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Questão não encontrada")
        
        return questao_from_row(row)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar questão: {str(e)}")


@app.get("/api/questoes/random/{materia}")
async def questao_aleatoria(materia: str):
    """Retorna uma questão aleatória de uma matéria"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, exam_id, exame, ano, fase, numero_questao,
                   materia, materia_original, assunto, enunciado,
                   alternativas, gabarito, justificativa, anulada,
                   dificuldade, tags
            FROM questoes
            WHERE materia = ? AND anulada = 0
            ORDER BY RANDOM()
            LIMIT 1
        """, (materia,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Nenhuma questão encontrada para {materia}")
        
        return questao_from_row(row)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar questão: {str(e)}")


# =====================================================================
# ENDPOINTS FUTUROS (comentados)
# =====================================================================

# @app.post("/api/oab/generate-question")
# async def generate_question(tema: str):
#     """Gera uma questão de múltipla escolha sobre um tema"""
#     pass

# @app.post("/api/oab/evaluate-answer")
# async def evaluate_answer(question_id: str, answer: str):
#     """Avalia a resposta do aluno e dá feedback"""
#     pass

# @app.get("/api/user/{user_id}/progress")
# async def get_user_progress(user_id: str):
#     """Retorna progresso do aluno"""
#     pass

# @app.post("/api/user/{user_id}/study-plan")
# async def generate_study_plan(user_id: str):
#     """Gera plano de estudos personalizado"""
#     pass


# =====================================================================
# EXECUÇÃO
# =====================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("CASTRO API - INICIANDO SERVIDOR")
    print("="*70)
    print("\nDocumentação: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/health")
    print("\nEndpoints disponíveis:")
    print("  AGENTE:")
    print("    POST /api/oab/chat           - Chat com Tutor OAB")
    print("    POST /api/oab/search         - Busca em documentos")
    print("    GET  /api/oab/stats          - Estatísticas da base")
    print("  QUESTÕES:")
    print("    GET  /api/questoes/materias  - Listar matérias")
    print("    POST /api/questoes/filtrar   - Filtrar questões")
    print("    GET  /api/questoes/{id}      - Detalhe de questão")
    print("    GET  /api/questoes/random/{materia} - Questão aleatória")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
