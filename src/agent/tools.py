"""
Ferramentas (Tools) para o Agente Tutor OAB
"""

import sys
sys.path.insert(0, 'src')

from typing import Optional, Literal
from langchain_core.tools import tool, StructuredTool
from rag_pipeline import LawProcessor


class SearchTools:
    """Classe com ferramentas de busca para o agente"""
    
    def __init__(self, chroma_persist_directory: str = "./chroma_db", collection_name: str = "oab_corpus"):
        """Inicializa as ferramentas com conexão ao ChromaDB"""
        self.processor = LawProcessor(
            chroma_persist_directory=chroma_persist_directory,
            collection_name=collection_name
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
        # Montar filtros com sintaxe correta do ChromaDB
        if law_filter:
            filters = {
                "$and": [
                    {"kind": "lei"},
                    {"sigla": law_filter.upper()}
                ]
            }
        else:
            filters = {"kind": "lei"}
        
        results = self.processor.search(query, top_k=top_k, filter_metadata=filters)
        
        if not results:
            return f"Nenhum artigo encontrado para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            law_name = meta.get('law_name', 'N/A')
            article_ref = meta.get('full_reference', 'N/A')
            relevance = result['relevance_score']
            text = result['document'][:500]  # Limitar tamanho
            
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
        filters = {"kind": "edital"}
        results = self.processor.search(query, top_k=top_k, filter_metadata=filters)
        
        if not results:
            return f"Nenhuma informação encontrada no edital para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            doc_name = meta.get('document_name', 'Edital')
            relevance = result['relevance_score']
            text = result['document'][:400]
            
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
        filters = {"kind": "normativo"}
        results = self.processor.search(query, top_k=top_k, filter_metadata=filters)
        
        if not results:
            return f"Nenhuma informação encontrada no provimento para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            doc_name = meta.get('document_name', 'Provimento CFOAB')
            relevance = result['relevance_score']
            text = result['document'][:400]
            
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
        stats = self.processor.get_collection_stats()
        
        return (
            f"Base de Dados OAB:\n"
            f"- Total de itens: {stats['total_articles']}\n"
            f"- Leis indexadas: {stats['laws_count']}\n"
            f"- Leis disponíveis: {', '.join(stats['laws']) if stats['laws'] else 'Nenhuma'}\n"
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
