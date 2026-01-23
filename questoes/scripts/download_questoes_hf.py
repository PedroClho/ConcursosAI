"""
Script para baixar dataset de questões OAB do Hugging Face
Dataset: eduagarcia/oab_exams (2.210 questões de 2010-2018)
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Verificar se datasets está instalado
try:
    from datasets import load_dataset
except ImportError:
    print("[ERRO] Biblioteca 'datasets' não encontrada!")
    print("\nInstale com: pip install datasets")
    exit(1)


def download_oab_exams(output_dir: str = "questoes/data"):
    """
    Baixa dataset eduagarcia/oab_exams do Hugging Face
    
    Estrutura do dataset:
    - id: "2010-01_1" (ano-mes_numero)
    - exam_id: "2010-01"
    - exam_year: "2010"
    - question_number: 1
    - question: "Texto da questão"
    - choices: {"text": [...], "label": ["A", "B", "C", "D"]}
    - answerKey: "A"
    - question_type: "ETHICS", "CONSTITUTIONAL", etc.
    - nullified: true/false
    
    Args:
        output_dir: Diretório de saída
    """
    print("=" * 70)
    print("DOWNLOAD DE QUESTÕES OAB - HUGGING FACE")
    print("Dataset: eduagarcia/oab_exams")
    print("=" * 70)
    
    # Criar diretório se não existir
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[1/4] Baixando dataset eduagarcia/oab_exams...")
    try:
        dataset = load_dataset("eduagarcia/oab_exams")
        print(f"      [OK] Dataset carregado!")
    except Exception as e:
        print(f"      [ERRO] Falha ao carregar dataset: {e}")
        print("\nVerifique sua conexão com internet")
        exit(1)
    
    # Verificar splits disponíveis
    print(f"\n[2/4] Splits disponíveis: {list(dataset.keys())}")
    
    # Usar o split 'train' (único disponível)
    df = dataset['train']
    
    print(f"\n      Total de questões: {len(df)}")
    print(f"      Colunas: {df.column_names}")
    
    # Mostrar exemplo
    print(f"\n[3/4] Exemplo de questão:")
    exemplo = df[0]
    print(f"\n      ID: {exemplo['id']}")
    print(f"      Ano: {exemplo['exam_year']}")
    print(f"      Tipo: {exemplo['question_type']}")
    print(f"      Questão: {exemplo['question'][:100]}...")
    print(f"      Alternativas: {len(exemplo['choices']['text'])} opções")
    print(f"      Gabarito: {exemplo['answerKey']}")
    print(f"      Anulada: {exemplo['nullified']}")
    
    # Salvar como JSON
    output_file = output_path / "questoes_raw.json"
    print(f"\n[4/4] Salvando em: {output_file}")
    
    # Converter para lista de dicts
    questoes = []
    for i, item in enumerate(df):
        questoes.append(dict(item))
        
        if (i + 1) % 500 == 0:
            print(f"      Processando: {i + 1}/{len(df)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(questoes, f, indent=2, ensure_ascii=False)
    
    print(f"      [OK] {len(questoes)} questões salvas!")
    
    # Gerar estatísticas
    stats = {
        "total_questoes": len(questoes),
        "anos": {},
        "tipos": {},
        "anuladas": 0
    }
    
    for q in questoes:
        # Por ano
        ano = q['exam_year']
        stats['anos'][ano] = stats['anos'].get(ano, 0) + 1
        
        # Por tipo
        tipo = q['question_type']
        stats['tipos'][tipo] = stats['tipos'].get(tipo, 0) + 1
        
        # Anuladas
        if q['nullified']:
            stats['anuladas'] += 1
    
    # Salvar metadados
    metadata = {
        "dataset_name": "eduagarcia/oab_exams",
        "dataset_url": "https://huggingface.co/datasets/eduagarcia/oab_exams",
        "download_date": datetime.now().isoformat(),
        "total_questoes": len(questoes),
        "periodo": "2010-2018",
        "estatisticas": stats,
        "columns": df.column_names,
        "output_file": str(output_file)
    }
    
    metadata_file = output_path / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("DOWNLOAD CONCLUÍDO!")
    print("=" * 70)
    
    print(f"\nESTATÍSTICAS:")
    print(f"   Total: {stats['total_questoes']} questões")
    print(f"   Período: 2010-2018")
    print(f"   Anuladas: {stats['anuladas']}")
    
    print(f"\nQuestões por ano:")
    for ano in sorted(stats['anos'].keys()):
        print(f"   {ano}: {stats['anos'][ano]} questões")
    
    print(f"\nQuestões por tipo:")
    for tipo, count in sorted(stats['tipos'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {tipo}: {count} questões")
    
    print(f"\nArquivos gerados:")
    print(f"   - {output_file}")
    print(f"   - {metadata_file}")
    
    print(f"\nPróximo passo:")
    print(f"   python questoes/scripts/processar_questoes.py")
    
    return questoes, metadata


if __name__ == "__main__":
    try:
        questoes, metadata = download_oab_exams()
    except KeyboardInterrupt:
        print("\n\n[!] Download interrompido pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
