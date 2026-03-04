"""
Ferramentas (Tools) para o Agente Tutor OAB
"""

from typing import Optional, Literal
from langchain_core.tools import tool, StructuredTool
from ..rag_pipeline.supabase_rag import SupabaseRAGProcessor


class SearchTools:
    """Classe com ferramentas de busca para o agente"""
    
    def __init__(self, supabase_url: str, supabase_key: str, openai_key: str):
        """Inicializa as ferramentas com conexão ao Supabase"""
        self.rag = SupabaseRAGProcessor(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            openai_key=openai_key
        )
    
    def search_laws(self, query: str, law_filter: Optional[str] = None, top_k: int = 3) -> str:
        """
        Busca artigos de leis (CF, CPC, CPP, CTN) relevantes para uma consulta.
        
        Args:
            query: Pergunta ou tema a buscar
            law_filter: Filtrar por lei específica: "CF", "CPC", "CPP", ou "CTN" (opcional)
            top_k: Número de resultados (padrão: 3)
        
        Returns:
            Texto formatado com artigos encontrados e suas referências
        """
        # Buscar usando Supabase RAG
        results = self.rag.search(
            query=query,
            top_k=top_k,
            filter_kind="lei",
            match_threshold=0.5
        )
        
        if not results:
            return f"Nenhum artigo encontrado para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            law_name = meta.get('law_name', 'N/A')
            article_ref = meta.get('full_reference', 'N/A')
            relevance = result['similarity']
            text = result['content'][:500]  # Limitar tamanho
            
            output.append(
                f"[{i}] {law_name} - {article_ref} (Relevância: {relevance:.1%})\n"
                f"{text}...\n"
            )
        
        return "\n".join(output)
    
    def search_edital(self, query: str, top_k: int = 2) -> str:
        """
        Busca informações nos editais do Exame de Ordem (datas, locais, horários, regras).
        
        Args:
            query: Pergunta sobre o edital (ex: "data da prova", "local de prova")
            top_k: Número de resultados (padrão: 2)
        
        Returns:
            Texto com informações do edital
        """
        results = self.rag.search(
            query=query,
            top_k=top_k,
            filter_kind="edital",
            match_threshold=0.5
        )
        
        if not results:
            return f"Nenhuma informação encontrada no edital para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            doc_name = meta.get('document_name', 'Edital')
            relevance = result['similarity']
            text = result['content'][:400]
            
            output.append(
                f"[{i}] {doc_name} (Relevância: {relevance:.1%})\n"
                f"{text}...\n"
            )
        
        return "\n".join(output)
    
    def search_provimento(self, query: str, top_k: int = 2) -> str:
        """
        Busca regras do Provimento CFOAB (inscrição, recursos, aprovação no Exame de Ordem).
        
        Args:
            query: Pergunta sobre as regras do exame
            top_k: Número de resultados (padrão: 2)
        
        Returns:
            Texto com regras do provimento
        """
        results = self.rag.search(
            query=query,
            top_k=top_k,
            filter_kind="normativo",
            match_threshold=0.5
        )
        
        if not results:
            return f"Nenhuma informação encontrada no provimento para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            doc_name = meta.get('document_name', 'Provimento CFOAB')
            relevance = result['similarity']
            text = result['content'][:400]
            
            output.append(
                f"[{i}] {doc_name} (Relevância: {relevance:.1%})\n"
                f"{text}...\n"
            )
        
        return "\n".join(output)
    
    def get_database_stats(self) -> str:
        """
        Retorna estatísticas da base de dados (quantas leis, artigos, documentos estão indexados).
        
        Returns:
            Texto com estatísticas
        """
        stats = self.rag.get_stats_by_eixo()
        
        return (
            f"Base de Dados OAB (Supabase):\n"
            f"- Total de embeddings: {stats.get('total_embeddings', 0)}\n"
            f"- Total de artigos: {stats.get('total_artigos', 0)}\n"
            f"- Documentos: {stats.get('total_documents', 0)}\n"
            f"- Eixo Ético: {stats.get('artigos_etico', 0)} artigos\n"
            f"- Eixo Fundamental: {stats.get('artigos_fundamental', 0)} artigos\n"
            f"- Eixo Administrativo: {stats.get('artigos_administrativo', 0)} artigos\n"
            f"- Questões OAB: {stats.get('total_questoes', 0)}\n"
        )
    
    def get_all_tools(self):
        """Retorna lista de todas as ferramentas disponíveis para o agente"""
        # Criar StructuredTools vinculadas à instância
        return [
            StructuredTool.from_function(
                func=self.search_laws,
                name="search_laws",
                description="""Busca artigos de leis (CF, CPC, CPP, CTN) relevantes para uma consulta.
                
Args:
    query: Pergunta ou tema a buscar
    law_filter: Filtrar por lei específica: "CF", "CPC", "CPP", ou "CTN" (opcional)
    top_k: Número de resultados (padrão: 3)

Returns:
    Texto formatado com artigos encontrados e suas referências"""
            ),
            StructuredTool.from_function(
                func=self.search_edital,
                name="search_edital",
                description="""Busca informações nos editais do Exame de Ordem (datas, locais, horários, regras).

Args:
    query: Pergunta sobre o edital (ex: "data da prova", "local de prova")
    top_k: Número de resultados (padrão: 2)

Returns:
    Texto com informações do edital"""
            ),
            StructuredTool.from_function(
                func=self.search_provimento,
                name="search_provimento",
                description="""Busca regras do Provimento CFOAB (inscrição, recursos, aprovação no Exame de Ordem).

Args:
    query: Pergunta sobre as regras do exame
    top_k: Número de resultados (padrão: 2)

Returns:
    Texto com regras do provimento"""
            ),
            StructuredTool.from_function(
                func=self.get_database_stats,
                name="get_database_stats",
                description="""Retorna estatísticas da base de dados (quantas leis, artigos, documentos estão indexados).

Returns:
    Texto com estatísticas"""
            ),
        ]
