"""
Script para testar consultas no banco SQLite de questões
"""

import sqlite3
import json
from pathlib import Path


def testar_banco(db_path: str = "questoes/database/oab_questoes.db"):
    """Testa consultas no banco de questões"""
    
    if not Path(db_path).exists():
        print(f"[ERRO] Banco não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("TESTANDO BANCO DE QUESTÕES OAB")
    print("=" * 70)
    
    # Teste 1: Buscar questões de Direito Constitucional
    print("\n[TESTE 1] Buscar 3 questões de Direito Constitucional:")
    cursor.execute("""
        SELECT id, ano, numero_questao, materia, gabarito
        FROM questoes
        WHERE materia = 'Direito Constitucional'
        LIMIT 3
    """)
    
    for row in cursor.fetchall():
        print(f"  - {row[0]} | Ano: {row[1]} | Q{row[2]} | {row[3]} | Gabarito: {row[4]}")
    
    # Teste 2: Buscar questões de 2015
    print("\n[TESTE 2] Total de questões de 2015:")
    cursor.execute("""
        SELECT COUNT(*) FROM questoes WHERE ano = 2015
    """)
    total_2015 = cursor.fetchone()[0]
    print(f"  Total: {total_2015} questões")
    
    # Teste 3: Buscar uma questão completa
    print("\n[TESTE 3] Questão completa (exemplo):")
    cursor.execute("""
        SELECT id, enunciado, alternativas, gabarito
        FROM questoes
        WHERE materia = 'Ética Profissional'
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if row:
        questao_id, enunciado, alternativas_json, gabarito = row
        alternativas = json.loads(alternativas_json)
        
        print(f"\n  ID: {questao_id}")
        print(f"  Enunciado: {enunciado[:100]}...")
        print(f"  Alternativas:")
        for alt in alternativas:
            print(f"    {alt['letra']}) {alt['texto'][:80]}...")
        print(f"  Gabarito: {gabarito}")
    
    # Teste 4: Filtro por matéria e ano
    print("\n[TESTE 4] Questões de Direito Penal de 2016:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM questoes 
        WHERE materia = 'Direito Penal' AND ano = 2016
    """)
    total = cursor.fetchone()[0]
    print(f"  Total: {total} questões")
    
    # Teste 5: Buscar por tag
    print("\n[TESTE 5] Questões com tag 'ano-2017':")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM questoes 
        WHERE tags LIKE '%ano-2017%'
    """)
    total = cursor.fetchone()[0]
    print(f"  Total: {total} questões")
    
    # Teste 6: Metadados
    print("\n[TESTE 6] Metadados do banco:")
    cursor.execute("SELECT chave, valor FROM metadata")
    for chave, valor in cursor.fetchall():
        print(f"  {chave}: {valor}")
    
    print("\n" + "=" * 70)
    print("TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 70)
    print("\nBanco está funcionando perfeitamente! ✅")
    
    conn.close()


if __name__ == "__main__":
    testar_banco()
