# 📦 Componentes do Castro Frontend

Componentes React reutilizáveis para a plataforma Castro de preparação para OAB.

---

## 🎯 Componentes Disponíveis

### 1. **QuestionCard** 🎴

Card completo para exibir questões de simulados com alternativas, gabarito e explicações.

**Props:**
- `questao: Questao` - Objeto com dados da questão
- `index: number` - Índice da questão (para numeração)
- `respostaUsuario?: string` - Resposta selecionada pelo usuário
- `mostrarGabarito: boolean` - Se deve mostrar gabarito e feedback
- `onSelecionarResposta: (letra: string) => void` - Callback ao selecionar alternativa
- `explicacao?: string` - Explicação do agente tutor (markdown)
- `loadingExplicacao?: boolean` - Estado de carregamento da explicação
- `onExplicar?: () => void` - Callback para solicitar explicação

**Exemplo:**
```tsx
<QuestionCard
  questao={questao}
  index={0}
  respostaUsuario="A"
  mostrarGabarito={true}
  onSelecionarResposta={(letra) => console.log(letra)}
  explicacao="Explicação em markdown..."
  onExplicar={() => buscarExplicacao()}
/>
```

**Features:**
- ✅ Visual moderno com badges
- ✅ Feedback visual (correto/incorreto)
- ✅ Integração com agente tutor
- ✅ Renderização de markdown para explicações
- ✅ Animações e transições suaves

---

### 2. **RadioGroup** 📻

Grupo de opções de rádio estilizado para alternativas de questões.

**Props:**
- `options: RadioOption[]` - Array de opções `{value, label}`
- `value?: string` - Valor selecionado
- `onChange: (value: string) => void` - Callback de mudança
- `disabled?: boolean` - Desabilitar interação
- `correctValue?: string` - Resposta correta (para feedback visual)
- `name?: string` - Nome do grupo de rádio

**Exemplo:**
```tsx
<RadioGroup
  options={[
    { value: 'A', label: 'Alternativa A' },
    { value: 'B', label: 'Alternativa B' },
  ]}
  value="A"
  onChange={(val) => setResposta(val)}
  correctValue="B"
/>
```

**Features:**
- ✅ Feedback visual para correto/incorreto
- ✅ Estados de hover e seleção
- ✅ Acessibilidade com input nativo
- ✅ Animações suaves

---

### 3. **StatsCard** 📊

Card de estatísticas com ícone, valor principal e indicador de tendência.

**Props:**
- `title: string` - Título do card
- `value: string | number` - Valor principal
- `subtitle?: string` - Subtítulo opcional
- `icon?: LucideIcon` - Ícone do Lucide React
- `trend?: object` - Objeto com tendência `{value, direction, label}`
- `color?: string` - Cor do tema (`green`, `blue`, `purple`, etc.)
- `size?: string` - Tamanho (`sm`, `md`, `lg`)

**Exemplo:**
```tsx
<StatsCard
  title="Questões Respondidas"
  value={156}
  icon={BookOpen}
  color="green"
  trend={{ value: 15, direction: 'up', label: 'vs. semana passada' }}
/>
```

**Features:**
- ✅ 7 variações de cores
- ✅ 3 tamanhos disponíveis
- ✅ Indicador de tendência (up/down)
- ✅ Ícones personalizáveis
- ✅ Hover effects

---

### 4. **ProgressBar** 📈

Barra de progresso animada com label e porcentagem.

**Props:**
- `value: number` - Valor atual
- `max?: number` - Valor máximo (padrão: 100)
- `label?: string` - Label da barra
- `showPercentage?: boolean` - Mostrar porcentagem (padrão: true)
- `color?: string` - Cor (`green`, `blue`, `purple`, etc.)
- `size?: string` - Tamanho (`sm`, `md`, `lg`)
- `animated?: boolean` - Animação shimmer (padrão: true)

**Exemplo:**
```tsx
<ProgressBar
  value={75}
  max={100}
  label="Direito Constitucional"
  color="green"
  animated={true}
/>
```

**Features:**
- ✅ Animação shimmer opcional
- ✅ 6 variações de cores
- ✅ Cálculo automático de porcentagem
- ✅ Responsivo e fluido

---

### 5. **QuestionsTable** 📋

Tabela completa para listar histórico de questões com status e métricas.

**Props:**
- `questoes: Questao[]` - Array de questões
- `onViewQuestion?: (questaoId: string) => void` - Callback para visualizar questão

**Exemplo:**
```tsx
<QuestionsTable
  questoes={questoesRecentes}
  onViewQuestion={(id) => navigate(`/questao/${id}`)}
/>
```

**Features:**
- ✅ Status visual (correto/incorreto/não respondida)
- ✅ Formatação de tempo
- ✅ Resumo no footer
- ✅ Ação de visualização
- ✅ Hover states

---

## 🎨 Paleta de Cores

Todos os componentes suportam as seguintes cores:

- `green` - Verde (principal, sucesso)
- `blue` - Azul (informação)
- `purple` - Roxo (criatividade)
- `orange` - Laranja (alerta)
- `yellow` - Amarelo (atenção)
- `pink` - Rosa (especial)
- `red` - Vermelho (erro)

---

## 🚀 Uso nas Páginas

### Página de Simulado (`/simulado`)
- ✅ `QuestionCard` - Exibir questões
- ✅ `RadioGroup` - Alternativas (dentro do QuestionCard)

### Dashboard (`/dashboard`)
- ✅ `StatsCard` - Cards de estatísticas principais
- ✅ `ProgressBar` - Progresso por matéria
- ✅ `QuestionsTable` - Histórico de questões

---

## 📦 Dependências

Todos os componentes utilizam:
- **React** (18+)
- **TypeScript**
- **Tailwind CSS**
- **Lucide React** (ícones)
- **React Markdown** (para explicações)

---

## 🎯 Roadmap de Componentes

### Implementados ✅
1. ✅ QuestionCard
2. ✅ RadioGroup
3. ✅ StatsCard
4. ✅ ProgressBar
5. ✅ QuestionsTable

### Futuros 🔮
- [ ] CalendarWidget (revisão espaçada)
- [ ] FlashCard (para artigos)
- [ ] StudyPlanCard (cronograma)
- [ ] AchievementBadge (conquistas)
- [ ] ChartCard (gráficos de desempenho)

---

## 💡 Boas Práticas

1. **Reutilização**: Use os componentes em múltiplas páginas
2. **Consistência**: Mantenha as mesmas cores/tamanhos em contextos similares
3. **Acessibilidade**: Componentes já incluem labels e aria-*
4. **Performance**: Componentes são otimizados e evitam re-renders

---

## 🐛 Troubleshooting

**Erro: "Cannot find module '@/components/...'**
- Verifique se o alias `@` está configurado em `tsconfig.json`

**Estilos não aplicados:**
- Verifique se `globals.css` está importado em `layout.tsx`
- Confirme que Tailwind está configurado corretamente

**Ícones não aparecem:**
- Instale `lucide-react`: `npm install lucide-react`

---

**Desenvolvido com ❤️ para Castro - Plataforma OAB**
