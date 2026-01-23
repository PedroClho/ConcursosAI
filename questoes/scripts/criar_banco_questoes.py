"""
Script para criar banco SQLite de questões OAB
Lê questoes_processadas.json e cria banco relacional otimizado
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def criar_schema(conn: sqlite3.Connection):
    """Cria schema do banco de dados"""
    cursor = conn.cursor()
    
    print("\n[1/5] Criando schema do banco...")
    
    # Criar tabela de questões
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questoes (
            id TEXT PRIMARY KEY,
            exam_id TEXT NOT NULL,
            exame TEXT NOT NULL,
            ano INTEGER NOT NULL,
            fase INTEGER NOT NULL,
            numero_questao INTEGER NOT NULL,
            materia TEXT NOT NULL,
            materia_original TEXT,
            assunto TEXT,
            enunciado TEXT NOT NULL,
            alternativas TEXT NOT NULL,  -- JSON serializado
            gabarito TEXT NOT NULL,
            justificativa TEXT,
            anulada BOOLEAN DEFAULT 0,
            dificuldade TEXT DEFAULT 'media',
            tags TEXT,  -- JSON serializado
            artigos_relacionados TEXT,  -- JSON serializado
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Criar índices para otimizar buscas
    print("      Criando índices...")
    
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_materia ON questoes(materia)",
        "CREATE INDEX IF NOT EXISTS idx_ano ON questoes(ano)",
        "CREATE INDEX IF NOT EXISTS idx_exam_id ON questoes(exam_id)",
        "CREATE INDEX IF NOT EXISTS idx_anulada ON questoes(anulada)",
        "CREATE INDEX IF NOT EXISTS idx_fase ON questoes(fase)",
        "CREATE INDEX IF NOT EXISTS idx_dificuldade ON questoes(dificuldade)",
        "CREATE INDEX IF NOT EXISTS idx_materia_ano ON questoes(materia, ano)"
    ]
    
    for idx_sql in indices:
        cursor.execute(idx_sql)
    
    # Criar tabela de metadados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("      [OK] Schema criado com sucesso!")


def inserir_questoes(conn: sqlite3.Connection, questoes: list) -> dict:
    """Insere questões no banco de dados"""
    cursor = conn.cursor()
    
    print(f"\n[2/5] Inserindo {len(questoes)} questões...")
    
    stats = {
        "total": len(questoes),
        "inseridas": 0,
        "erros": 0,
        "por_materia": {},
        "por_ano": {}
    }
    
    for i, questao in enumerate(questoes):
        try:
            # Serializar campos JSON
            alternativas_json = json.dumps(questao.get("alternativas", []), ensure_ascii=False)
            tags_json = json.dumps(questao.get("tags", []), ensure_ascii=False)
            artigos_json = json.dumps(questao.get("artigos_relacionados", []), ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO questoes (
                    id, exam_id, exame, ano, fase, numero_questao,
                    materia, materia_original, assunto, enunciado,
                    alternativas, gabarito, justificativa, anulada,
                    dificuldade, tags, artigos_relacionados
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                questao.get("id"),
                questao.get("exam_id"),
                questao.get("exame"),
                questao.get("ano"),
                questao.get("fase"),
                questao.get("numero_questao"),
                questao.get("materia"),
                questao.get("materia_original"),
                questao.get("assunto"),
                questao.get("enunciado"),
                alternativas_json,
                questao.get("gabarito"),
                questao.get("justificativa"),
                1 if questao.get("anulada") else 0,
                questao.get("dificuldade", "media"),
                tags_json,
                artigos_json
            ))
            
            stats["inseridas"] += 1
            
            # Estatísticas
            materia = questao.get("materia", "Desconhecida")
            ano = questao.get("ano", 0)
            stats["por_materia"][materia] = stats["por_materia"].get(materia, 0) + 1
            stats["por_ano"][ano] = stats["por_ano"].get(ano, 0) + 1
            
            if (i + 1) % 500 == 0:
                print(f"      Inseridas: {i + 1}/{len(questoes)}")
                conn.commit()  # Commit parcial
        
        except Exception as e:
            stats["erros"] += 1
            print(f"      [ERRO] Questão {questao.get('id')}: {e}")
    
    conn.commit()
    print(f"      [OK] {stats['inseridas']} questões inseridas!")
    if stats["erros"] > 0:
        print(f"      [!] {stats['erros']} erros")
    
    return stats


def inserir_metadata(conn: sqlite3.Connection, stats: dict):
    """Insere metadados no banco"""
    cursor = conn.cursor()
    
    print("\n[3/5] Salvando metadados...")
    
    metadata = {
        "total_questoes": str(stats["total"]),
        "questoes_inseridas": str(stats["inseridas"]),
        "dataset_source": "eduagarcia/oab_exams",
        "periodo": "2010-2018",
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    for chave, valor in metadata.items():
        cursor.execute("""
            INSERT OR REPLACE INTO metadata (chave, valor, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (chave, valor))
    
    conn.commit()
    print("      [OK] Metadados salvos!")


