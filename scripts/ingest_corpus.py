"""
Script de Ingestão do Corpus no ChromaDB
Lê corpus_manifest.json e processa todos os documentos:
- Leis: divide por artigos
- Editais/Comunicados: divide por páginas ou mantém completo
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env ANTES de importar LawProcessor
load_dotenv()

sys.path.insert(0, 'src')
from rag_pipeline import LawProcessor


def process_law_document(processor: LawProcessor, doc: dict, manifest_meta: dict) -> dict:
    """
    Processa um documento de lei (divide por artigos).
    
    Args:
        processor: Instância do LawProcessor
        doc: Documento do manifest
        manifest_meta: Metadados do concurso (banca, fase, etc)
    
    Returns:
        Estatísticas do processamento
    """
    print(f"\n[LEI] Processando: {doc['title']}")
    print(f"      Arquivo: {doc['path']}")
    
    # Metadados adicionais do manifest
    additional_metadata = {
        "banca": manifest_meta["banca"],
        "concurso": manifest_meta["nome"],
        "fase": manifest_meta["fase"],
        "kind": doc["kind"],
        "doc_id": doc["id"],
        "tags": ",".join(doc["tags"]),  # ChromaDB aceita string
    }
    
    # Adicionar metadados customizados se existirem
    if "metadata" in doc:
        for key, value in doc["metadata"].items():
            if key != "source_type":  # Já temos implicitamente
                additional_metadata[key] = str(value)
    
    # Adicionar metadados extraídos se existirem
    if "extracted_metadata" in doc:
        ext_meta = doc["extracted_metadata"]
        additional_metadata["num_pages"] = ext_meta.get("num_pages", 0)
        additional_metadata["char_count"] = ext_meta.get("char_count", 0)
        if "extracted_date" in ext_meta:
            additional_metadata["document_date"] = ext_meta["extracted_date"]
    
    # Processar usando LawProcessor
    result = processor.process_law_pdf(
        pdf_path=doc["path"],
        law_name=doc["title"],
        additional_metadata=additional_metadata
    )
    
    return result


def process_non_law_document(processor: LawProcessor, doc: dict, manifest_meta: dict) -> dict:
    """
    Processa documentos que não são leis (editais, comunicados, normativos).
    Estratégia: divide por páginas ou mantém completo dependendo do tamanho.
    
    Args:
        processor: Instância do LawProcessor
        doc: Documento do manifest
        manifest_meta: Metadados do concurso
    
    Returns:
        Estatísticas do processamento
    """
    print(f"\n[{doc['kind'].upper()}] Processando: {doc['title']}")
    print(f"      Arquivo: {doc['path']}")
    
    pdf_path = doc["path"]
    
    if not os.path.exists(pdf_path):
        print(f"      [X] Arquivo não encontrado: {pdf_path}")
        return {"error": "Arquivo não encontrado"}
    
    # Extrair texto
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    
    # Metadados base
    base_metadata = {
        "banca": manifest_meta["banca"],
        "concurso": manifest_meta["nome"],
        "fase": manifest_meta["fase"],
        "kind": doc["kind"],
        "doc_id": doc["id"],
        "document_name": doc["title"],
        "tags": ",".join(doc["tags"]),
        "num_pages": num_pages,
    }
    
    # Adicionar metadados extraídos
    if "extracted_metadata" in doc:
        ext_meta = doc["extracted_metadata"]
        base_metadata["char_count"] = ext_meta.get("char_count", 0)
        if "extracted_date" in ext_meta:
            base_metadata["document_date"] = ext_meta["extracted_date"]
    
    # Estratégia: se <= 5 páginas, mantém completo; senão, divide por página
    chunks = []
    
    if num_pages <= 5:
        # Documento pequeno: manter completo
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        
        import re
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        chunk_metadata = base_metadata.copy()
        chunk_metadata["chunk_type"] = "complete"
        chunk_metadata["page_range"] = f"1-{num_pages}"
        
        chunks.append({
            "text": full_text,
            "metadata": chunk_metadata,
            "chunk_id": f"{doc['id']}_complete"
        })
        
        print(f"      [OK] Documento completo: {len(full_text)} caracteres")
    
    else:
        # Documento grande: dividir por página
        for i, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if not page_text or len(page_text.strip()) < 50:
                continue
            
            import re
            page_text = re.sub(r'\s+', ' ', page_text).strip()
            
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_type"] = "page"
            chunk_metadata["page_number"] = i
            
            chunks.append({
                "text": page_text,
                "metadata": chunk_metadata,
                "chunk_id": f"{doc['id']}_page_{i}"
            })
        
        print(f"      [OK] {len(chunks)} páginas processadas")
    
    # Gerar embeddings e salvar no ChromaDB
    if not chunks:
        print(f"      [!] Nenhum chunk gerado")
        return {"chunks_saved": 0}
    
    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["chunk_id"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    # Gerar embeddings
    print(f"      Gerando embeddings para {len(chunks)} chunks...")
    embeddings = processor.generate_embeddings_batch(texts)
    
    # Salvar no ChromaDB
    processor.collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    
    print(f"      [OK] {len(chunks)} chunks salvos no ChromaDB")
    
    return {
        "document_name": doc["title"],
        "chunks_saved": len(chunks),
        "total_chars": sum(len(c["text"]) for c in chunks)
    }


def ingest_corpus(
    manifest_path: str = "data/corpus_manifest.json",
    chroma_persist_dir: str = "./chroma_db",
    collection_name: str = "oab_corpus"
) -> dict:
    """
    Ingere todo o corpus no ChromaDB baseado no manifest.
    
    Args:
        manifest_path: Caminho para o corpus_manifest.json
        chroma_persist_dir: Diretório de persistência do ChromaDB
        collection_name: Nome da coleção
    
    Returns:
        Estatísticas gerais da ingestão
    """
    print("=" * 70)
    print("INGESTAO DO CORPUS NO CHROMADB")
    print("=" * 70)
    
    # Carregar manifest
    print(f"\n[1/3] Carregando manifest: {manifest_path}")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    concurso_meta = manifest["concurso"]
    documents = manifest["documents"]
    
    print(f"      Concurso: {concurso_meta['nome']}")
    print(f"      Banca: {concurso_meta['banca']}")
    print(f"      Fase: {concurso_meta['fase']}")
    print(f"      Total de documentos: {len(documents)}")
    
    # Inicializar LawProcessor
    print(f"\n[2/3] Inicializando ChromaDB")
    print(f"      Diretorio: {chroma_persist_dir}")
    print(f"      Colecao: {collection_name}")
    
    processor = LawProcessor(
        chroma_persist_directory=chroma_persist_dir,
        collection_name=collection_name
    )
    
    print(f"      [OK] ChromaDB inicializado")
    
    # Processar documentos
    print(f"\n[3/3] Processando {len(documents)} documentos...")
    
    stats = {
        "total_documents": len(documents),
        "processed": 0,
        "errors": 0,
        "laws_processed": 0,
        "non_laws_processed": 0,
        "total_articles": 0,
        "total_chunks": 0,
        "errors_list": []
    }
    
    for i, doc in enumerate(documents, 1):
        print(f"\n--- Documento {i}/{len(documents)} ---")
        
        try:
            if doc["kind"] == "lei":
                # Processar como lei (divide por artigos)
                result = process_law_document(processor, doc, concurso_meta)
                
                if "error" not in result:
                    stats["laws_processed"] += 1
                    stats["total_articles"] += result.get("articles_saved", 0)
                else:
                    stats["errors"] += 1
                    stats["errors_list"].append(doc["id"])
            
            else:
                # Processar como documento não-lei
                result = process_non_law_document(processor, doc, concurso_meta)
                
                if "error" not in result:
                    stats["non_laws_processed"] += 1
                    stats["total_chunks"] += result.get("chunks_saved", 0)
                else:
                    stats["errors"] += 1
                    stats["errors_list"].append(doc["id"])
            
            stats["processed"] += 1
        
        except Exception as e:
            print(f"      [X] Erro ao processar: {e}")
            stats["errors"] += 1
            stats["errors_list"].append(doc["id"])
    
    # Estatísticas finais
    print("\n" + "=" * 70)
    print("INGESTAO CONCLUIDA!")
    print("=" * 70)
    
    collection_stats = processor.get_collection_stats()
    
    print(f"\nEstatisticas de Processamento:")
    print(f"  Documentos processados: {stats['processed']}/{stats['total_documents']}")
    print(f"  Leis processadas: {stats['laws_processed']}")
    print(f"  Artigos indexados: {stats['total_articles']}")
    print(f"  Outros documentos: {stats['non_laws_processed']}")
    print(f"  Chunks de outros docs: {stats['total_chunks']}")
    print(f"  Erros: {stats['errors']}")
    
    print(f"\nEstatisticas do ChromaDB:")
    print(f"  Total de itens na colecao: {collection_stats['total_articles']}")
    print(f"  Colecao: {collection_stats['collection_name']}")
    print(f"  Diretorio: {collection_stats['persist_directory']}")
    
    if stats['errors_list']:
        print(f"\nDocumentos com erro:")
        for doc_id in stats['errors_list']:
            print(f"  - {doc_id}")
    
    # Salvar log de ingestão
    log_data = {
        "ingestion_date": datetime.now().isoformat(),
        "manifest_path": manifest_path,
        "collection_name": collection_name,
        "stats": stats,
        "collection_stats": collection_stats
    }
    
    log_path = "ingestion_log.json"
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Log salvo em: {log_path}")
    
    return stats


if __name__ == "__main__":
    # Verificar se o manifest existe
    if not os.path.exists("data/corpus_manifest.json"):
        print("[X] data/corpus_manifest.json nao encontrado!")
        print("    Execute scripts/enrich_manifest.py primeiro.")
        sys.exit(1)
    
    # Executar ingestão
    try:
        stats = ingest_corpus()
        
        print("\n" + "=" * 70)
        print("Proximos passos:")
        print("  1. Testar busca semantica: python test_search.py")
        print("  2. Ver estatisticas: python -c 'from rag_pipeline import LawProcessor; p=LawProcessor(collection_name=\"oab_corpus\"); print(p.get_collection_stats())'")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n[!] Ingestao interrompida pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
