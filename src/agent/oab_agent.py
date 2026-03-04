"""
Agente Tutor OAB usando LangGraph
"""

from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from .tools import SearchTools


class AgentState(TypedDict):
    """Estado do agente"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_action: str


class OABTutorAgent:
    """
    Agente Tutor inteligente para o Exame de Ordem (OAB).
    
    Funcionalidades:
    - Responde perguntas sobre leis (CF, CPC, CPP, CTN)
    - Consulta editais e informações da prova
    - Explica artigos de forma didática
    - Cita fontes e referências legais
    """
    
    SYSTEM_PROMPT = """Você é um Tutor especializado em preparação para o Exame de Ordem da OAB (banca FGV).

Suas responsabilidades:
1. Responder perguntas jurídicas com base nas leis indexadas (CF, CPC, CPP, CTN)
2. Fornecer informações sobre editais, datas e regras do exame
3. SEMPRE citar artigos e referências legais quando aplicável
4. Explicar de forma didática e clara
5. Identificar pontos importantes para a prova

IMPORTANTE:
- Use as ferramentas disponíveis para buscar informações atualizadas
- SEMPRE tente buscar nos editais/documentos antes de dizer que não sabe
- Quando o usuário perguntar sobre "próximo exame" ou "data da prova", busque nos editais
  mesmo que a data pareça ser do passado - pode ser a informação mais recente disponível
- Quando citar artigos, use o formato: "Art. X da Lei Y"
- Se não encontrar informação depois de buscar, seja honesto e sugira onde buscar
- Foque em ajudar o candidato a entender E memorizar

Ferramentas disponíveis:
- search_laws: busca artigos de leis (CF, CPC, CPP, CTN)
- search_edital: busca informações nos editais (SEMPRE USE PARA PERGUNTAS SOBRE DATAS/LOCAIS)
- search_provimento: busca regras do Exame de Ordem
- get_database_stats: mostra estatísticas da base

Responda sempre em português, de forma profissional mas acessível."""
    
    def __init__(
        self,
        openai_api_key: str = None,
        model: str = "gpt-4o-mini",
        supabase_url: str = None,
        supabase_key: str = None
    ):
        """
        Inicializa o agente tutor.
        
        Args:
            openai_api_key: Chave da API OpenAI
            model: Modelo a usar (padrão: gpt-4o-mini)
            supabase_url: URL do Supabase
            supabase_key: Chave do Supabase
        """
        # Inicializar ferramentas com Supabase
        self.search_tools = SearchTools(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            openai_key=openai_api_key
        )
        
        # Obter todas as ferramentas
        self.tools = self.search_tools.get_all_tools()
        
        # Criar LLM com ferramentas
        self.llm = ChatOpenAI(
            model=model,
            api_key=openai_api_key,
            temperature=0.3  # Mais determinístico para respostas técnicas
        ).bind_tools(self.tools)
        
        # Criar grafo do agente
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Cria o grafo de execução do agente usando LangGraph"""
        
        # Definir nós do grafo
        def call_model(state: AgentState) -> AgentState:
            """Nó que chama o modelo LLM"""
            messages = state["messages"]
            
            # Adicionar system prompt se não existir
            if not any(isinstance(m, SystemMessage) for m in messages):
                messages = [SystemMessage(content=self.SYSTEM_PROMPT)] + messages
            
            response = self.llm.invoke(messages)
            
            return {"messages": [response]}
        
        def should_continue(state: AgentState) -> str:
            """Decide se deve continuar (usar tools) ou finalizar"""
            last_message = state["messages"][-1]
            
            # Se tem tool_calls, executar ferramentas
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            
            # Caso contrário, finalizar
            return END
        
        # Criar grafo
        workflow = StateGraph(AgentState)
        
        # Adicionar nós
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Definir entrada
        workflow.set_entry_point("agent")
        
        # Adicionar edges condicionais
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Após executar tools, volta para o agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def chat(self, user_message: str, conversation_history: list[BaseMessage] = None) -> str:
        """
        Envia uma mensagem para o agente e recebe a resposta.
        
        Args:
            user_message: Pergunta do usuário
            conversation_history: Histórico de mensagens (opcional)
        
        Returns:
            Resposta do agente
        """
        # Preparar estado inicial
        messages = conversation_history or []
        messages.append(HumanMessage(content=user_message))
        
        initial_state = {
            "messages": messages,
            "next_action": "agent"
        }
        
        # Executar grafo
        final_state = self.graph.invoke(initial_state)
        
        # Extrair resposta
        last_message = final_state["messages"][-1]
        
        if hasattr(last_message, 'content'):
            return last_message.content
        
        return str(last_message)
    
    def chat_stream(self, user_message: str, conversation_history: list[BaseMessage] = None):
        """
        Versão streaming do chat (para interfaces interativas).
        
        Args:
            user_message: Pergunta do usuário
            conversation_history: Histórico de mensagens (opcional)
        
        Yields:
            Chunks da resposta conforme são gerados
        """
        messages = conversation_history or []
        messages.append(HumanMessage(content=user_message))
        
        initial_state = {
            "messages": messages,
            "next_action": "agent"
        }
        
        # Stream do grafo
        for event in self.graph.stream(initial_state):
            # Extrair mensagens do evento
            for key, value in event.items():
                if "messages" in value:
                    last_message = value["messages"][-1]
                    if hasattr(last_message, 'content') and last_message.content:
                        yield last_message.content