def validar_banco(conn: sqlite3.Connection) -> bool:
    """Valida integridade do banco criado"""
    cursor = conn.cursor()
    
    print("\n[4/5] Validando banco de dados...")
    
    validacoes = []
    
    # Validação 1: Total de questões
    cursor.execute("SELECT COUNT(*) FROM questoes")
    total = cursor.fetchone()[0]
    validacoes.append(("Total de questões", total, total == 2210))
    print(f"      Total de questões: {total}")
    
    # Validação 2: Questões sem gabarito
    cursor.execute("SELECT COUNT(*) FROM questoes WHERE gabarito IS NULL OR gabarito = ''")
    sem_gabarito = cursor.fetchone()[0]
    validacoes.append(("Sem gabarito", sem_gabarito, sem_gabarito == 0))
    print(f"      Sem gabarito: {sem_gabarito}")
    
    # Validação 3: Questões sem enunciado
    cursor.execute("SELECT COUNT(*) FROM questoes WHERE enunciado IS NULL OR enunciado = ''")
    sem_enunciado = cursor.fetchone()[0]
    validacoes.append(("Sem enunciado", sem_enunciado, sem_enunciado == 0))
    print(f"      Sem enunciado: {sem_enunciado}")
    
    # Validação 4: Questões sem alternativas
    cursor.execute("SELECT COUNT(*) FROM questoes WHERE alternativas IS NULL OR alternativas = '[]'")
    sem_alternativas = cursor.fetchone()[0]
    validacoes.append(("Sem alternativas", sem_alternativas, sem_alternativas == 0))
    print(f"      Sem alternativas: {sem_alternativas}")
    
    # Validação 5: Índices criados
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
    total_indices = cursor.fetchone()[0]
    validacoes.append(("Índices criados", total_indices, total_indices >= 7))
    print(f"      Índices criados: {total_indices}")
    
    # Resultado
    todas_ok = all(v[2] for v in validacoes)
    
    if todas_ok:
        print("      [OK] Banco validado com sucesso!")
    else:
        print("      [!] Algumas validações falharam:")
        for nome, valor, ok in validacoes:
            if not ok:
                print(f"          - {nome}: {valor}")
    
    return todas_ok


def gerar_estatisticas(conn: sqlite3.Connection):
    """Gera e exibe estatísticas do banco"""
    cursor = conn.cursor()
    
    print("\n[5/5] Gerando estatísticas...")
    
    print("\n" + "=" * 70)
    print("ESTATÍSTICAS DO BANCO")
    print("=" * 70)
    
    # Total
    cursor.execute("SELECT COUNT(*) FROM questoes")
    total = cursor.fetchone()[0]
    print(f"\nTotal de questões: {total}")
    
    # Por matéria
    print("\nTop 10 matérias:")
    cursor.execute("""
        SELECT materia, COUNT(*) as total
        FROM questoes
        GROUP BY materia
        ORDER BY total DESC
        LIMIT 10
    """)
    for materia, count in cursor.fetchall():
        print(f"  {materia}: {count}")
    
    # Por ano
    print("\nQuestões por ano:")
    cursor.execute("""
        SELECT ano, COUNT(*) as total
        FROM questoes
        GROUP BY ano
        ORDER BY ano
    """)
    for ano, count in cursor.fetchall():
        print(f"  {ano}: {count}")
    
    # Anuladas
    cursor.execute("SELECT COUNT(*) FROM questoes WHERE anulada = 1")
    anuladas = cursor.fetchone()[0]
    print(f"\nQuestões anuladas: {anuladas}")
    
    # Tamanho do banco
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    size_bytes = cursor.fetchone()[0]
    size_mb = size_bytes / (1024 * 1024)
    print(f"\nTamanho do banco: {size_mb:.2f} MB")


def criar_banco_questoes(
    input_file: str = "questoes/data/questoes_processadas.json",
    output_db: str = "questoes/database/oab_questoes.db"
):
    """
    Função principal para criar banco SQLite de questões
    """
    print("=" * 70)
    print("CRIAÇÃO DE BANCO SQLITE - QUESTÕES OAB")
    print("=" * 70)
    
    # Verificar se arquivo de entrada existe
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"\n[ERRO] Arquivo não encontrado: {input_file}")
        print("Execute primeiro: python questoes/scripts/processar_questoes.py")
        return False
    
    # Criar diretório do banco se não existir
    output_path = Path(output_db)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Verificar se banco já existe
    if output_path.exists():
        print(f"\n[!] Banco já existe: {output_db}")
        resposta = input("Deseja sobrescrever? (s/N): ").lower()
        if resposta != 's':
            print("Operação cancelada.")
            return False
        output_path.unlink()
        print("    Banco anterior removido.")
    
    # Carregar questões
    print(f"\nCarregando questões de: {input_file}")
    with open(input_path, 'r', encoding='utf-8') as f:
        questoes = json.load(f)
    print(f"Total de questões: {len(questoes)}")
    
    # Conectar ao banco
    print(f"\nCriando banco: {output_db}")
    conn = sqlite3.connect(output_db)
    
    try:
        # Criar schema
        criar_schema(conn)
        
        # Inserir questões
        stats = inserir_questoes(conn, questoes)
        
        # Inserir metadata
        inserir_metadata(conn, stats)
        
        # Validar banco
        validado = validar_banco(conn)
        
        # Gerar estatísticas
        gerar_estatisticas(conn)
        
        print("\n" + "=" * 70)
        print("BANCO CRIADO COM SUCESSO!")
        print("=" * 70)
        print(f"\nArquivo: {output_db}")
        print(f"Tamanho: ~{output_path.stat().st_size / (1024*1024):.2f} MB")
        print(f"\nPróximo passo:")
        print(f"  - Adicionar endpoints no backend (backend/main.py)")
        print(f"  - Criar ferramenta do agente para buscar questões")
        
        return True
    
    except Exception as e:
        print(f"\n[ERRO] Falha ao criar banco: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        sucesso = criar_banco_questoes()
        exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n[!] Operação cancelada pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
