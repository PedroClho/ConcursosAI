"""
Script de teste para busca semântica no corpus OAB
"""

import sys
sys.path.insert(0, 'src')
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

from rag_pipeline import LawProcessor


def test_search():
    """Testa a busca semântica com exemplos da OAB"""
    
    print("=" * 70)
    print("TESTE DE BUSCA SEMANTICA - CORPUS OAB")
    print("=" * 70)
    
    # Inicializar processador
    processor = LawProcessor(
        chroma_persist_directory="./chroma_db",
        collection_name="oab_corpus"
    )
    
    # Estatísticas
    stats = processor.get_collection_stats()
    print(f"\nEstatisticas da colecao:")
    print(f"  Total de itens: {stats['total_articles']}")
    print(f"  Colecao: {stats['collection_name']}")
    
    # Queries de teste
    test_queries = [
        {
            "query": "direitos e garantias fundamentais",
            "filter": {"kind": "lei"},
            "description": "Busca na CF - Direitos Fundamentais"
        },
        {
            "query": "prazo para recurso e contestacao",
            "filter": {"kind": "lei"},
            "description": "Busca processual - Prazos"
        },
        {
            "query": "data e horario da prova do exame de ordem",
            "filter": {"kind": "edital"},
            "description": "Busca no edital - Informacoes da prova"
        },
        {
            "query": "como funciona a inscricao no exame de ordem",
            "filter": {"kind": "normativo"},
            "description": "Busca no Provimento - Inscricao"
        },
        {
            "query": "prisao em flagrante",
            "filter": {"sigla": "CPP"},
            "description": "Busca no CPP - Prisao"
        }
    ]
    
    # Executar buscas
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'=' * 70}")
        print(f"TESTE {i}: {test['description']}")
        print(f"Query: \"{test['query']}\"")
        if test.get('filter'):
            print(f"Filtros: {test['filter']}")
        print("-" * 70)
        
        results = processor.search(
            query=test['query'],
            top_k=3,
            filter_metadata=test.get('filter')
        )
        
        if not results:
            print("  [!] Nenhum resultado encontrado")
            continue
        
        for j, result in enumerate(results, 1):
            metadata = result['metadata']
            print(f"\n  Resultado {j}:")
            print(f"    Relevancia: {result['relevance_score']:.1%}")
            print(f"    Documento: {metadata.get('document_name', metadata.get('law_name', 'N/A'))}")
            print(f"    Tipo: {metadata.get('kind', 'N/A')}")
            
            # Mostrar artigo se for lei
            if 'article_number' in metadata:
                print(f"    Artigo: {metadata.get('full_reference', 'N/A')}")
            
            # Preview do conteúdo
            preview = result['document'][:200].replace('\n', ' ')
            print(f"    Trecho: {preview}...")
    
    print("\n" + "=" * 70)
    print("TESTE CONCLUIDO")
    print("=" * 70)


if __name__ == "__main__":
    test_search()
