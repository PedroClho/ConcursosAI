"""
RAG Pipeline para Concursos Brasileiros
Módulo para processamento de leis e documentos jurídicos
"""

from .law_processor import LawProcessor
from .supabase_rag import SupabaseRAGProcessor

__all__ = ["LawProcessor", "SupabaseRAGProcessor"]
__version__ = "0.1.0"
