"""
Ferramentas (Tools) para o Agente Tutor OAB
"""

import sys
import os
# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Literal
from langchain_core.tools import tool, StructuredTool
from rag.law_processor import LawProcessor
import sqlite3
import json
from pathlib import Path


class SearchTools:
    """Classe com ferramentas de busca para o agente"""
    
    def __init__(self, chroma_persist_directory: str = "./chroma_db", collection_name: str = "oab_corpus"):
        """Inicializa as ferramentas com conexão ao ChromaDB"""
        self.processor = LawProcessor(
            chroma_persist_directory=chroma_persist_directory,
            collection_name=collection_name
        )
        
        # Path para banco de questões
        self.db_path = Path(__file__).parent.parent / "questoes" / "database" / "oab_questoes.db"
    
    def search_laws(self, query: str, law_filter: Optional[str] = None, top_k: int = 3) -> str:
        """
        Busca artigos de leis (CF, CPC, CPP, CTN) relevantes para uma consulta.
        
        Args:
            query: Pergunta ou tema a buscar
            law_filter: Filtrar por lei específica: "CF", "CPC", "CPP", ou "CTN" (opcional)
            top_k: Número de resultados (padrão: 3)
        
        Returns:
            Texto formatado com artigos encontrados e suas referências
        """
        # Montar filtros com sintaxe correta do ChromaDB
        if law_filter:
            filters = {
                "$and": [
                    {"kind": "lei"},
                    {"sigla": law_filter.upper()}
                ]
            }
        else:
            filters = {"kind": "lei"}
        
        results = self.processor.search(query, top_k=top_k, filter_metadata=filters)
        
        if not results:
            return f"Nenhum artigo encontrado para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            law_name = meta.get('law_name', 'N/A')
            article_ref = meta.get('full_reference', 'N/A')
            relevance = result['relevance_score']
            text = result['document'][:500]  # Limitar tamanho
            
            output.append(
                f"[{i}] {law_name} - {article_ref} (Relevância: {relevance:.1%})\n"
                f"{text}...\n"
            )
        
        return "\n".join(output)
    
    def search_edital(self, query: str, top_k: int = 2) -> str:
        """
        Busca informações nos editais do Exame de Ordem (datas, locais, horários, regras).
        
        Args:
            query: Pergunta sobre o edital (ex: "data da prova", "local de prova")
            top_k: Número de resultados (padrão: 2)
        
        Returns:
            Texto com informações do edital
        """
        filters = {"kind": "edital"}
        results = self.processor.search(query, top_k=top_k, filter_metadata=filters)
        
        if not results:
            return f"Nenhuma informação encontrada no edital para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            doc_name = meta.get('document_name', 'Edital')
            relevance = result['relevance_score']
            text = result['document'][:400]
            
            output.append(
                f"[{i}] {doc_name} (Relevância: {relevance:.1%})\n"
                f"{text}...\n"
            )
        
        return "\n".join(output)
    
    def search_provimento(self, query: str, top_k: int = 2) -> str:
        """
        Busca regras do Provimento CFOAB (inscrição, recursos, aprovação no Exame de Ordem).
        
        Args:
            query: Pergunta sobre as regras do exame
            top_k: Número de resultados (padrão: 2)
        
        Returns:
            Texto com regras do provimento
        """
        filters = {"kind": "normativo"}
        results = self.processor.search(query, top_k=top_k, filter_metadata=filters)
        
        if not results:
            return f"Nenhuma informação encontrada no provimento para: {query}"
        
        output = []
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            doc_name = meta.get('document_name', 'Provimento CFOAB')
            relevance = result['relevance_score']
            text = result['document'][:400]
            
            output.append(
                f"[{i}] {doc_name} (Relevância: {relevance:.1%})\n"
                f"{text}...\n"
            )
        
        return "\n".join(output)
    
    def get_database_stats(self) -> str:
        """
        Retorna estatísticas da base de dados (quantas leis, artigos, documentos estão indexados).
        
        Returns:
            Texto com estatísticas
        """
        stats = self.processor.get_collection_stats()
        
        return (
            f"Base de Dados OAB:\n"
            f"- Total de itens: {stats['total_articles']}\n"
            f"- Leis indexadas: {stats['laws_count']}\n"
            f"- Leis disponíveis: {', '.join(stats['laws']) if stats['laws'] else 'Nenhuma'}\n"
        )
    
    def buscar_questoes(self, materia: str, quantidade: int = 5) -> str:
        """
        Busca questões da OAB de uma matéria específica para o aluno praticar.
        
        Args:
            materia: Nome da matéria (ex: "Direito Constitucional", "Direito Penal")
            quantidade: Quantidade de questões a retornar (padrão: 5, máximo: 10)
        
        Returns:
            Texto formatado com as questões encontradas (enunciado + alternativas + ID)
        """
        if not self.db_path.exists():
            return "⚠️ Banco de questões não disponível."
        
        quantidade = min(quantidade, 10)  # Limitar a 10
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, ano, numero_questao, enunciado, alternativas, exam_id
                FROM questoes
                WHERE materia = ? AND anulada = 0
                ORDER BY RANDOM()
                LIMIT ?
            """, (materia, quantidade))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return f"Não foram encontradas questões de {materia}. Verifique o nome da matéria."
            
            response = f"📝 QUESTÕES DE {materia.upper()}\n"
            response += f"Total encontradas: {len(rows)}\n\n"
            
            for i, row in enumerate(rows, 1):
                questao_id, ano, num_q, enunciado, alternativas_json, exam_id = row
                alternativas = json.loads(alternativas_json)
                
                response += f"{'='*60}\n"
                response += f"QUESTÃO {i} (ID: {questao_id})\n"
                response += f"Ano: {ano} | Exame: {exam_id} | Nº: {num_q}\n"
                response += f"{'='*60}\n\n"
                response += f"{enunciado}\n\n"
                
                for alt in alternativas:
                    response += f"{alt['letra']}) {alt['texto']}\n"
                
                response += f"\n💡 Para ver o gabarito e explicação, use explicar_questao\n\n"
            
            return response
        
        except Exception as e:
            return f"⚠️ Erro ao buscar questões: {str(e)}"
    
    def explicar_questao(self, questao_id: str) -> str:
        """
        Explica uma questão específica da OAB, mostrando gabarito e buscando artigos relacionados.
        
        Args:
            questao_id: ID da questão (ex: "2015-01_5")
        
        Returns:
            Texto com gabarito, justificativa e artigos relacionados do RAG
        """
        if not self.db_path.exists():
            return "⚠️ Banco de questões não disponível."
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, ano, materia, enunciado, alternativas, gabarito, 
                       justificativa, exam_id, numero_questao
                FROM questoes
                WHERE id = ?
            """, (questao_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return f"⚠️ Questão {questao_id} não encontrada."
            
            (qid, ano, materia, enunciado, alternativas_json, gabarito, 
             justificativa, exam_id, num_q) = row
            
            alternativas = json.loads(alternativas_json)
            
            # Montar resposta com Markdown rico
            response = f"# 📚 Explicação da Questão\n\n"
            response += f"**Questão:** {qid} | **Ano:** {ano} | **Exame:** {exam_id} | **Nº:** {num_q}  \n"
            response += f"**Matéria:** {materia}\n\n"
            response += "---\n\n"
            
            response += f"## 📋 Enunciado\n\n"
            response += f"{enunciado}\n\n"
            
            response += f"## 📝 Alternativas\n\n"
            for alt in alternativas:
                if alt['letra'] == gabarito:
                    # Alternativa correta em destaque
                    response += f"- **✅ {alt['letra']})** **{alt['texto']}** ← *Resposta Correta*\n"
                else:
                    # Alternativas incorretas
                    response += f"- ❌ **{alt['letra']})** {alt['texto']}\n"
            
            response += f"\n---\n\n"
            response += f"## 🎯 Gabarito Oficial\n\n"
            response += f"> **Alternativa correta: {gabarito}**\n\n"
            
            if justificativa:
                response += f"### 💡 Justificativa\n\n"
                response += f"{justificativa}\n\n"
            
            # Buscar artigos relacionados no RAG
            response += "---\n\n"
            response += "## 📖 Base Legal e Artigos Relacionados\n\n"
            
            # Buscar artigos relacionados ao tema
            search_query = f"{materia}: {enunciado[:200]}"
            rag_results = self.processor.search(search_query, top_k=2, filter_metadata={"kind": "lei"})
            
            if rag_results:
                for i, result in enumerate(rag_results, 1):
                    lei = result['metadata'].get('sigla', 'Lei')
                    lei_nome = result['metadata'].get('law_name', '')
                    artigo = result['metadata'].get('article_number', '?')
                    texto = result['document'][:400]
                    relevancia = result['relevance_score']
                    
                    response += f"### 📜 {lei} - Artigo {artigo}\n"
                    if lei_nome:
                        response += f"*{lei_nome}*\n\n"
                    response += f"> {texto}...\n\n"
                    response += f"*Relevância: {relevancia:.0%}*\n\n"
            else:
                response += "> *Nenhum artigo específico foi encontrado na base de dados para esta questão.*\n\n"
            
            response += "---\n\n"
            response += "### 💭 Dica de Estudo\n\n"
            response += "Revise os artigos mencionados acima e tente entender o raciocínio por trás da resposta correta. "
            response += "Pratique questões similares para fixar o conteúdo!\n"
            
            return response
        
        except Exception as e:
            return f"⚠️ Erro ao explicar questão: {str(e)}"
    
    def get_all_tools(self):
        """Retorna lista de todas as ferramentas disponíveis para o agente"""
        # Criar StructuredTools vinculadas à instância
        return [
            StructuredTool.from_function(
                func=self.search_laws,
                name="search_laws",
                description="""Busca artigos de leis (CF, CPC, CPP, CTN) relevantes para uma consulta.
                
Args:
    query: Pergunta ou tema a buscar
    law_filter: Filtrar por lei específica: "CF", "CPC", "CPP", ou "CTN" (opcional)
    top_k: Número de resultados (padrão: 3)

Returns:
    Texto formatado com artigos encontrados e suas referências"""
            ),
            StructuredTool.from_function(
                func=self.search_edital,
                name="search_edital",
                description="""Busca informações nos editais do Exame de Ordem (datas, locais, horários, regras).

Args:
    query: Pergunta sobre o edital (ex: "data da prova", "local de prova")
    top_k: Número de resultados (padrão: 2)

Returns:
    Texto com informações do edital"""
            ),
            StructuredTool.from_function(
                func=self.search_provimento,
                name="search_provimento",
                description="""Busca regras do Provimento CFOAB (inscrição, recursos, aprovação no Exame de Ordem).

Args:
    query: Pergunta sobre as regras do exame
    top_k: Número de resultados (padrão: 2)

Returns:
    Texto com regras do provimento"""
            ),
            StructuredTool.from_function(
                func=self.get_database_stats,
                name="get_database_stats",
                description="""Retorna estatísticas da base de dados (quantas leis, artigos, documentos estão indexados).

Returns:
    Texto com estatísticas"""
            ),
            StructuredTool.from_function(
                func=self.buscar_questoes,
                name="buscar_questoes",
                description="""Busca questões da OAB de uma matéria específica para o aluno praticar.
                
Args:
    materia: Nome da matéria (ex: "Direito Constitucional", "Direito Penal", "Ética Profissional")
    quantidade: Quantidade de questões (padrão: 5, máximo: 10)

Returns:
    Questões formatadas com enunciado, alternativas e IDs para explicação posterior"""
            ),
            StructuredTool.from_function(
                func=self.explicar_questao,
                name="explicar_questao",
                description="""Explica uma questão específica da OAB, mostrando gabarito e buscando artigos relacionados no RAG.
                
Args:
    questao_id: ID da questão (ex: "2015-01_5")

Returns:
    Explicação completa com gabarito, justificativa e artigos de lei relacionados"""
            ),
        ]
