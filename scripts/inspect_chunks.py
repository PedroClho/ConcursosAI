"""
Script para inspecionar chunks no ChromaDB
"""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from rag_pipeline import LawProcessor

load_dotenv()


def inspect_by_kind(processor: LawProcessor, kind: str):
    """Inspeciona chunks por tipo (kind)"""
    print(f"\n{'='*70}")
    print(f"CHUNKS DO TIPO: {kind.upper()}")
    print(f"{'='*70}")
    
    results = processor.collection.get(
        where={"kind": kind},
        limit=100
    )
    
    total = len(results['ids'])
    print(f"\nTotal de chunks: {total}")
    
    if total == 0:
        print("  [!] Nenhum chunk encontrado")
        return
    
    for i, (chunk_id, doc, meta) in enumerate(zip(results['ids'], results['documents'], results['metadatas']), 1):
        print(f"\n[{i}] ID: {chunk_id}")
        print(f"    Documento: {meta.get('document_name', 'N/A')}")
        print(f"    Tipo de chunk: {meta.get('chunk_type', 'N/A')}")
        
        if meta.get('chunk_type') == 'page':
            print(f"    Página: {meta.get('page_number', 'N/A')}")
        elif meta.get('chunk_type') == 'complete':
            print(f"    Intervalo: {meta.get('page_range', 'N/A')}")
        elif meta.get('article_number'):
            print(f"    Artigo: {meta.get('full_reference', 'N/A')}")
        
        print(f"    Tamanho: {len(doc)} caracteres")
        print(f"    Preview: {doc[:150].replace(chr(10), ' ')}...")


def main():
    """Inspeção completa"""
    print("="*70)
    print("INSPEÇÃO DE CHUNKS NO CHROMADB")
    print("="*70)
    
    processor = LawProcessor(
        chroma_persist_directory="./chroma_db",
        collection_name="oab_corpus"
    )
    
    # Estatísticas gerais
    stats = processor.get_collection_stats()
    print(f"\nEstatísticas Gerais:")
    print(f"  Total de itens: {stats['total_articles']}")
    print(f"  Coleção: {stats['collection_name']}")
    
    # Inspeção por tipo
    tipos = ["edital", "comunicado", "normativo", "lei"]
    
    for tipo in tipos:
        inspect_by_kind(processor, tipo)
    
    print("\n" + "="*70)
    print("INSPEÇÃO CONCLUÍDA")
    print("="*70)


if __name__ == "__main__":
    main()
