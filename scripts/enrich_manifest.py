"""
Script para enriquecer o corpus_manifest.json com metadados extraídos dos PDFs
Lê cada PDF, extrai título oficial, data, páginas, preview e valida extração
"""

import json
import os
import re
from datetime import datetime
from pypdf import PdfReader
from pathlib import Path


def extract_pdf_metadata(pdf_path: str) -> dict:
    """
    Extrai metadados de um PDF.
    
    Returns:
        dict com: num_pages, extracted_title, extracted_date, 
                  preview, char_count, extraction_quality
    """
    if not os.path.exists(pdf_path):
        return {
            "error": "Arquivo não encontrado",
            "exists": False
        }
    
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        # Extrair texto das primeiras 3 páginas para metadados
        preview_text = ""
        for i in range(min(3, num_pages)):
            page_text = reader.pages[i].extract_text()
            if page_text:
                preview_text += page_text + "\n"
        
        # Limpar texto
        preview_text = re.sub(r'\s+', ' ', preview_text).strip()
        
        # Extrair texto completo para estatísticas
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        char_count = len(full_text)
        
        # Tentar extrair título (primeiras linhas significativas)
        lines = preview_text.split('\n')[:10]
        title_candidates = []
        for line in lines:
            line = line.strip()
            # Linhas com pelo menos 10 chars e que não sejam só números
            if len(line) >= 10 and not re.match(r'^[\d\s\-/]+$', line):
                title_candidates.append(line)
        
        extracted_title = title_candidates[0] if title_candidates else preview_text[:100]
        
        # Tentar extrair data (vários formatos comuns em documentos brasileiros)
        date_patterns = [
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',  # 15 de janeiro de 2024
            r'(\d{2})/(\d{2})/(\d{4})',                 # 15/01/2024
            r'(\d{4})-(\d{2})-(\d{2})',                 # 2024-01-15
            r'Brasília[,\s]+(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
        ]
        
        extracted_date = None
        for pattern in date_patterns:
            match = re.search(pattern, preview_text, re.IGNORECASE)
            if match:
                extracted_date = match.group(0)
                break
        
        # Avaliar qualidade da extração
        avg_chars_per_page = char_count / num_pages if num_pages > 0 else 0
        
        if avg_chars_per_page < 100:
            quality = "baixa (possível OCR/imagem)"
        elif avg_chars_per_page < 1000:
            quality = "média"
        else:
            quality = "boa"
        
        # Tentar extrair número de artigos (para leis)
        article_matches = re.findall(r'\bArt\.?\s*\d+', full_text, re.IGNORECASE)
        num_articles_detected = len(set(article_matches))  # Unique articles
        
        return {
            "exists": True,
            "num_pages": num_pages,
            "extracted_title": extracted_title[:200],  # Limitar tamanho
            "extracted_date": extracted_date,
            "preview": preview_text[:500],
            "char_count": char_count,
            "avg_chars_per_page": round(avg_chars_per_page, 1),
            "extraction_quality": quality,
            "num_articles_detected": num_articles_detected if num_articles_detected > 0 else None,
            "file_size_mb": round(os.path.getsize(pdf_path) / (1024 * 1024), 2)
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "exists": True
        }


def enrich_manifest(manifest_path: str = "data/corpus_manifest.json") -> dict:
    """
    Lê o manifest, enriquece cada documento com metadados dos PDFs e salva.
    
    Returns:
        Estatísticas do processamento
    """
    print("=" * 70)
    print("Enriquecendo corpus_manifest.json com metadados dos PDFs")
    print("=" * 70)
    
    # Carregar manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    stats = {
        "total_docs": len(manifest["documents"]),
        "processed": 0,
        "errors": 0,
        "low_quality": []
    }
    
    # Processar cada documento
    for doc in manifest["documents"]:
        doc_id = doc["id"]
        doc_path = doc["path"]
        
        print(f"\n[*] Processando: {doc_id}")
        print(f"    Arquivo: {doc_path}")
        
        # Extrair metadados
        pdf_metadata = extract_pdf_metadata(doc_path)
        
        if "error" in pdf_metadata:
            print(f"    [X] Erro: {pdf_metadata['error']}")
            doc["extraction_status"] = "error"
            doc["extraction_error"] = pdf_metadata["error"]
            stats["errors"] += 1
            continue
        
        # Atualizar documento com metadados extraídos
        doc["extracted_metadata"] = {
            "num_pages": pdf_metadata["num_pages"],
            "extracted_title": pdf_metadata["extracted_title"],
            "char_count": pdf_metadata["char_count"],
            "avg_chars_per_page": pdf_metadata["avg_chars_per_page"],
            "extraction_quality": pdf_metadata["extraction_quality"],
            "file_size_mb": pdf_metadata["file_size_mb"],
            "extracted_at": datetime.now().isoformat()
        }
        
        if pdf_metadata.get("extracted_date"):
            doc["extracted_metadata"]["extracted_date"] = pdf_metadata["extracted_date"]
        
        if pdf_metadata.get("num_articles_detected"):
            doc["extracted_metadata"]["num_articles_detected"] = pdf_metadata["num_articles_detected"]
        
        # Preview (apenas para inspeção, não vai para o Chroma)
        doc["preview"] = pdf_metadata["preview"]
        
        doc["extraction_status"] = "success"
        
        # Log
        print(f"    [OK] {pdf_metadata['num_pages']} paginas")
        print(f"    [OK] {pdf_metadata['char_count']:,} caracteres")
        print(f"    [OK] Qualidade: {pdf_metadata['extraction_quality']}")
        if pdf_metadata.get("num_articles_detected"):
            print(f"    [OK] ~{pdf_metadata['num_articles_detected']} artigos detectados")
        print(f"    Titulo: {pdf_metadata['extracted_title'][:80]}...")
        
        if pdf_metadata["extraction_quality"] == "baixa (possível OCR/imagem)":
            stats["low_quality"].append(doc_id)
        
        stats["processed"] += 1
    
    # Adicionar timestamp de atualização
    manifest["last_enrichment"] = datetime.now().isoformat()
    
    # Salvar manifest atualizado
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("[OK] Manifest enriquecido e salvo!")
    print("=" * 70)
    print(f"\nEstatisticas:")
    print(f"   Total de documentos: {stats['total_docs']}")
    print(f"   Processados com sucesso: {stats['processed']}")
    print(f"   Erros: {stats['errors']}")
    
    if stats['low_quality']:
        print(f"\n[!] Documentos com baixa qualidade de extracao:")
        for doc_id in stats['low_quality']:
            print(f"   - {doc_id}")
        print("   (Podem ser PDFs escaneados/imagens. Considere OCR.)")
    
    return stats


if __name__ == "__main__":
    stats = enrich_manifest()
    
    print("\n" + "=" * 70)
    print("Próximos passos:")
    print("  1. Revisar o corpus_manifest.json atualizado")
    print("  2. Se houver PDFs de baixa qualidade, considere OCR")
    print("  3. Executar ingestão no ChromaDB")
    print("=" * 70)
