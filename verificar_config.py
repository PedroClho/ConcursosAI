"""
Script para verificar se a configuração está correta
"""

import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("VERIFICAÇÃO DE CONFIGURAÇÃO - CASTRO")
print("=" * 70)

# 1. Verificar se .env existe
env_path = Path(".env")
if env_path.exists():
    print(f"\n[OK] Arquivo .env encontrado em: {env_path.absolute()}")
else:
    print(f"\n[ERRO] Arquivo .env NÃO encontrado!")
    print(f"       Esperado em: {env_path.absolute()}")
    print("\nCrie o arquivo .env com:")
    print("OPENAI_API_KEY=sk-proj-sua-chave-aqui")
    exit(1)

# 2. Carregar .env
load_dotenv()

# 3. Verificar OPENAI_API_KEY
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"[OK] OPENAI_API_KEY carregada")
    print(f"     Começa com: {api_key[:15]}...")
    print(f"     Tamanho: {len(api_key)} caracteres")
    
    # Verificar se não tem aspas
    if api_key.startswith('"') or api_key.startswith("'"):
        print("\n[AVISO] A chave tem aspas! Remova as aspas do .env")
        print("        Deve ser: OPENAI_API_KEY=sk-proj-...")
        print("        NÃO: OPENAI_API_KEY=\"sk-proj-...\"")
else:
    print(f"[ERRO] OPENAI_API_KEY não foi carregada!")
    print("\nVerifique se o .env tem:")
    print("OPENAI_API_KEY=sk-proj-sua-chave-aqui")
    print("\n(SEM aspas!)")
    exit(1)

# 4. Verificar ChromaDB
chroma_path = Path("chroma_db")
if chroma_path.exists():
    print(f"[OK] ChromaDB encontrado em: {chroma_path.absolute()}")
else:
    print(f"[AVISO] ChromaDB não encontrado!")
    print(f"        Execute: python scripts/ingest_corpus.py")

# 5. Verificar Node.js (para frontend)
import subprocess
try:
    node_version = subprocess.run(
        ["node", "--version"], 
        capture_output=True, 
        text=True,
        timeout=5
    )
    if node_version.returncode == 0:
        print(f"[OK] Node.js instalado: {node_version.stdout.strip()}")
    else:
        print(f"[AVISO] Node.js não encontrado (necessário para frontend)")
except:
    print(f"[AVISO] Node.js não encontrado (necessário para frontend)")

print("\n" + "=" * 70)
print("VERIFICAÇÃO COMPLETA!")
print("=" * 70)
print("\nPróximo passo: python backend/main.py")
