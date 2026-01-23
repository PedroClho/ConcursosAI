# Castro Backend API

API REST para a plataforma de ensino Castro, usando FastAPI + LangGraph.

## 🚀 Quick Start

### 1. Instalar dependências

```bash
# Da pasta raiz do projeto
pip install -r requirements.txt
```

### 2. Executar servidor

```bash
# Da pasta raiz do projeto
python backend/main.py
```

Servidor rodando em: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

---

## 📚 Endpoints Disponíveis

### **POST** `/api/oab/chat`

Chat com o Tutor OAB.

**Request:**
```json
{
  "message": "O que diz o Art. 5º da CF?",
  "conversation_history": [],
  "concurso": "oab"
}
```

**Response:**
```json
{
  "response": "O Art. 5º da Constituição Federal...",
  "sources": [],
  "timestamp": "2026-01-14T10:30:00"
}
```

---

### **POST** `/api/oab/search`

Busca direta em documentos (sem chat).

**Request:**
```json
{
  "query": "direitos fundamentais",
  "kind": "lei",
  "law_filter": "CF",
  "top_k": 5
}
```

**Response:**
```json
[
  {
    "document": "Art. 5º Todos são iguais...",
    "metadata": {
      "law_name": "Constituição Federal (CF/88)",
      "article_number": "5",
      ...
    },
    "relevance_score": 0.95
  }
]
```

---

### **GET** `/api/oab/stats`

Estatísticas da base de dados.

**Response:**
```json
{
  "total_items": 3140,
  "laws_count": 4,
  "available_laws": ["CF", "CPC", "CPP", "CTN"],
  "collection_name": "oab_corpus"
}
```

---

## 🔧 Configuração

### Variáveis de Ambiente

O backend usa as mesmas variáveis do `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sk-proj-...
```

### CORS

Por padrão, o backend aceita requests de:
- `http://localhost:3000` (Next.js)
- `http://localhost:5173` (Vite)

Para adicionar outras origens, edite `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://seu-dominio.com",  # Adicionar aqui
    ],
    ...
)
```

---

## 🧪 Testar API

### Com curl:

```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/api/oab/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, tutor!"}'

# Busca
curl -X POST http://localhost:8000/api/oab/search \
  -H "Content-Type: application/json" \
  -d '{"query": "prisão em flagrante", "kind": "lei", "top_k": 3}'
```

### Com Python:

```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/api/oab/chat",
    json={"message": "O que é prisão em flagrante?"}
)
print(response.json()['response'])

# Busca
response = requests.post(
    "http://localhost:8000/api/oab/search",
    json={"query": "Art. 5º", "law_filter": "CF"}
)
for result in response.json():
    print(f"Relevância: {result['relevance_score']:.1%}")
    print(f"Documento: {result['document'][:100]}...\n")
```

---

## 📁 Estrutura

```
backend/
├── main.py              # Aplicação FastAPI principal
├── requirements.txt     # Dependências
└── README.md           # Esta documentação
```

---

## 🔜 Próximos Passos

### Endpoints a implementar:

- [ ] `/api/oab/generate-question` - Gerar questões com IA
- [ ] `/api/oab/evaluate-answer` - Avaliar resposta do aluno
- [ ] `/api/user/{id}/progress` - Progresso do aluno
- [ ] `/api/user/{id}/study-plan` - Plano de estudos

### Melhorias:

- [ ] Sistema de autenticação (JWT)
- [ ] Rate limiting
- [ ] Caching de respostas frequentes
- [ ] Logging estruturado
- [ ] Métricas (Prometheus)
- [ ] Testes unitários

---

## 📚 Documentação

Acesse `/docs` para documentação interativa (Swagger UI)

Ou `/redoc` para documentação alternativa (ReDoc)
