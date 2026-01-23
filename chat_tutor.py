"""
Interface de chat com o Agente Tutor OAB
"""

import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from agent.oab_agent import OABTutorAgent
from langchain_core.messages import HumanMessage, AIMessage

# Carregar .env
load_dotenv()


def main():
    """Interface de chat simples"""
    
    print("=" * 70)
    print("AGENTE TUTOR OAB - EXAME DE ORDEM")
    print("=" * 70)
    print("\nInicializando agente...")
    
    # Criar agente
    agent = OABTutorAgent(
        model="gpt-4o-mini",  # Modelo rápido e barato
        chroma_persist_directory="./chroma_db",
        collection_name="oab_corpus"
    )
    
    print("[OK] Agente inicializado!")
    print("\nVocê pode fazer perguntas sobre:")
    print("  - Leis: CF, CPC, CPP, CTN")
    print("  - Editais e informações da prova")
    print("  - Regras do Exame de Ordem")
    print("\nDigite 'sair' para encerrar\n")
    
    # Histórico de conversação
    conversation_history = []
    
    while True:
        print("-" * 70)
        user_input = input("\nVocê: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("\nEncerrando chat. Bons estudos! 📚")
            break
        
        # Obter resposta do agente
        try:
            print("\nTutor: ", end="", flush=True)
            response = agent.chat(user_input, conversation_history)
            print(response)
            
            # Atualizar histórico
            conversation_history.append(HumanMessage(content=user_input))
            conversation_history.append(AIMessage(content=response))
            
        except KeyboardInterrupt:
            print("\n\nInterrompido. Digite 'sair' para encerrar.")
            continue
        except Exception as e:
            print(f"\n[ERRO] {e}")
            print("Tente novamente.")


if __name__ == "__main__":
    main()
