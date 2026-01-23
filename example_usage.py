"""
Exemplo de uso do LawProcessor
Demonstra como processar uma lei e fazer buscas semânticas
"""

import sys
sys.path.insert(0, 'src')
from dotenv import load_dotenv
from rag_pipeline import LawProcessor

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


def main():
    """Exemplo completo de uso do LawProcessor"""
    
    # 1. Inicializar o processador
    print("=" * 60)
    print("Inicializando LawProcessor...")
    print("=" * 60)
    
    processor = LawProcessor(
        chroma_persist_directory="./chroma_db",
        collection_name="leis_concursos"
    )
    
    # 2. Processar um PDF de lei (descomente e ajuste o caminho)
    # result = processor.process_law_pdf(
    #     pdf_path="./pdfs/constituicao_federal.pdf",
    #     law_name="Constituição Federal de 1988",
    #     additional_metadata={
    #         "banca": "CESPE",
    #         "cargo": "Analista Judiciário",
    #         "ano_edital": "2024",
    #         "tema": "Direito Constitucional"
    #     }
    # )
    # print(f"\nResultado: {result}")
    
    # 3. Verificar estatísticas da coleção
    print("\n" + "=" * 60)
    print("Estatísticas da Coleção")
    print("=" * 60)
    
    stats = processor.get_collection_stats()
    print(f"Total de artigos: {stats['total_articles']}")
    print(f"Leis indexadas: {stats['laws_count']}")
    if stats['laws']:
        print("Leis:")
        for law in stats['laws']:
            print(f"  - {law}")
    
    # 4. Exemplo de busca (funciona apenas se houver dados)
    if stats['total_articles'] > 0:
        print("\n" + "=" * 60)
        print("Exemplo de Busca Semântica")
        print("=" * 60)
        
        query = "direitos fundamentais do cidadão"
        print(f"Buscando: '{query}'")
        
        results = processor.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Resultado {i} ---")
            print(f"Lei: {result['metadata'].get('law_name', 'N/A')}")
            print(f"Artigo: {result['metadata'].get('full_reference', 'N/A')}")
            print(f"Relevância: {result['relevance_score']:.2%}")
            print(f"Trecho: {result['document'][:300]}...")
    else:
        print("\n⚠ Nenhum dado na coleção. Processe um PDF primeiro.")
        print("Descomente as linhas de process_law_pdf e ajuste o caminho.")


if __name__ == "__main__":
    main()
