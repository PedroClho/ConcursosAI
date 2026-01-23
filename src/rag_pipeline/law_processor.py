"""
Processador de Leis para RAG Pipeline
Extrai artigos de PDFs de leis brasileiras, gera embeddings e armazena no ChromaDB
"""

import re
import os
from typing import Optional
from dataclasses import dataclass

from openai import OpenAI
from pypdf import PdfReader
import chromadb
from chromadb.config import Settings


@dataclass
class ArticleChunk:
    """Representa um artigo extraído de uma lei"""
    article_number: str
    content: str
    law_name: str
    metadata: dict


class LawProcessor:
    """
    Classe para processar PDFs de leis brasileiras.
    
    Funcionalidades:
    - Extrai texto de PDFs
    - Divide o texto por artigos usando regex
    - Gera embeddings usando OpenAI
    - Armazena no ChromaDB local
    
    Exemplo de uso:
        processor = LawProcessor(openai_api_key="sua-chave")
        processor.process_law_pdf("constituicao.pdf", "Constituição Federal")
        results = processor.search("direitos fundamentais", top_k=5)
    """
    
    # Padrões regex para identificar artigos em leis brasileiras
    ARTICLE_PATTERNS = [
        # Art. 1º, Art. 2º, Art. 10, Art. 100
        r'(Art\.\s*\d+[º°]?[\.\s\-]+)',
        # Artigo 1º, Artigo 2º
        r'(Artigo\s+\d+[º°]?[\.\s\-]+)',
        # Art 1º - sem ponto após Art
        r'(Art\s+\d+[º°]?[\.\s\-]+)',
    ]
    
    # Padrão combinado para split
    SPLIT_PATTERN = r'(?=Art\.?\s*\d+[º°]?[\.\s\-])'
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        chroma_persist_directory: str = "./chroma_db",
        collection_name: str = "leis_brasileiras",
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Inicializa o processador de leis.
        
        Args:
            openai_api_key: Chave da API OpenAI. Se None, usa OPENAI_API_KEY do ambiente.
            chroma_persist_directory: Diretório para persistir o ChromaDB.
            collection_name: Nome da coleção no ChromaDB.
            embedding_model: Modelo de embedding da OpenAI a ser usado.
        """
        # Configurar cliente OpenAI
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API Key da OpenAI não fornecida. "
                "Passe como parâmetro ou defina OPENAI_API_KEY no ambiente."
            )
        
        self.openai_client = OpenAI(api_key=self.api_key)
        self.embedding_model = embedding_model
        
        # Configurar ChromaDB com persistência local
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Obter ou criar coleção
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Leis brasileiras para estudo de concursos"}
        )
        
        self.chroma_persist_directory = chroma_persist_directory
        self.collection_name = collection_name
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto completo de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF.
            
        Returns:
            Texto extraído do PDF.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        full_text = "\n".join(text_parts)
        
        # Limpar texto: remover múltiplos espaços e quebras de linha excessivas
        full_text = re.sub(r'\s+', ' ', full_text)
        full_text = re.sub(r'\n\s*\n', '\n\n', full_text)
        
        return full_text.strip()
    
    def split_by_articles(self, text: str) -> list[dict]:
        """
        Divide o texto da lei em artigos individuais usando regex.
        
        Args:
            text: Texto completo da lei.
            
        Returns:
            Lista de dicionários com número do artigo e conteúdo.
        """
        # Dividir texto pelos artigos
        parts = re.split(self.SPLIT_PATTERN, text, flags=re.IGNORECASE)
        
        articles = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Extrair número do artigo
            match = re.match(
                r'Art\.?\s*(\d+)[º°]?[\.\s\-]+(.+)',
                part,
                flags=re.IGNORECASE | re.DOTALL
            )
            
            if match:
                article_number = match.group(1)
                content = match.group(2).strip()
                
                # Limpar conteúdo
                content = re.sub(r'\s+', ' ', content)
                
                articles.append({
                    "article_number": article_number,
                    "full_reference": f"Art. {article_number}º",
                    "content": content,
                    "full_text": part.strip()
                })
        
        return articles
    
    def generate_embedding(self, text: str) -> list[float]:
        """
        Gera embedding para um texto usando a API da OpenAI.
        
        Args:
            text: Texto para gerar embedding.
            
        Returns:
            Lista de floats representando o embedding.
        """
        # Truncar texto se necessário (limite do modelo)
        max_tokens = 8000  # Limite conservador
        if len(text) > max_tokens * 4:  # Aproximação: 4 chars por token
            text = text[:max_tokens * 4]
        
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        
        return response.data[0].embedding
    
    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Gera embeddings para múltiplos textos em batch.
        
        Args:
            texts: Lista de textos para gerar embeddings.
            
        Returns:
            Lista de embeddings.
        """
        # API da OpenAI suporta até 2048 inputs por request
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Truncar textos muito longos
            processed_batch = []
            for text in batch:
                if len(text) > 32000:  # ~8000 tokens
                    text = text[:32000]
                processed_batch.append(text)
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=processed_batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def save_to_chromadb(
        self,
        articles: list[dict],
        law_name: str,
        additional_metadata: Optional[dict] = None
    ) -> int:
        """
        Salva os artigos no ChromaDB com seus embeddings.
        
        Args:
            articles: Lista de artigos extraídos.
            law_name: Nome da lei para referência.
            additional_metadata: Metadados adicionais (banca, edital, etc).
            
        Returns:
            Número de artigos salvos.
        """
        if not articles:
            return 0
        
        # Preparar textos para embedding
        texts = [article["full_text"] for article in articles]
        
        # Gerar embeddings em batch
        print(f"Gerando embeddings para {len(texts)} artigos...")
        embeddings = self.generate_embeddings_batch(texts)
        
        # Preparar dados para ChromaDB
        ids = []
        documents = []
        metadatas = []
        
        for i, article in enumerate(articles):
            # ID único: nome_da_lei_artigo_numero_índice
            # Usar índice sempre para garantir unicidade (artigos duplicados = parágrafos/incisos)
            safe_law_name = re.sub(r'[^a-zA-Z0-9]', '_', law_name)
            doc_id = f"{safe_law_name}_art_{article['article_number']}_{i}"
            
            ids.append(doc_id)
            documents.append(article["full_text"])
            
            # Metadados
            metadata = {
                "law_name": law_name,
                "article_number": article["article_number"],
                "full_reference": article["full_reference"],
            }
            
            if additional_metadata:
                metadata.update(additional_metadata)
            
            metadatas.append(metadata)
        
        # Inserir no ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"[OK] {len(ids)} artigos salvos no ChromaDB")
        return len(ids)
    
    def process_law_pdf(
        self,
        pdf_path: str,
        law_name: str,
        additional_metadata: Optional[dict] = None
    ) -> dict:
        """
        Processa um PDF de lei completo: extrai, divide, gera embeddings e salva.
        
        Args:
            pdf_path: Caminho para o arquivo PDF.
            law_name: Nome da lei para referência.
            additional_metadata: Metadados adicionais (banca, ano, edital, etc).
            
        Returns:
            Dicionário com estatísticas do processamento.
        """
        print(f"Processando: {law_name}")
        print(f"Arquivo: {pdf_path}")
        
        # 1. Extrair texto do PDF
        print("1. Extraindo texto do PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        print(f"   -> {len(text)} caracteres extraidos")
        
        # 2. Dividir por artigos
        print("2. Dividindo texto por artigos...")
        articles = self.split_by_articles(text)
        print(f"   -> {len(articles)} artigos encontrados")
        
        if not articles:
            print("[!] Nenhum artigo encontrado no documento")
            return {
                "law_name": law_name,
                "pdf_path": pdf_path,
                "characters_extracted": len(text),
                "articles_found": 0,
                "articles_saved": 0
            }
        
        # 3. Gerar embeddings e salvar no ChromaDB
        print("3. Gerando embeddings e salvando no ChromaDB...")
        saved_count = self.save_to_chromadb(articles, law_name, additional_metadata)
        
        print(f"\n[OK] Processamento concluido!")
        
        return {
            "law_name": law_name,
            "pdf_path": pdf_path,
            "characters_extracted": len(text),
            "articles_found": len(articles),
            "articles_saved": saved_count
        }
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[dict] = None
    ) -> list[dict]:
        """
        Busca artigos relevantes para uma consulta.
        
        Args:
            query: Texto da consulta.
            top_k: Número de resultados a retornar.
            filter_metadata: Filtros de metadados (ex: {"law_name": "Constituição Federal"}).
            
        Returns:
            Lista de artigos relevantes com scores.
        """
        # Gerar embedding da query
        query_embedding = self.generate_embedding(query)
        
        # Buscar no ChromaDB
        where_filter = filter_metadata if filter_metadata else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Formatar resultados
        formatted_results = []
        
        if results and results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                formatted_results.append({
                    "id": doc_id,
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i],
                    "relevance_score": 1 - results['distances'][0][i]  # Converter distância em score
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> dict:
        """
        Retorna estatísticas da coleção no ChromaDB.
        
        Returns:
            Dicionário com estatísticas.
        """
        count = self.collection.count()
        
        # Obter leis únicas
        all_data = self.collection.get(include=["metadatas"])
        laws = set()
        
        if all_data and all_data['metadatas']:
            for metadata in all_data['metadatas']:
                if metadata and 'law_name' in metadata:
                    laws.add(metadata['law_name'])
        
        return {
            "total_articles": count,
            "laws_count": len(laws),
            "laws": list(laws),
            "collection_name": self.collection_name,
            "persist_directory": self.chroma_persist_directory
        }
    
    def delete_law(self, law_name: str) -> int:
        """
        Remove todos os artigos de uma lei específica.
        
        Args:
            law_name: Nome da lei a ser removida.
            
        Returns:
            Número de artigos removidos.
        """
        # Buscar IDs dos artigos da lei
        results = self.collection.get(
            where={"law_name": law_name},
            include=["metadatas"]
        )
        
        if not results or not results['ids']:
            return 0
        
        ids_to_delete = results['ids']
        self.collection.delete(ids=ids_to_delete)
        
        return len(ids_to_delete)


# Exemplo de uso
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar argumentos
    if len(sys.argv) < 3:
        print("Uso: python law_processor.py <caminho_pdf> <nome_lei>")
        print("Exemplo: python law_processor.py constituicao.pdf 'Constituição Federal'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    law_name = sys.argv[2]
    
    # Processar lei
    processor = LawProcessor()
    result = processor.process_law_pdf(pdf_path, law_name)
    
    print("\nResultado do processamento:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # Mostrar estatísticas
    stats = processor.get_collection_stats()
    print("\nEstatisticas da colecao:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
