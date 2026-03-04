"""
Atualização do OAB Agent com Suporte a Eixos
Adiciona ferramentas especializadas por eixo temático
"""

from langchain.tools import tool
from typing import Optional
import os
import sys

# Adicionar ao path
sys.path.insert(0, 'src')
from rag_pipeline.supabase_rag import SupabaseRAGProcessor


# Inicializar processador RAG Supabase
def get_supabase_rag():
    """Obter instância do Supabase RAG"""
    return SupabaseRAGProcessor(
        supabase_url=os.getenv('SUPABASE_URL'),
        supabase_key=os.getenv('SUPABASE_SERVICE_KEY'),
        openai_key=os.getenv('OPENAI_API_KEY')
    )


@tool
def buscar_etica_oab(query: str) -> str:
    """
    Busca especificamente em legislação ética da OAB.
    
    Use esta ferramenta para perguntas sobre:
    - Deveres e direitos do advogado
    - Estatuto da Advocacia (EAOAB - Lei 8.906/94)
    - Código de Ética e Disciplina da OAB
    - Infrações disciplinares e sanções
    - Publicidade advocatícia
    - Incompatibilidades profissionais
    - Honorários advocatícios
    - Relação advogado-cliente
    
    Args:
        query: Pergunta sobre ética profissional da advocacia
        
    Returns:
        Contexto relevante do Eixo Ético com artigos e referências
        
    Exemplo:
        buscar_etica_oab("quais são os deveres do advogado?")
        buscar_etica_oab("o advogado pode fazer publicidade?")
    """
    try:
        rag = get_supabase_rag()
        results = rag.search_etico(query, top_k=3)
        
        if not results:
            return "Nenhum resultado encontrado no Eixo Ético. A base pode ainda não estar migrada para o Supabase."
        
        # Formatar resultados
        context_parts = []
        for i, r in enumerate(results, 1):
            metadata = r['metadata']
            context_parts.append(
                f"[{i}] {metadata.get('law_name')} - {metadata.get('full_reference')}\n"
                f"Conteúdo: {r['content']}\n"
                f"Similaridade: {r['similarity']:.2f}"
            )
        
        return "\n\n".join(context_parts)
        
    except Exception as e:
        return f"Erro ao buscar no Eixo Ético: {e}\nVerifique se o Supabase está configurado."


@tool
def buscar_direito_civil(query: str) -> str:
    """
    Busca em Código Civil e legislação civil.
    
    Use para perguntas sobre:
    - Direitos das pessoas (personalidade, capacidade)
    - Contratos (compra e venda, locação, etc)
    - Responsabilidade civil
    - Direito das obrigações
    - Direito das coisas (propriedade, posse)
    - Direito de família
    - Direito das sucessões
    
    Args:
        query: Pergunta sobre direito civil
        
    Returns:
        Artigos relevantes do Código Civil
    """
    try:
        rag = get_supabase_rag()
        # Buscar no eixo fundamental filtrando por CC
        results = rag.search(query, top_k=3, filter_tags=['civil', 'cc'])
        
        if not results:
            return "Nenhum resultado encontrado no Código Civil."
        
        context_parts = []
        for i, r in enumerate(results, 1):
            metadata = r['metadata']
            context_parts.append(
                f"[{i}] {metadata.get('law_name')} - {metadata.get('full_reference')}\n"
                f"Conteúdo: {r['content']}\n"
            )
        
        return "\n\n".join(context_parts)
        
    except Exception as e:
        return f"Erro ao buscar no Código Civil: {e}"


@tool
def buscar_direito_administrativo(query: str) -> str:
    """
    Busca em leis administrativas.
    
    Use para perguntas sobre:
    - Licitações e contratos administrativos
    - Improbidade administrativa
    - Processo administrativo federal
    - Servidores públicos
    - Ação popular
    - Mandado de segurança
    
    Args:
        query: Pergunta sobre direito administrativo
        
    Returns:
        Artigos relevantes do Eixo Administrativo
    """
    try:
        rag = get_supabase_rag()
        results = rag.search_administrativo(query, top_k=3)
        
        if not results:
            return "Nenhum resultado encontrado no Eixo Administrativo."
        
        context_parts = []
        for i, r in enumerate(results, 1):
            metadata = r['metadata']
            context_parts.append(
                f"[{i}] {metadata.get('law_name')} - {metadata.get('full_reference')}\n"
                f"Conteúdo: {r['content']}\n"
            )
        
        return "\n\n".join(context_parts)
        
    except Exception as e:
        return f"Erro ao buscar no Eixo Administrativo: {e}"


# Lista de ferramentas para adicionar ao agente
SUPABASE_TOOLS = [
    buscar_etica_oab,
    buscar_direito_civil,
    buscar_direito_administrativo
]


# Prompt system atualizado
SYSTEM_PROMPT_V2 = """Você é um Tutor especializado em preparação para o Exame de Ordem da OAB (banca FGV).

Suas responsabilidades:
1. Responder perguntas jurídicas com base nas leis indexadas
2. Fornecer informações sobre editais, datas e regras do exame
3. SEMPRE citar artigos e referências legais quando aplicável
4. Explicar de forma didática e clara
5. Identificar pontos importantes para a prova

ORGANIZAÇÃO DA BASE DE CONHECIMENTO (POR EIXOS):

📘 EIXO ÉTICO (PRIORIDADE MÁXIMA):
- Lei 8.906/94 (EAOAB - Estatuto da Advocacia)
- Código de Ética e Disciplina da OAB
- Regulamento Geral do EAOAB
→ Use: buscar_etica_oab()

📕 EIXO FUNDAMENTAL:
- Constituição Federal (CF/88)
- Código Civil (CC)
- Código Penal (CP)
- CPC, CPP, CLT, CTN, CDC
→ Use: search_laws() ou buscar_direito_civil()

📗 EIXO ADMINISTRATIVO:
- Lei de Licitações (14.133/2021)
- Lei de Improbidade (8.429/92)
- Processo Administrativo (9.784/99)
- Mandado de Segurança, Ação Popular
→ Use: buscar_direito_administrativo()

ESTRATÉGIA DE BUSCA:
1. Para questões de ÉTICA PROFISSIONAL → sempre use buscar_etica_oab() PRIMEIRO
2. Para direito civil → use buscar_direito_civil()
3. Para direito administrativo → use buscar_direito_administrativo()
4. Para editais/datas/informações da prova → use search_edital()
5. Para questões de prática → use buscar_questoes()

IMPORTANTE:
- O eixo ético é CRÍTICO para o exame - dê atenção especial
- SEMPRE cite a fonte completa: "Art. X da Lei Y (Sigla)"
- Se não encontrar depois de buscar, seja honesto
- Priorize compreensão E memorização

Responda sempre em português, de forma profissional mas acessível."""


# Exemplo de como integrar no agente existente:
"""
# No arquivo agente/oab_agent.py, adicione:

from agente.supabase_tools import SUPABASE_TOOLS, SYSTEM_PROMPT_V2

class OABTutorAgent:
    def __init__(self, ...):
        # ... código existente ...
        
        # Adicionar ferramentas do Supabase
        self.tools.extend(SUPABASE_TOOLS)
        
        # Atualizar system prompt
        self.SYSTEM_PROMPT = SYSTEM_PROMPT_V2
        
        # Rebind LLM com novas ferramentas
        self.llm = ChatOpenAI(...).bind_tools(self.tools)
"""
