# 💾 Módulo de Questões OAB

## 📊 Sobre

Este módulo gerencia o banco de questões da OAB, incluindo:
- Download de datasets externos (Hugging Face)
- Processamento e normalização de dados
- Criação e gerenciamento de banco SQLite
- API de acesso às questões

---

## 📁 Estrutura

```
questoes/
├── data/                           # Dados brutos e processados
│   ├── questoes_raw.json           # Dataset original (2.210 questões)
│   ├── questoes_processadas.json   # Dados normalizados
│   ├── metadata.json               # Metadados do download
│   └── erros_processamento.json    # Log de erros (se houver)
│
├── database/                       # Banco de dados SQLite
│   └── oab_questoes.db             # Banco principal (será criado)
│
├── scripts/                        # Scripts de processamento
│   ├── download_questoes_hf.py     # Download do Hugging Face
│   ├── processar_questoes.py       # Normalização de dados
│   └── criar_banco_questoes.py     # Criação do banco SQLite (próximo)
│
├── CAPTURA_QUESTOES.md             # Documentação de captura
└── README.md                       # Este arquivo
```

---

## 🚀 Como Usar

### **1. Download do Dataset**

```powershell
python questoes/scripts/download_questoes_hf.py
```

**Fonte**: `eduagarcia/oab_exams` (Hugging Face)
**Total**: 2.210 questões (2010-2018)

### **2. Processar Questões**

```powershell
python questoes/scripts/processar_questoes.py
```

**O que faz:**
- Normaliza estrutura
- Traduz tipos de questão
- Extrai alternativas e gabaritos
- Adiciona tags automáticas
- Verifica integridade

### **3. Criar Banco (Próximo)**

```powershell
python questoes/scripts/criar_banco_questoes.py
```

---

## 📋 Formato dos Dados

### **Dados Brutos** (`questoes_raw.json`)

```json
{
  "id": "2010-01_1",
  "exam_id": "2010-01",
  "exam_year": "2010",
  "question_number": 1,
  "question": "Texto da questão...",
  "choices": {
    "text": ["Alt A", "Alt B", "Alt C", "Alt D"],
    "label": ["A", "B", "C", "D"]
  },
  "answerKey": "A",
  "question_type": "CONSTITUTIONAL",
  "nullified": false
}
```

### **Dados Processados** (`questoes_processadas.json`)

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
  "enunciado": "Texto da questão...",
  "alternativas": [
    {"letra": "A", "texto": "..."},
    {"letra": "B", "texto": "..."},
    {"letra": "C", "texto": "..."},
    {"letra": "D", "texto": "..."}
  ],
  "gabarito": "A",
  "anulada": false,
  "tags": ["direito-constitucional", "ano-2010", "constitutional"]
}
```

---

## 📊 Estatísticas do Dataset

- **Total**: 2.210 questões
- **Período**: 2010-2018
- **Fases**: Apenas 1ª fase
- **Matérias**: 17+ (Constitucional, Penal, Civil, etc.)
- **Questões anuladas**: ~10-20

### **Distribuição por Matéria** (aproximado)

| Matéria | Quantidade |
|---------|------------|
| Direito Constitucional | ~300 |
| Direito Civil | ~250 |
| Direito Penal | ~200 |
| Ética Profissional | ~200 |
| Direito Processual Civil | ~180 |
| Direito do Trabalho | ~150 |
| Direito Tributário | ~130 |
| Outros | ~800 |

---

## 🔄 Atualização de Dados

Para atualizar o dataset (caso haja nova versão):

```powershell
# Backup dos dados atuais
Move-Item questoes\data\questoes_raw.json questoes\data\questoes_raw_backup.json

# Download novamente
python questoes/scripts/download_questoes_hf.py

# Reprocessar
python questoes/scripts/processar_questoes.py

# Recriar banco
python questoes/scripts/criar_banco_questoes.py
```

---

## 🎯 Uso no Sistema

### **1. Simulados** (Frontend)

```typescript
// Buscar questões por filtro
GET /api/questoes?materia=constitucional&ano=2015&limit=20

// Resposta
[
  {
    "id": "2015-01_5",
    "enunciado": "...",
    "alternativas": [...],
    "gabarito": "B"
  }
]
```

### **2. Explicações** (Agente)

```python
# Ferramenta do agente
@tool
def explicar_questao(questao_id: str) -> str:
    """Explica uma questão específica da OAB"""
    # Busca questão no banco
    # Gera explicação contextualizada
    # Cita artigos relacionados
```

---

## 🗄️ Schema do Banco (SQLite)

```sql
CREATE TABLE questoes (
    id TEXT PRIMARY KEY,
    exam_id TEXT NOT NULL,
    ano INTEGER NOT NULL,
    fase INTEGER NOT NULL,
    numero_questao INTEGER NOT NULL,
    materia TEXT NOT NULL,
    materia_original TEXT,
    assunto TEXT,
    enunciado TEXT NOT NULL,
    alternativas JSON NOT NULL,
    gabarito TEXT NOT NULL,
    justificativa TEXT,
    anulada BOOLEAN DEFAULT 0,
    dificuldade TEXT DEFAULT 'media',
    tags JSON,
    artigos_relacionados JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materia ON questoes(materia);
CREATE INDEX idx_ano ON questoes(ano);
CREATE INDEX idx_exam_id ON questoes(exam_id);
CREATE INDEX idx_anulada ON questoes(anulada);
```

---

## 📚 Documentação

- **Captura de dados**: `CAPTURA_QUESTOES.md`
- **Estrutura do projeto**: `../ESTRUTURA_PROJETO.md`
- **Execução geral**: `../COMO_EXECUTAR.md`

---

## 🔮 Roadmap

- [x] Download do Hugging Face
- [x] Processamento e normalização
- [ ] Criação do banco SQLite
- [ ] Endpoints da API (backend)
- [ ] Página de simulados (frontend)
- [ ] Ferramenta do agente para explicar
- [ ] Filtros avançados (matéria + ano + dificuldade)
- [ ] Sistema de estatísticas de acerto
- [ ] Revisão espaçada (spaced repetition)
- [ ] Exportar simulados em PDF

---

## 🆘 Suporte

Consulte `CAPTURA_QUESTOES.md` para:
- Guia passo a passo
- Troubleshooting
- Estrutura detalhada do dataset
