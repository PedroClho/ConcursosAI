"""
API Backend para Plataforma Castro - Tutores para Concursos
FastAPI + LangGraph + Supabase
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import sys
import os
from datetime import datetime
import json
import random

# Adicionar raiz ao path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from src.agent.oab_agent import OABTutorAgent
from dotenv import load_dotenv
from supabase import create_client

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
# CONEXÃO COM BANCO DE QUESTÕES (SUPABASE)
# =====================================================================

def get_supabase_client():
    """Retorna cliente Supabase para questões"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise HTTPException(
            status_code=500,
            detail="Configuração do Supabase não encontrada no .env"
        )
    
    return create_client(supabase_url, supabase_key)


def questao_from_supabase(data: dict) -> QuestaoModel:
    """Converte dados do Supabase para QuestaoModel"""
    return QuestaoModel(
        id=data['id'],
        exam_id=data['exam_id'],
        exame=data['exame'],
        ano=data['ano'],
        fase=data['fase'],
        numero_questao=data['numero_questao'],
        materia=data['materia'],
        materia_original=data.get('materia_original'),
        assunto=data.get('assunto'),
        enunciado=data['enunciado'],
        alternativas=[AlternativaModel(**alt) for alt in data['alternativas']],
        gabarito=data['gabarito'],
        justificativa=data.get('justificativa'),
        anulada=data['anulada'],
        dificuldade=data['dificuldade'],
        tags=data.get('tags', [])
    )


# =====================================================================
# INICIALIZAÇÃO DOS AGENTES
# =====================================================================

print("Inicializando agentes...")

# Obter API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not OPENAI_API_KEY:
    print("[ERRO] OPENAI_API_KEY não encontrada no .env")
    oab_agent = None
elif not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("[ERRO] SUPABASE_URL ou SUPABASE_SERVICE_KEY não encontradas no .env")
    oab_agent = None
else:
    # Agente OAB com Supabase
    try:
        oab_agent = OABTutorAgent(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4o-mini",
            supabase_url=SUPABASE_URL,
            supabase_key=SUPABASE_SERVICE_KEY
        )
        print("[OK] Agente OAB inicializado com Supabase RAG")
    except Exception as e:
        print(f"[ERRO] Falha ao inicializar agente OAB: {e}")
        oab_agent = None

# Futuro: outros agentes
# pf_agent = PFTutorAgent(...)
# pm_agent = PMTutorAgent(...)

# =====================================================================
# AUTENTICAÇÃO
# =====================================================================

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Any:
    """Verifica e retorna o usuário logado via Supabase JWT"""
    token = credentials.credentials
    try:
        # A forma recomendada de validar no Supabase Python Client
        # é instanciar um client temporário só com a anon_key e o token
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") # ou ANON_KEY
        temp_client = create_client(supabase_url, supabase_key)
        
        user_resp = temp_client.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")
        return user_resp.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Não autorizado: {str(e)}")

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
async def oab_chat(request: ChatRequest, user = Depends(get_current_user)):
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
async def oab_search(request: SearchRequest, user = Depends(get_current_user)):
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
        # Buscar usando Supabase RAG
        results = oab_agent.search_tools.rag.search(
            query=request.query,
            top_k=request.top_k,
            filter_kind=request.kind,
            # TODO: Adicionar filtro por sigla quando necessário
        )
        
        # Converter para modelo de resposta
        return [
            SearchResult(
                document=result['content'],
                metadata=result['metadata'],
                relevance_score=result['similarity']
            )
            for result in results
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar: {str(e)}"
        )


@app.get("/api/oab/stats", response_model=StatsResponse)
async def oab_stats(user = Depends(get_current_user)):
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
        stats = oab_agent.search_tools.rag.get_stats_by_eixo()
        
        return StatsResponse(
            total_items=stats.get('total_embeddings', 0),
            laws_count=stats.get('total_documents', 0),
            available_laws=[],  # TODO: Extrair lista de leis do Supabase
            collection_name="supabase_rag"
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
        supabase = get_supabase_client()
        
        # Buscar todas as questões não anuladas
        response = supabase.table('questoes_oab')\
            .select('materia')\
            .eq('anulada', False)\
            .execute()
        
        # Contar por matéria
        materias_count = {}
        for questao in response.data:
            materia = questao['materia']
            materias_count[materia] = materias_count.get(materia, 0) + 1
        
        # Ordenar por total
        materias = [
            {"nome": materia, "total": total}
            for materia, total in sorted(materias_count.items(), key=lambda x: x[1], reverse=True)
        ]
        
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
        supabase = get_supabase_client()
        
        # Construir query base
        query = supabase.table('questoes_oab').select('*', count='exact')
        
        # Aplicar filtros
        if filtros.materia:
            query = query.eq('materia', filtros.materia)
        
        if filtros.ano:
            query = query.eq('ano', filtros.ano)
        
        if filtros.fase:
            query = query.eq('fase', filtros.fase)
        
        if not filtros.incluir_anuladas:
            query = query.eq('anulada', False)
        
        # Executar query para contar total
        count_response = query.execute()
        total = count_response.count
        
        # Buscar questões com paginação (Supabase não tem RANDOM direto, então pegamos todas e embaralhamos)
        query = supabase.table('questoes_oab').select('*')
        
        if filtros.materia:
            query = query.eq('materia', filtros.materia)
        if filtros.ano:
            query = query.eq('ano', filtros.ano)
        if filtros.fase:
            query = query.eq('fase', filtros.fase)
        if not filtros.incluir_anuladas:
            query = query.eq('anulada', False)
        
        # Aplicar range para paginação
        query = query.range(filtros.offset, filtros.offset + filtros.limit - 1)
        
        response = query.execute()
        
        questoes = [questao_from_supabase(q) for q in response.data]
        
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
        supabase = get_supabase_client()
        
        response = supabase.table('questoes_oab')\
            .select('*')\
            .eq('id', questao_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Questão não encontrada")
        
        return questao_from_supabase(response.data[0])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar questão: {str(e)}")


@app.get("/api/questoes/random/{materia}")
async def questao_aleatoria(materia: str):
    """Retorna uma questão aleatória de uma matéria"""
    try:
        supabase = get_supabase_client()
        
        # Buscar todas as questões da matéria (não anuladas)
        response = supabase.table('questoes_oab')\
            .select('*')\
            .eq('materia', materia)\
            .eq('anulada', False)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Nenhuma questão encontrada para {materia}")
        
        # Escolher uma aleatória
        questao_data = random.choice(response.data)
        
        return questao_from_supabase(questao_data)
    
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
