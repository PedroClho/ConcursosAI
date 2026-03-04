"""
SupabaseRAGProcessor - Processador RAG com Supabase
Substitui o ChromaDB local por Supabase PostgreSQL com pgvector
"""

import os
from typing import List, Dict, Optional
from supabase import create_client
from openai import OpenAI


class SupabaseRAGProcessor:
    """
    Processador RAG usando Supabase como backend
    
    Funcionalidades:
    - Busca vetorial com pgvector
    - Filtros por eixo, tags, tipo
    - Estatísticas por eixo
    """
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        openai_key: str,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Inicializar o processador RAG com Supabase
        
        Args:
            supabase_url: URL do projeto Supabase
            supabase_key: Service key do Supabase
            openai_key: API key da OpenAI
            embedding_model: Modelo de embedding a usar
        """
        self.supabase = create_client(supabase_url, supabase_key)
        self.openai = OpenAI(api_key=openai_key)
        self.embedding_model = embedding_model
    
    def generate_embedding(self, text: str) -> List[float]:
        """Gerar embedding para um texto"""
        # Truncar se necessário
        if len(text) > 32000:
            text = text[:32000]
        
        response = self.openai.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        
        return response.data[0].embedding
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_kind: Optional[str] = None,
        filter_tags: Optional[List[str]] = None,
        match_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Buscar documentos relevantes
        
        Args:
            query: Consulta em linguagem natural
            top_k: Número de resultados
            filter_kind: Filtrar por tipo (lei, edital, etc)
            filter_tags: Filtrar por tags
            match_threshold: Threshold mínimo de similaridade
            
        Returns:
            Lista de resultados com conteúdo e metadata
        """
        # Gerar embedding da query
        embedding = self.generate_embedding(query)
        
        # Buscar usando função SQL
        results = self.supabase.rpc('search_embeddings', {
            'query_embedding': embedding,
            'match_count': top_k,
            'match_threshold': match_threshold,
            'filter_kind': filter_kind,
            'filter_tags': filter_tags
        }).execute()
        
        # Hidratar resultados com conteúdo original
        return self.hydrate_results(results.data)
    
    def search_by_eixo(
        self,
        query: str,
        eixo: str,
        top_k: int = 5,
        match_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Buscar apenas em um eixo específico
        
        Args:
            query: Consulta
            eixo: Nome do eixo (etico, fundamental, administrativo)
            top_k: Número de resultados
            match_threshold: Threshold mínimo de similaridade (padrão: 0.5)
            
        Returns:
            Resultados filtrados por eixo
        """
        return self.search(query, top_k=top_k, filter_tags=[eixo], match_threshold=match_threshold)
    
    def search_etico(self, query: str, top_k: int = 5, match_threshold: float = 0.5) -> List[Dict]:
        """Atalho para buscar no eixo ético"""
        return self.search_by_eixo(query, 'etico', top_k, match_threshold)
    
    def search_fundamental(self, query: str, top_k: int = 5, match_threshold: float = 0.5) -> List[Dict]:
        """Atalho para buscar no eixo fundamental"""
        return self.search_by_eixo(query, 'fundamental', top_k, match_threshold)
    
    def search_administrativo(self, query: str, top_k: int = 5, match_threshold: float = 0.5) -> List[Dict]:
        """Atalho para buscar no eixo administrativo"""
        return self.search_by_eixo(query, 'administrativo', top_k, match_threshold)
    
    def search_questoes(
        self,
        query: str,
        top_k: int = 5,
        filter_materia: Optional[str] = None,
        filter_ano: Optional[int] = None,
        filter_tags: Optional[List[str]] = None,
        match_threshold: float = 0.5
    ) -> List[Dict]:
        """
        Buscar questões OAB por similaridade semântica
        
        Args:
            query: Consulta em linguagem natural
            top_k: Número de resultados
            filter_materia: Filtrar por matéria
            filter_ano: Filtrar por ano
            filter_tags: Filtrar por tags
            match_threshold: Threshold mínimo de similaridade
            
        Returns:
            Lista de questões relevantes
        """
        # Gerar embedding da query
        embedding = self.generate_embedding(query)
        
        # Buscar usando função SQL
        results = self.supabase.rpc('search_questoes', {
            'query_embedding': embedding,
            'match_count': top_k,
            'match_threshold': match_threshold,
            'filter_materia': filter_materia,
            'filter_ano': filter_ano,
            'filter_tags': filter_tags
        }).execute()
        
        return results.data if results.data else []
    
    def search_questoes_similares(
        self,
        questao_id: str,
        top_k: int = 5,
        match_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Buscar questões similares a uma questão específica
        
        Args:
            questao_id: ID da questão de referência
            top_k: Número de resultados
            match_threshold: Threshold mínimo de similaridade
            
        Returns:
            Lista de questões similares
        """
        results = self.supabase.rpc('search_questoes_similares', {
            'questao_id': questao_id,
            'match_count': top_k,
            'match_threshold': match_threshold
        }).execute()
        
        return results.data if results.data else []
    
    def search_questoes_por_artigo(
        self,
        artigo_id: str,
        top_k: int = 10,
        match_threshold: float = 0.6
    ) -> List[Dict]:
        """
        Buscar questões relacionadas a um artigo de lei
        
        Args:
            artigo_id: ID do artigo de lei
            top_k: Número de resultados
            match_threshold: Threshold mínimo de similaridade
            
        Returns:
            Lista de questões relacionadas
        """
        results = self.supabase.rpc('search_questoes_por_artigo', {
            'artigo_id': artigo_id,
            'match_count': top_k,
            'match_threshold': match_threshold
        }).execute()
        
        return results.data if results.data else []
    
    def search_rag_completo(
        self,
        query: str,
        match_count_questoes: int = 5,
        match_count_artigos: int = 5,
        filter_materia: Optional[str] = None,
        match_threshold: float = 0.5
    ) -> Dict[str, List[Dict]]:
        """
        Busca híbrida que retorna questões e artigos relacionados
        
        Args:
            query: Consulta em linguagem natural
            match_count_questoes: Número de questões
            match_count_artigos: Número de artigos
            filter_materia: Filtrar por matéria
            match_threshold: Threshold mínimo de similaridade
            
        Returns:
            Dicionário com 'questoes' e 'artigos'
        """
        # Gerar embedding da query
        embedding = self.generate_embedding(query)
        
        # Buscar usando função SQL
        results = self.supabase.rpc('search_rag_completo', {
            'query_embedding': embedding,
            'match_threshold': match_threshold,
            'match_count_questoes': match_count_questoes,
            'match_count_artigos': match_count_artigos,
            'filter_materia': filter_materia
        }).execute()
        
        # Separar questões e artigos
        questoes = []
        artigos = []
        
        for item in (results.data or []):
            if item['tipo'] == 'questao':
                questoes.append(item)
            elif item['tipo'] == 'artigo':
                artigos.append(item)
        
        return {
            'questoes': questoes,
            'artigos': artigos
        }
    
    def hydrate_results(self, matches: List[Dict]) -> List[Dict]:
        """
        Recuperar conteúdo completo dos resultados
        
        Args:
            matches: Resultados da busca vetorial
            
        Returns:
            Resultados com conteúdo completo
        """
        results = []
        
        for match in matches:
            source_type = match['source_type']
            source_id = match['source_id']
            
            try:
                if source_type == 'law_article':
                    article = self.supabase.table('law_articles')\
                        .select('*')\
                        .eq('id', source_id)\
                        .single()\
                        .execute()
                    
                    results.append({
                        'type': 'law_article',
                        'content': article.data['full_text'],
                        'metadata': article.data,
                        'similarity': match['similarity']
                    })
                
                elif source_type == 'document_chunk':
                    chunk = self.supabase.table('document_chunks')\
                        .select('*')\
                        .eq('id', source_id)\
                        .single()\
                        .execute()
                    
                    results.append({
                        'type': 'document_chunk',
                        'content': chunk.data['content'],
                        'metadata': chunk.data,
                        'similarity': match['similarity']
                    })
                
                elif source_type == 'questao':
                    questao = self.supabase.table('questoes_oab')\
                        .select('*')\
                        .eq('id', source_id)\
                        .single()\
                        .execute()
                    
                    results.append({
                        'type': 'questao',
                        'content': questao.data['enunciado'],
                        'metadata': questao.data,
                        'similarity': match['similarity']
                    })
            
            except Exception as e:
                print(f"[!] Erro ao recuperar {source_id}: {e}")
                continue
        
        return results
    
    def get_stats_by_eixo(self) -> Dict[str, int]:
        """
        Obter estatísticas por eixo
        
        Returns:
            Dicionário com contagem por eixo
        """
        try:
            stats = self.supabase.table('rag_stats_completo')\
                .select('*')\
                .execute()
            
            if stats.data:
                return stats.data[0]
            
            return {}
        
        except Exception as e:
            print(f"[!] Erro ao obter estatísticas: {e}")
            return {}


# Exemplo de uso
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    rag = SupabaseRAGProcessor(
        supabase_url=os.getenv('SUPABASE_URL'),
        supabase_key=os.getenv('SUPABASE_SERVICE_KEY'),
        openai_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Teste de busca
    results = rag.search_etico("deveres do advogado", top_k=3)
    
    print("\nResultados da busca:")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] Similaridade: {r['similarity']:.2f}")
        print(f"    Lei: {r['metadata'].get('law_name')}")
        print(f"    Ref: {r['metadata'].get('full_reference')}")
        print(f"    Conteúdo: {r['content'][:200]}...")
