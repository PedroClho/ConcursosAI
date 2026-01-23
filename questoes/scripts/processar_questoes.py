"""
Script para processar questões do dataset eduagarcia/oab_exams
e estruturá-las no formato padronizado para o banco de dados
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# Mapeamento de tipos de questão (inglês → português)
QUESTION_TYPE_MAP = {
    "ETHICS": "Ética Profissional",
    "CONSTITUTIONAL": "Direito Constitucional",
    "CRIMINAL": "Direito Penal",
    "CIVIL": "Direito Civil",
    "ADMINISTRATIVE": "Direito Administrativo",
    "TAX": "Direito Tributário",
    "TAXES": "Direito Tributário",
    "LABOR": "Direito do Trabalho",
    "LABOUR": "Direito do Trabalho",
    "PROCEDURAL_CIVIL": "Direito Processual Civil",
    "CIVIL-PROCEDURE": "Direito Processual Civil",
    "PROCEDURAL_CRIMINAL": "Direito Processual Penal",
    "CRIMINAL-PROCEDURE": "Direito Processual Penal",
    "LABOUR-PROCEDURE": "Direito Processual do Trabalho",
    "BUSINESS": "Direito Empresarial",
    "CONSUMER": "Direito do Consumidor",
    "ENVIRONMENTAL": "Direito Ambiental",
    "INTERNATIONAL": "Direito Internacional",
    "CHILD": "Direito da Criança e do Adolescente",
    "CHILDREN": "Direito da Criança e do Adolescente",
    "ELDERLY": "Direito do Idoso",
    "HUMAN_RIGHTS": "Direitos Humanos",
    "HUMAN-RIGHTS": "Direitos Humanos",
    "PHILOSOPHY": "Filosofia do Direito",
    "PHILOSHOPY": "Filosofia do Direito",
    "GENERAL": "Direito Geral"
}


def normalize_questao(raw_questao: dict) -> dict:
    """
    Normaliza uma questão do dataset eduagarcia/oab_exams
    
    Estrutura original:
    - id: "2010-01_1"
    - exam_id: "2010-01"
    - exam_year: "2010"
    - question_number: 1
    - question: "Texto..."
    - choices: {"text": [...], "label": ["A", "B", "C", "D"]}
    - answerKey: "A"
    - question_type: "ETHICS"
    - nullified: false
    """
    
    # Extrair alternativas
    alternativas = []
    if "choices" in raw_questao and raw_questao["choices"]:
        labels = raw_questao["choices"].get("label", [])
        texts = raw_questao["choices"].get("text", [])
        
        for label, text in zip(labels, texts):
            alternativas.append({
                "letra": label.upper(),
                "texto": text
            })
    
    # Mapear tipo de questão
    question_type_raw = raw_questao.get("question_type") or "GENERAL"
    materia = QUESTION_TYPE_MAP.get(question_type_raw, question_type_raw)
    
    # Extrair exame (número do exame)
    exam_id = raw_questao.get("exam_id", "")
    parts = exam_id.split("-")
    exame_numero = None
    if len(parts) == 2:
        ano, sessao = parts
        # Calcular número do exame aproximado (OAB tem ~3 exames por ano desde 2010)
        try:
            exame_base = (int(ano) - 2010) * 3
            sessao_num = int(sessao)
            exame_numero = exame_base + sessao_num
        except:
            pass
    
    # Estrutura padronizada
    questao_normalizada = {
        "id": raw_questao.get("id"),
        "exame": f"{exame_numero}º Exame OAB" if exame_numero else f"OAB {exam_id}",
        "exam_id": exam_id,
        "ano": int(raw_questao.get("exam_year", 0)),
        "fase": 1,  # Dataset é só 1ª fase
        "numero_questao": raw_questao.get("question_number", 0),
        "materia": materia,
        "materia_original": question_type_raw,
        "assunto": None,  # Não disponível no dataset
        "enunciado": raw_questao.get("question", ""),
        "alternativas": alternativas,
        "gabarito": raw_questao.get("answerKey", "").upper(),
        "justificativa": None,  # Não disponível no dataset
        "anulada": raw_questao.get("nullified", False),
        "dificuldade": "media",
        "tags": [
            materia.lower().replace(" ", "-"),
            f"ano-{raw_questao.get('exam_year')}",
            question_type_raw.lower()
        ],
        "artigos_relacionados": []
    }
    
    # Adicionar tag se foi anulada
    if questao_normalizada["anulada"]:
        questao_normalizada["tags"].append("anulada")
    
    return questao_normalizada


def processar_questoes(
    input_file: str = "questoes/data/questoes_raw.json",
    output_file: str = "questoes/data/questoes_processadas.json"
):
    """
    Processa arquivo de questões brutas e gera arquivo estruturado
    """
    print("=" * 70)
    print("PROCESSAMENTO DE QUESTÕES OAB")
    print("Dataset: eduagarcia/oab_exams")
    print("=" * 70)
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"\n[ERRO] Arquivo não encontrado: {input_file}")
        print("Execute primeiro: python questoes/scripts/download_questoes_hf.py")
        exit(1)
    
    print(f"\n[1/3] Carregando questões de: {input_file}")
    with open(input_path, 'r', encoding='utf-8') as f:
        questoes_raw = json.load(f)
    
    print(f"      Total de questões: {len(questoes_raw)}")
    
    print(f"\n[2/3] Processando e normalizando questões...")
    questoes_processadas = []
    erros = []
    
    for i, questao_raw in enumerate(questoes_raw):
        try:
            questao_norm = normalize_questao(questao_raw)
            questoes_processadas.append(questao_norm)
            
            if (i + 1) % 500 == 0:
                print(f"      Processadas: {i + 1}/{len(questoes_raw)}")
        
        except Exception as e:
            erros.append({"index": i, "error": str(e), "data": questao_raw})
            print(f"      [!] Erro na questão {i}: {e}")
    
    print(f"      [OK] {len(questoes_processadas)} questões processadas")
    if erros:
        print(f"      [!] {len(erros)} questões com erro")
    
    print(f"\n[3/3] Salvando questões processadas...")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questoes_processadas, f, indent=2, ensure_ascii=False)
    
    print(f"      [OK] Salvo em: {output_file}")
    
    # Salvar log de erros se houver
    if erros:
        erros_file = output_path.parent / "erros_processamento.json"
        with open(erros_file, 'w', encoding='utf-8') as f:
            json.dump(erros, f, indent=2, ensure_ascii=False)
        print(f"      [!] Log de erros: {erros_file}")
    
    # Estatísticas detalhadas
    print("\n" + "=" * 70)
    print("ESTATÍSTICAS")
    print("=" * 70)
    
    # Contar por matéria
    materias = defaultdict(int)
    anos = defaultdict(int)
    anuladas = 0
    
    for q in questoes_processadas:
        materias[q["materia"]] += 1
        anos[q["ano"]] += 1
        if q["anulada"]:
            anuladas += 1
    
    print(f"\nQuestões por matéria:")
    for materia, count in sorted(materias.items(), key=lambda x: x[1], reverse=True):
        print(f"   {materia}: {count}")
    
    print(f"\nQuestões por ano:")
    for ano, count in sorted(anos.items()):
        print(f"   {ano}: {count}")
    
    print(f"\nQuestões anuladas: {anuladas}")
    
    # Verificar integridade
    print(f"\nVerificação de integridade:")
    sem_alternativas = sum(1 for q in questoes_processadas if not q["alternativas"])
    sem_gabarito = sum(1 for q in questoes_processadas if not q["gabarito"])
    
    print(f"   Sem alternativas: {sem_alternativas}")
    print(f"   Sem gabarito: {sem_gabarito}")
    
    if sem_alternativas == 0 and sem_gabarito == 0:
        print(f"   [OK] Todas as questões estão completas!")
    
    print("\n" + "=" * 70)
    print("PROCESSAMENTO CONCLUÍDO!")
    print("=" * 70)
    print(f"\nPróximo passo:")
    print(f"   python questoes/scripts/criar_banco_questoes.py")


if __name__ == "__main__":
    try:
        processar_questoes()
    except KeyboardInterrupt:
        print("\n\n[!] Processamento interrompido")
        exit(1)
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
