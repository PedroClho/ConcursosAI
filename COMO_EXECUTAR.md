# 🚀 Como Executar o Castro - Tutor OAB

## Pré-requisitos

- Python 3.10+ instalado
- Node.js 18+ instalado
- Chave API da OpenAI no `.env` (raiz do projeto)

---

## 🔍 Pré-verificação (Recomendado)

Antes de executar, verifique se está tudo configurado:

```bash
python verificar_config.py
```

Se tudo estiver OK ✅, continue!

---

## ⚡ Quick Start (2 Terminais)

### Terminal 1: Backend (FastAPI)

```bash
# Da pasta raiz do projeto
python backend/main.py
```

Aguarde até ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Frontend (Next.js)

```bash
# Entrar na pasta frontend
cd frontend

# Instalar dependências (primeira vez)
npm install

# Executar em modo desenvolvimento
npm run dev
```

Aguarde até ver:
```
Ready - started server on 0.0.0.0:3000
```

### 3. Acessar

Abra seu navegador em: **http://localhost:3000**

---

## 📋 Checklist de Verificação

Antes de executar, certifique-se de que:

- [ ] `.env` existe na raiz com `OPENAI_API_KEY=sk-proj-...`
- [ ] ChromaDB foi populado (`chroma_db/` existe com dados)
- [ ] Dependências Python instaladas (`pip install -r requirements.txt`)
- [ ] Dependências Node.js instaladas (`cd frontend && npm install`)

---

## 🐛 Troubleshooting

### Backend não inicia

**Erro:** `ModuleNotFoundError: No module named 'fastapi'`

**Solução:**
```bash
pip install fastapi uvicorn
```

---

**Erro:** `API Key da OpenAI não fornecida`

**Solução:** Verifique se o `.env` está correto:
```bash
# Verificar se existe
ls .env

# Verificar conteúdo (não deve ter aspas)
cat .env
```

Deve estar assim (SEM aspas):
```
OPENAI_API_KEY=sk-proj-XXXXX
```

---

### Frontend não conecta no backend

**Erro na tela:** "Não foi possível conectar ao servidor..."

**Solução:**
1. Verifique se o backend está rodando em `http://localhost:8000`
2. Teste o health check:
   ```bash
   curl http://localhost:8000/health
   ```
3. Verifique se `frontend/.env.local` existe e tem:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

---

### Frontend não instala dependências

**Erro:** `npm ERR! network`

**Solução:**
```bash
# Limpar cache do npm
npm cache clean --force

# Tentar novamente
cd frontend
npm install
```

---

### Porta 3000 já está em uso

**Erro:** `Port 3000 is already in use`

**Solução:**
```bash
# Rodar em outra porta
PORT=3001 npm run dev
```

Depois acesse: http://localhost:3001

---

## 🔄 Reiniciar do Zero

Se algo der muito errado:

```bash
# 1. Parar todos os servidores (Ctrl+C nos terminais)

# 2. Limpar frontend
cd frontend
rm -rf node_modules .next
npm install

# 3. Reiniciar backend
cd ..
python backend/main.py

# 4. Reiniciar frontend (novo terminal)
cd frontend
npm run dev
```

---

## 📦 Build para Produção

### Frontend

```bash
cd frontend
npm run build
npm start  # Roda versão otimizada na porta 3000
```

### Backend

```bash
# Instalar gunicorn
pip install gunicorn

# Rodar com gunicorn (4 workers)
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🎯 Próximos Passos

Depois que tudo estiver funcionando:

1. **Testar o chat:** Faça perguntas ao tutor
2. **Testar reiniciar:** Clique no botão "Reiniciar" no header
3. **Verificar backend:** Acesse http://localhost:8000/docs para ver a API

---

## 💾 Sobre Commits

**Você NÃO precisa commitar para testar!**

Mas se quiser versionar o código:

```bash
# Da pasta raiz do projeto
git add .
git commit -m "feat: adicionar frontend Next.js com tema escuro/verde"
```

---

## ✅ Está Funcionando?

Se você conseguir:
- ✅ Abrir http://localhost:3000
- ✅ Ver a tela de boas-vindas do tutor
- ✅ Enviar uma mensagem e receber resposta
- ✅ Clicar em "Reiniciar" e limpar o histórico

**Parabéns! Está tudo funcionando!** 🎉
