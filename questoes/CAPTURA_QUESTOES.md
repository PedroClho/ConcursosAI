# 📥 Captura de Questões OAB - Hugging Face

## 📊 Dataset: `eduagarcia/oab_exams`

- **2.210 questões** da OAB 1ª Fase
- **Período**: 2010-2018
- **Fonte**: https://huggingface.co/datasets/eduagarcia/oab_exams

---

## 🚀 Passo a Passo

### **1. Baixar dataset**

```powershell
python questoes/scripts/download_questoes_hf.py
```

**O que faz:**
- ✅ Baixa automaticamente de `eduagarcia/oab_exams`
- ✅ Salva em `questoes/data/questoes_raw.json`
- ✅ Gera estatísticas (por ano, matéria, anuladas)
- ✅ Cria `metadata.json` com informações do dataset

**Saída esperada:**
```
📊 ESTATÍSTICAS:
   Total: 2210 questões
   Período: 2010-2018
   Anuladas: X

📅 Questões por ano:
   2010: XXX questões
   2011: XXX questões
   ...

📚 Questões por tipo:
   CONSTITUTIONAL: XXX
   CRIMINAL: XXX
   ...
```

---

### **2. Processar questões**

```powershell
python questoes/scripts/processar_questoes.py
```

**O que faz:**
- ✅ Normaliza estrutura para formato padrão
- ✅ Traduz tipos de questão (CONSTITUTIONAL → Direito Constitucional)
- ✅ Extrai alternativas e gabaritos
- ✅ Adiciona tags automáticas
- ✅ Verifica integridade dos dados
- ✅ Salva em `questoes/data/questoes_processadas.json`

---

### **3. Criar banco de dados** *(próximo passo)*

```powershell
python questoes/scripts/criar_banco_questoes.py
```

---

## 📋 Estrutura do Dataset Original

```json
{
  "id": "2010-01_1",
  "exam_id": "2010-01",
  "exam_year": "2010",
  "question_number": 1,
  "question": "Texto da questão...",
  "choices": {
    "text": ["Alternativa A", "Alternativa B", "Alternativa C", "Alternativa D"],
    "label": ["A", "B", "C", "D"]
  },
  "answerKey": "A",
  "question_type": "CONSTITUTIONAL",
  "nullified": false
}
```

---

## 📋 Estrutura Processada (Formato Padrão)

```json
{
  "id": "2010-01_1",
  "exame": "1º Exame OAB",
  "exam_id": "2010-01",
  "ano": 2010,
  "fase": 1,
  "numero_questao": 1,
  "materia": "Direito Constitucional",
  "materia_original": "CONSTITUTIONAL",
  "assunto": null,
  "enunciado": "Texto da questão...",
  "alternativas": [
    {"letra": "A", "texto": "Alternativa A"},
    {"letra": "B", "texto": "Alternativa B"},
    {"letra": "C", "texto": "Alternativa C"},
    {"letra": "D", "texto": "Alternativa D"}
  ],
  "gabarito": "A",
  "justificativa": null,
  "anulada": false,
  "dificuldade": "media",
  "tags": ["direito-constitucional", "ano-2010", "constitutional"],
  "artigos_relacionados": []
}
```

---

## 📚 Matérias Disponíveis

O dataset contém questões de:

- ✅ Ética Profissional (`ETHICS`)
- ✅ Direito Constitucional (`CONSTITUTIONAL`)
- ✅ Direito Penal (`CRIMINAL`)
- ✅ Direito Civil (`CIVIL`)
- ✅ Direito Administrativo (`ADMINISTRATIVE`)
- ✅ Direito Tributário (`TAX`)
- ✅ Direito do Trabalho (`LABOR`)
- ✅ Direito Processual Civil (`PROCEDURAL_CIVIL`)
- ✅ Direito Processual Penal (`PROCEDURAL_CRIMINAL`)
- ✅ Direito Empresarial (`BUSINESS`)
- ✅ Direito do Consumidor (`CONSUMER`)
- ✅ E outras...

---

## ❓ Problemas Comuns

### **Erro: "ModuleNotFoundError: No module named 'datasets'"**

**Solução:**
```powershell
pip install datasets
```

Ou:
```powershell
pip install -r requirements.txt
```

---

### **Erro de conexão**

**Solução:**
- Verifique sua conexão com internet
- Tente novamente (o download pode ser retomado)

---

## 📁 Arquivos Gerados

```
questoes/
├── data/
│   ├── questoes_raw.json              # Dados originais do HF
│   ├── questoes_processadas.json      # Dados normalizados
│   ├── metadata.json                  # Metadados do download
│   └── erros_processamento.json       # Log de erros (se houver)
└── scripts/
    ├── download_questoes_hf.py        # Script de download
    └── processar_questoes.py          # Script de processamento
```

---

## 🔄 Atualizar Dataset

Para baixar novamente (ex: nova versão do dataset):

```powershell
# Fazer backup
Move-Item questoes\data\questoes_raw.json questoes\data\questoes_raw_backup.json

# Baixar novamente
python questoes/scripts/download_questoes_hf.py

# Processar
python questoes/scripts/processar_questoes.py
```

---

## 📊 Estatísticas Esperadas

- **Total**: ~2.210 questões
- **Período**: 2010-2018
- **Questões anuladas**: ~10-20
- **Matéria mais comum**: Direito Constitucional
- **Todas possuem**: enunciado + 4 alternativas + gabarito

---

## ➡️ Próximos Passos

1. ✅ **Download** → `python questoes/scripts/download_questoes_hf.py`
2. ✅ **Processar** → `python questoes/scripts/processar_questoes.py`
3. ⏳ **Criar Banco** → `python questoes/scripts/criar_banco_questoes.py`
4. ⏳ **API** → Endpoints para buscar/filtrar questões
5. ⏳ **Frontend** → Página de simulado
6. ⏳ **Agente** → Ferramenta para explicar questões
