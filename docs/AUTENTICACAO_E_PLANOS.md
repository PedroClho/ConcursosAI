# 🔐 Autenticação e Sistema de Planos - Atlas Concursos

## 📋 Índice
1. [Estado Atual da Autenticação](#estado-atual)
2. [Estrutura do Banco de Dados](#estrutura-banco)
3. [Plano de Implementação](#plano-implementacao)
4. [Google OAuth](#google-oauth)
5. [Stripe e Planos de Assinatura](#stripe-planos)
6. [Roadmap de Implementação](#roadmap)

---

## 🎯 Estado Atual da Autenticação {#estado-atual}

### ✅ O que já está implementado

#### 1. **Supabase Auth (Básico)**
A aplicação já utiliza o Supabase Auth como sistema de autenticação principal, com:

- **Email/Senha**: Login e cadastro tradicional
- **JWT Tokens**: Gerenciamento de sessão via cookies
- **Middleware de Proteção**: Rotas protegidas automaticamente
- **Validação Backend**: API FastAPI valida tokens Supabase

#### 2. **Frontend (Next.js 15)**

**Página de Login** (`frontend/app/login/page.tsx`):
```typescript
// Formulário simples com email e senha
// Dois botões: "Entrar" e "Cadastrar"
```

**Actions de Autenticação** (`frontend/app/login/actions.ts`):
```typescript
// login(formData) - Login com email/senha
// signup(formData) - Cadastro com email/senha e nome completo
```

**Middleware** (`frontend/middleware.ts`):
- Protege rotas privadas (redireciona para `/login` se não autenticado)
- Redireciona usuários logados de `/login` para `/dashboard`
- Atualiza sessão automaticamente

**Clientes Supabase**:
- `lib/supabase/server.ts` - Para Server Components e Actions
- `lib/supabase/client.ts` - Para Client Components
- `lib/supabase/middleware.ts` - Para Next.js Middleware

#### 3. **Backend (FastAPI)**

**Autenticação JWT** (`backend/main.py`):
```python
# HTTPBearer security scheme
# get_current_user() - Valida token JWT do Supabase
# Protege endpoints sensíveis
```

#### 4. **Banco de Dados**

**Tabela `profiles`**:
- Criada automaticamente via trigger quando usuário se cadastra
- Armazena: `id`, `full_name`, `avatar_url`, `objective`
- RLS habilitado (usuário só vê próprio perfil)

**Trigger Automático**:
```sql
-- handle_new_user() é executado após INSERT em auth.users
-- Cria perfil e estatísticas iniciais automaticamente
```

---

## 🗄️ Estrutura do Banco de Dados {#estrutura-banco}

### Tabelas Existentes

#### **`auth.users`** (Tabela nativa do Supabase)
Gerenciada automaticamente pelo Supabase Auth:
- `id` (UUID) - Primary Key
- `email` - Email do usuário
- `encrypted_password` - Senha criptografada
- `email_confirmed_at` - Data de confirmação do email
- `raw_user_meta_data` - Metadados customizados (nome, avatar, etc)
- `created_at`, `updated_at`

#### **`profiles`** (Tabela customizada)
```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL PRIMARY KEY,
  full_name TEXT,
  avatar_url TEXT,
  objective TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

**RLS Policies**:
- ✅ Usuários podem ver próprio perfil
- ✅ Usuários podem atualizar próprio perfil

#### **`user_statistics`**
```sql
CREATE TABLE user_statistics (
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL PRIMARY KEY,
  questoes_respondidas INTEGER DEFAULT 0,
  acertos INTEGER DEFAULT 0,
  horas_estudo NUMERIC DEFAULT 0,
  sequencia_atual INTEGER DEFAULT 0,
  melhor_sequencia INTEGER DEFAULT 0,
  simulados_feitos INTEGER DEFAULT 0,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
```

#### **`chats`** e **`messages`**
Sistema de chat com tutor IA (limite de 3 chats por usuário).

### Trigger de Criação Automática

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  -- Cria perfil
  INSERT INTO public.profiles (id, full_name, avatar_url)
  VALUES (
    NEW.id, 
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  );
  
  -- Inicializa estatísticas
  INSERT INTO public.user_statistics (user_id)
  VALUES (NEW.id);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

---

## 📝 Plano de Implementação {#plano-implementacao}

### Fase 1: Google OAuth ✨
**Objetivo**: Permitir login com Google (além de email/senha)

### Fase 2: Sistema de Planos com Stripe 💳
**Objetivo**: Monetização com planos Free, Pro e Premium

---

## 🔑 Google OAuth - Implementação Detalhada {#google-oauth}

### 1. Configuração no Google Cloud Console

#### Passo 1: Criar Projeto no Google Cloud
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto: **"Atlas Concursos"**
3. Ative a **Google+ API** (ou **Google Identity Services**)

#### Passo 2: Configurar OAuth Consent Screen
1. Vá em **APIs & Services** → **OAuth consent screen**
2. Escolha **External** (para permitir qualquer conta Google)
3. Preencha:
   - **App name**: Atlas Concursos
   - **User support email**: seu-email@dominio.com
   - **Developer contact**: seu-email@dominio.com
4. **Scopes**: Adicione `email`, `profile`, `openid`

#### Passo 3: Criar Credenciais OAuth 2.0
1. Vá em **APIs & Services** → **Credentials**
2. Clique em **Create Credentials** → **OAuth 2.0 Client ID**
3. Tipo: **Web application**
4. **Authorized redirect URIs**:
   ```
   https://[SEU_PROJETO].supabase.co/auth/v1/callback
   http://localhost:54321/auth/v1/callback (para dev local)
   ```
5. Copie o **Client ID** e **Client Secret**

### 2. Configuração no Supabase Dashboard

#### Passo 1: Habilitar Google Provider
1. Acesse [Supabase Dashboard](https://app.supabase.com/)
2. Vá em **Authentication** → **Providers**
3. Encontre **Google** e clique em **Enable**
4. Cole:
   - **Client ID** (do Google Cloud)
   - **Client Secret** (do Google Cloud)
5. Salve

### 3. Implementação no Frontend

#### Atualizar `frontend/app/login/actions.ts`

```typescript
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

// Ação existente de login com email/senha
export async function login(formData: FormData) {
    const supabase = await createClient()
    const data = {
        email: formData.get('email') as string,
        password: formData.get('password') as string,
    }
    const { error } = await supabase.auth.signInWithPassword(data)
    if (error) {
        return redirect('/login?message=Não foi possível autenticar o usuário')
    }
    revalidatePath('/', 'layout')
    redirect('/dashboard')
}

// Ação existente de cadastro
export async function signup(formData: FormData) {
    const supabase = await createClient()
    const data = {
        email: formData.get('email') as string,
        password: formData.get('password') as string,
        options: {
            data: {
                full_name: formData.get('name') as string,
            }
        }
    }
    const { error } = await supabase.auth.signUp(data)
    if (error) {
        return redirect('/login?message=Erro ao tentar criar a conta. A senha pode ser fraca.')
    }
    revalidatePath('/', 'layout')
    redirect('/dashboard')
}

// 🆕 NOVA AÇÃO: Login com Google
export async function signInWithGoogle() {
    const supabase = await createClient()
    
    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
            queryParams: {
                access_type: 'offline',
                prompt: 'consent',
            },
        },
    })

    if (error) {
        return redirect('/login?message=Erro ao tentar fazer login com Google')
    }

    if (data.url) {
        redirect(data.url) // Redireciona para o Google OAuth
    }
}
```

#### Atualizar `frontend/app/login/page.tsx`

```typescript
import { login, signup, signInWithGoogle } from './actions'
import { GraduationCap } from 'lucide-react'

export default async function LoginPage(props: { searchParams: Promise<{ message?: string }> }) {
    const searchParams = await props.searchParams
    return (
        <div className="flex h-screen w-screen items-center justify-center bg-background">
            <div className="w-full max-w-sm p-8 space-y-6 bg-card rounded-xl shadow-lg border border-border">
                <div className="flex flex-col items-center justify-center space-y-2">
                    <div className="bg-primary p-3 rounded-full">
                        <GraduationCap className="h-8 w-8 text-primary-foreground" />
                    </div>
                    <h1 className="text-2xl font-bold">Atlas Concursos</h1>
                    <p className="text-sm text-muted-foreground text-center">
                        Faça login na sua conta para acessar seu tutor e dashboard.
                    </p>
                </div>

                {searchParams?.message && (
                    <div className="p-3 text-sm text-center text-red-500 bg-red-100 rounded-lg">
                        {searchParams.message}
                    </div>
                )}

                {/* 🆕 BOTÃO GOOGLE - Adicionar ANTES do formulário */}
                <form action={signInWithGoogle}>
                    <button
                        type="submit"
                        className="w-full flex items-center justify-center gap-3 bg-white hover:bg-gray-50 text-gray-700 font-medium py-2.5 px-4 rounded-md border border-gray-300 transition-colors"
                    >
                        <svg className="w-5 h-5" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Continuar com Google
                    </button>
                </form>

                {/* Divisor */}
                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-300"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-card text-muted-foreground">Ou continue com email</span>
                    </div>
                </div>

                {/* Formulário existente de email/senha */}
                <form className="flex flex-col space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium" htmlFor="email">
                            Email
                        </label>
                        <input
                            className="w-full border border-input bg-background rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                            id="email"
                            name="email"
                            placeholder="seu@email.com"
                            required
                            type="email"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium" htmlFor="password">
                            Senha
                        </label>
                        <input
                            className="w-full border border-input bg-background rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                            id="password"
                            name="password"
                            placeholder="••••••••"
                            required
                            type="password"
                        />
                    </div>

                    <div className="flex gap-2 pt-2">
                        <button
                            formAction={login}
                            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-medium py-2 px-4 rounded-md transition-colors"
                        >
                            Entrar
                        </button>
                        <button
                            formAction={signup}
                            className="w-full bg-secondary hover:bg-secondary/80 text-secondary-foreground font-medium py-2 px-4 rounded-md transition-colors"
                        >
                            Cadastrar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
```

#### Criar `frontend/app/auth/callback/route.ts`

```typescript
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const origin = requestUrl.origin

    if (code) {
        const supabase = await createClient()
        await supabase.auth.exchangeCodeForSession(code)
    }

    // Redireciona para o dashboard após login bem-sucedido
    return NextResponse.redirect(`${origin}/dashboard`)
}
```

#### Atualizar `.env.local`

```env
NEXT_PUBLIC_SUPABASE_URL=https://[SEU_PROJETO].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJh...
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### 4. Ajustes no Trigger de Criação de Perfil

O trigger atual já suporta OAuth! Quando o usuário faz login com Google:
- `raw_user_meta_data->>'full_name'` vem do Google
- `raw_user_meta_data->>'avatar_url'` vem da foto do Google

**Nenhuma alteração necessária no banco de dados!** ✅

### 5. Teste

1. Inicie o frontend: `npm run dev`
2. Acesse `http://localhost:3000/login`
3. Clique em "Continuar com Google"
4. Faça login com sua conta Google
5. Você será redirecionado para `/dashboard`

---

## 💳 Stripe e Planos de Assinatura {#stripe-planos}

### Estrutura de Planos

| Plano | Preço | Recursos |
|-------|-------|----------|
| **Free** | R$ 0/mês | • 10 perguntas ao tutor/dia<br>• 1 chat simultâneo<br>• Estatísticas básicas |
| **Pro** | R$ 29,90/mês | • 100 perguntas ao tutor/dia<br>• 3 chats simultâneos<br>• Estatísticas avançadas<br>• Simulados ilimitados |
| **Premium** | R$ 59,90/mês | • Perguntas ilimitadas<br>• Chats ilimitados<br>• Estatísticas completas<br>• Simulados ilimitados<br>• Suporte prioritário |

### 1. Configuração do Stripe

#### Passo 1: Criar Conta Stripe
1. Acesse [Stripe Dashboard](https://dashboard.stripe.com/)
2. Crie uma conta (ou faça login)
3. Ative o **Modo de Teste** para desenvolvimento

#### Passo 2: Criar Produtos e Preços
1. Vá em **Produtos** → **Adicionar produto**
2. Crie 3 produtos:

**Produto 1: Atlas Pro**
- Nome: `Atlas Pro`
- Descrição: `Plano Pro com recursos avançados`
- Preço: `R$ 29,90 / mês` (recorrente)
- Copie o **Price ID**: `price_xxxxxxxxxxxxx`

**Produto 2: Atlas Premium**
- Nome: `Atlas Premium`
- Descrição: `Plano Premium com recursos ilimitados`
- Preço: `R$ 59,90 / mês` (recorrente)
- Copie o **Price ID**: `price_yyyyyyyyyyyyy`

#### Passo 3: Configurar Webhook
1. Vá em **Developers** → **Webhooks**
2. Clique em **Add endpoint**
3. URL do endpoint:
   ```
   https://seu-dominio.com/api/webhooks/stripe
   ```
4. Eventos a ouvir:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copie o **Webhook Secret**: `whsec_xxxxxxxxxxxxx`

#### Passo 4: Obter API Keys
1. Vá em **Developers** → **API keys**
2. Copie:
   - **Publishable key**: `pk_test_xxxxxxxxxxxxx`
   - **Secret key**: `sk_test_xxxxxxxxxxxxx`

### 2. Atualizar Schema do Banco de Dados

#### Adicionar ao `supabase_schema.sql`:

```sql
-- =================================================================================
-- SISTEMA DE PLANOS E ASSINATURAS (STRIPE)
-- =================================================================================

-- Enum para tipos de plano
CREATE TYPE subscription_tier AS ENUM ('free', 'pro', 'premium');

-- Enum para status de assinatura
CREATE TYPE subscription_status AS ENUM ('active', 'canceled', 'past_due', 'trialing', 'incomplete');

-- Tabela de assinaturas
CREATE TABLE subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL UNIQUE,
  tier subscription_tier DEFAULT 'free' NOT NULL,
  status subscription_status DEFAULT 'active' NOT NULL,
  
  -- Dados do Stripe
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  stripe_price_id TEXT,
  
  -- Datas
  current_period_start TIMESTAMP WITH TIME ZONE,
  current_period_end TIMESTAMP WITH TIME ZONE,
  cancel_at_period_end BOOLEAN DEFAULT false,
  
  -- Limites de uso (resetados mensalmente)
  questions_used_this_month INTEGER DEFAULT 0,
  questions_limit INTEGER DEFAULT 10, -- Free: 10, Pro: 100, Premium: -1 (ilimitado)
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- RLS para subscriptions
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own subscription" ON subscriptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own subscription" ON subscriptions FOR UPDATE USING (auth.uid() = user_id);

-- Tabela de histórico de pagamentos
CREATE TABLE payment_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
  
  stripe_invoice_id TEXT,
  stripe_payment_intent_id TEXT,
  
  amount_paid NUMERIC NOT NULL,
  currency TEXT DEFAULT 'brl',
  status TEXT NOT NULL, -- 'succeeded', 'failed', 'pending'
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- RLS para payment_history
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own payment history" ON payment_history FOR SELECT USING (auth.uid() = user_id);

-- Atualizar trigger de criação de usuário para incluir subscription
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  -- Insert into profiles
  INSERT INTO public.profiles (id, full_name, avatar_url)
  VALUES (
    NEW.id, 
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  );
  
  -- Initialize user stats
  INSERT INTO public.user_statistics (user_id)
  VALUES (NEW.id);
  
  -- 🆕 Initialize subscription (Free tier)
  INSERT INTO public.subscriptions (user_id, tier, status, questions_limit)
  VALUES (NEW.id, 'free', 'active', 10);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para resetar contador de perguntas mensalmente
CREATE OR REPLACE FUNCTION reset_monthly_question_count()
RETURNS void AS $$
BEGIN
  UPDATE subscriptions
  SET questions_used_this_month = 0
  WHERE current_period_end < NOW();
END;
$$ LANGUAGE plpgsql;

-- (Opcional) Criar um cron job no Supabase para executar diariamente
-- Vá em Database → Cron Jobs e adicione:
-- SELECT cron.schedule('reset-monthly-questions', '0 0 * * *', 'SELECT reset_monthly_question_count()');
```

### 3. Implementação no Frontend

#### Instalar Stripe SDK

```bash
npm install @stripe/stripe-js stripe
```

#### Criar `frontend/lib/stripe.ts`

```typescript
import { loadStripe, Stripe } from '@stripe/stripe-js'

let stripePromise: Promise<Stripe | null>

export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!)
  }
  return stripePromise
}
```

#### Criar `frontend/app/api/create-checkout-session/route.ts`

```typescript
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
})

export async function POST(request: Request) {
  try {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
    }

    const { priceId, tier } = await request.json()

    // Buscar ou criar customer no Stripe
    const { data: subscription } = await supabase
      .from('subscriptions')
      .select('stripe_customer_id')
      .eq('user_id', user.id)
      .single()

    let customerId = subscription?.stripe_customer_id

    if (!customerId) {
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: {
          supabase_user_id: user.id,
        },
      })
      customerId = customer.id

      // Atualizar no banco
      await supabase
        .from('subscriptions')
        .update({ stripe_customer_id: customerId })
        .eq('user_id', user.id)
    }

    // Criar sessão de checkout
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: `${process.env.NEXT_PUBLIC_SITE_URL}/dashboard?success=true`,
      cancel_url: `${process.env.NEXT_PUBLIC_SITE_URL}/pricing?canceled=true`,
      metadata: {
        user_id: user.id,
        tier: tier,
      },
    })

    return NextResponse.json({ sessionId: session.id })
  } catch (error: any) {
    console.error('Erro ao criar checkout session:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
```

#### Criar `frontend/app/api/webhooks/stripe/route.ts`

```typescript
import { NextResponse } from 'next/server'
import { headers } from 'next/headers'
import Stripe from 'stripe'
import { createClient } from '@supabase/supabase-js'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-11-20.acacia',
})

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!

// Supabase com service_role para bypass RLS
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function POST(request: Request) {
  const body = await request.text()
  const headersList = await headers()
  const signature = headersList.get('stripe-signature')!

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret)
  } catch (err: any) {
    console.error('Webhook signature verification failed:', err.message)
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  // Processar evento
  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session
      const userId = session.metadata?.user_id
      const tier = session.metadata?.tier as 'pro' | 'premium'

      if (userId && tier) {
        const questionsLimit = tier === 'pro' ? 100 : -1 // -1 = ilimitado

        await supabase
          .from('subscriptions')
          .update({
            tier: tier,
            status: 'active',
            stripe_subscription_id: session.subscription as string,
            stripe_price_id: session.line_items?.data[0]?.price?.id,
            current_period_start: new Date(session.created * 1000).toISOString(),
            questions_limit: questionsLimit,
            updated_at: new Date().toISOString(),
          })
          .eq('user_id', userId)
      }
      break
    }

    case 'customer.subscription.updated': {
      const subscription = event.data.object as Stripe.Subscription
      const customerId = subscription.customer as string

      // Buscar user_id pelo stripe_customer_id
      const { data: subData } = await supabase
        .from('subscriptions')
        .select('user_id')
        .eq('stripe_customer_id', customerId)
        .single()

      if (subData) {
        await supabase
          .from('subscriptions')
          .update({
            status: subscription.status as any,
            current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
            current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
            cancel_at_period_end: subscription.cancel_at_period_end,
            updated_at: new Date().toISOString(),
          })
          .eq('user_id', subData.user_id)
      }
      break
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object as Stripe.Subscription
      const customerId = subscription.customer as string

      const { data: subData } = await supabase
        .from('subscriptions')
        .select('user_id')
        .eq('stripe_customer_id', customerId)
        .single()

      if (subData) {
        // Voltar para plano Free
        await supabase
          .from('subscriptions')
          .update({
            tier: 'free',
            status: 'active',
            stripe_subscription_id: null,
            stripe_price_id: null,
            questions_limit: 10,
            questions_used_this_month: 0,
            updated_at: new Date().toISOString(),
          })
          .eq('user_id', subData.user_id)
      }
      break
    }

    case 'invoice.payment_succeeded': {
      const invoice = event.data.object as Stripe.Invoice
      const customerId = invoice.customer as string

      const { data: subData } = await supabase
        .from('subscriptions')
        .select('user_id, id')
        .eq('stripe_customer_id', customerId)
        .single()

      if (subData) {
        // Registrar pagamento
        await supabase.from('payment_history').insert({
          user_id: subData.user_id,
          subscription_id: subData.id,
          stripe_invoice_id: invoice.id,
          stripe_payment_intent_id: invoice.payment_intent as string,
          amount_paid: invoice.amount_paid / 100, // Converter de centavos
          currency: invoice.currency,
          status: 'succeeded',
        })
      }
      break
    }

    case 'invoice.payment_failed': {
      const invoice = event.data.object as Stripe.Invoice
      const customerId = invoice.customer as string

      const { data: subData } = await supabase
        .from('subscriptions')
        .select('user_id')
        .eq('stripe_customer_id', customerId)
        .single()

      if (subData) {
        // Atualizar status para past_due
        await supabase
          .from('subscriptions')
          .update({
            status: 'past_due',
            updated_at: new Date().toISOString(),
          })
          .eq('user_id', subData.user_id)
      }
      break
    }
  }

  return NextResponse.json({ received: true })
}
```

#### Criar página de preços `frontend/app/pricing/page.tsx`

```typescript
'use client'

import { useState } from 'react'
import { getStripe } from '@/lib/stripe'
import { Check } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    price: 'R$ 0',
    period: '/mês',
    description: 'Para começar seus estudos',
    features: [
      '10 perguntas ao tutor/dia',
      '1 chat simultâneo',
      'Estatísticas básicas',
      'Simulados básicos',
    ],
    priceId: null, // Free não tem checkout
    tier: 'free',
    cta: 'Plano Atual',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: 'R$ 29,90',
    period: '/mês',
    description: 'Para estudantes dedicados',
    features: [
      '100 perguntas ao tutor/dia',
      '3 chats simultâneos',
      'Estatísticas avançadas',
      'Simulados ilimitados',
      'Histórico completo',
    ],
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_PRO!,
    tier: 'pro',
    cta: 'Assinar Pro',
    highlighted: true,
  },
  {
    name: 'Premium',
    price: 'R$ 59,90',
    period: '/mês',
    description: 'Para máximo desempenho',
    features: [
      'Perguntas ilimitadas',
      'Chats ilimitados',
      'Estatísticas completas',
      'Simulados ilimitados',
      'Suporte prioritário',
      'Análise de desempenho com IA',
    ],
    priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID_PREMIUM!,
    tier: 'premium',
    cta: 'Assinar Premium',
    highlighted: false,
  },
]

export default function PricingPage() {
  const [loading, setLoading] = useState<string | null>(null)

  const handleSubscribe = async (priceId: string, tier: string) => {
    setLoading(tier)

    try {
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId, tier }),
      })

      const { sessionId, error } = await response.json()

      if (error) {
        alert(error)
        return
      }

      const stripe = await getStripe()
      await stripe?.redirectToCheckout({ sessionId })
    } catch (error) {
      console.error('Erro:', error)
      alert('Erro ao processar pagamento')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Escolha seu plano</h1>
          <p className="text-muted-foreground text-lg">
            Selecione o plano ideal para seus estudos
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div
              key={plan.tier}
              className={`rounded-xl border p-8 ${
                plan.highlighted
                  ? 'border-primary shadow-lg scale-105'
                  : 'border-border'
              }`}
            >
              {plan.highlighted && (
                <div className="bg-primary text-primary-foreground text-sm font-medium px-3 py-1 rounded-full inline-block mb-4">
                  Mais Popular
                </div>
              )}

              <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
              <div className="mb-4">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-muted-foreground">{plan.period}</span>
              </div>
              <p className="text-muted-foreground mb-6">{plan.description}</p>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() =>
                  plan.priceId && handleSubscribe(plan.priceId, plan.tier)
                }
                disabled={!plan.priceId || loading === plan.tier}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  plan.highlighted
                    ? 'bg-primary hover:bg-primary/90 text-primary-foreground'
                    : 'bg-secondary hover:bg-secondary/80 text-secondary-foreground'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {loading === plan.tier ? 'Processando...' : plan.cta}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
```

#### Atualizar `.env.local`

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://[SEU_PROJETO].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJh...
SUPABASE_SERVICE_ROLE_KEY=eyJh... # Para webhooks

# Site
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Price IDs dos produtos
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO=price_xxxxxxxxxxxxx
NEXT_PUBLIC_STRIPE_PRICE_ID_PREMIUM=price_yyyyyyyyyyyyy
```

### 4. Implementar Verificação de Limites

#### Criar `frontend/lib/subscription.ts`

```typescript
import { createClient } from '@/lib/supabase/server'

export async function checkQuestionLimit(): Promise<{
  allowed: boolean
  tier: string
  used: number
  limit: number
}> {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    return { allowed: false, tier: 'free', used: 0, limit: 0 }
  }

  const { data: subscription } = await supabase
    .from('subscriptions')
    .select('tier, questions_used_this_month, questions_limit')
    .eq('user_id', user.id)
    .single()

  if (!subscription) {
    return { allowed: false, tier: 'free', used: 0, limit: 0 }
  }

  const { tier, questions_used_this_month, questions_limit } = subscription

  // Premium tem limite -1 (ilimitado)
  if (questions_limit === -1) {
    return { allowed: true, tier, used: questions_used_this_month, limit: -1 }
  }

  const allowed = questions_used_this_month < questions_limit

  return {
    allowed,
    tier,
    used: questions_used_this_month,
    limit: questions_limit,
  }
}

export async function incrementQuestionCount() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) return

  await supabase.rpc('increment_question_count', { user_id: user.id })
}
```

#### Adicionar função RPC no banco:

```sql
-- Função para incrementar contador de perguntas
CREATE OR REPLACE FUNCTION increment_question_count(user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE subscriptions
  SET questions_used_this_month = questions_used_this_month + 1
  WHERE subscriptions.user_id = increment_question_count.user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

#### Usar no endpoint de chat (backend):

```python
# backend/main.py

@app.post("/api/oab/chat")
async def oab_chat(
    request: ChatRequest,
    current_user: Any = Depends(get_current_user)
):
    # Verificar limite de perguntas
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    supabase = create_client(supabase_url, supabase_key)
    
    subscription = supabase.table('subscriptions').select('*').eq('user_id', current_user.id).single().execute()
    
    if subscription.data:
        used = subscription.data['questions_used_this_month']
        limit = subscription.data['questions_limit']
        
        # Premium tem limite -1 (ilimitado)
        if limit != -1 and used >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Limite de perguntas atingido ({limit}/mês). Faça upgrade do seu plano."
            )
    
    # Processar chat normalmente...
    # ...
    
    # Incrementar contador
    supabase.rpc('increment_question_count', {'user_id': current_user.id}).execute()
    
    return response
```

---

## 🗺️ Roadmap de Implementação {#roadmap}

### ✅ Fase 0: Concluída
- [x] Supabase Auth básico (email/senha)
- [x] Middleware de proteção de rotas
- [x] Tabelas de usuário e perfil
- [x] Trigger de criação automática

### 🚀 Fase 1: Google OAuth (1-2 dias)

**Dia 1: Configuração**
- [ ] Criar projeto no Google Cloud Console
- [ ] Configurar OAuth Consent Screen
- [ ] Obter Client ID e Secret
- [ ] Habilitar Google Provider no Supabase
- [ ] Adicionar variáveis de ambiente

**Dia 2: Implementação Frontend**
- [ ] Criar action `signInWithGoogle()`
- [ ] Adicionar botão "Continuar com Google" na página de login
- [ ] Criar route handler `/auth/callback`
- [ ] Testar fluxo completo
- [ ] Validar criação automática de perfil com dados do Google

### 💳 Fase 2: Stripe e Planos (3-5 dias)

**Dia 1: Configuração Stripe**
- [ ] Criar conta Stripe (modo teste)
- [ ] Criar produtos (Pro e Premium)
- [ ] Configurar webhook endpoint
- [ ] Obter API keys e Price IDs

**Dia 2: Schema do Banco**
- [ ] Adicionar tabelas `subscriptions` e `payment_history`
- [ ] Criar enums `subscription_tier` e `subscription_status`
- [ ] Atualizar trigger `handle_new_user()` para criar subscription Free
- [ ] Criar função `reset_monthly_question_count()`
- [ ] Criar função RPC `increment_question_count()`

**Dia 3: API Routes**
- [ ] Instalar `@stripe/stripe-js` e `stripe`
- [ ] Criar `/api/create-checkout-session`
- [ ] Criar `/api/webhooks/stripe`
- [ ] Criar `lib/stripe.ts`
- [ ] Adicionar variáveis de ambiente

**Dia 4: Interface de Planos**
- [ ] Criar página `/pricing`
- [ ] Implementar cards de planos
- [ ] Integrar botões com Stripe Checkout
- [ ] Adicionar indicador de plano atual no dashboard
- [ ] Criar página de gerenciamento de assinatura

**Dia 5: Limites e Validações**
- [ ] Criar `lib/subscription.ts` com `checkQuestionLimit()`
- [ ] Integrar verificação no backend (FastAPI)
- [ ] Adicionar mensagens de limite atingido
- [ ] Implementar reset mensal automático
- [ ] Testar fluxo completo (upgrade, downgrade, cancelamento)

### 🧪 Fase 3: Testes e Ajustes (2-3 dias)

**Testes de Autenticação**
- [ ] Testar login com email/senha
- [ ] Testar cadastro com email/senha
- [ ] Testar login com Google
- [ ] Testar criação automática de perfil
- [ ] Testar middleware de proteção

**Testes de Planos**
- [ ] Testar checkout Stripe (Pro e Premium)
- [ ] Testar webhooks (subscription created, updated, deleted)
- [ ] Testar limites de perguntas (Free, Pro, Premium)
- [ ] Testar reset mensal
- [ ] Testar cancelamento de assinatura

**Ajustes Finais**
- [ ] Melhorar mensagens de erro
- [ ] Adicionar loading states
- [ ] Otimizar UX do fluxo de pagamento
- [ ] Documentar código

### 🚀 Fase 4: Deploy (1 dia)

**Produção**
- [ ] Configurar Google OAuth para produção
- [ ] Ativar modo de produção no Stripe
- [ ] Atualizar webhook URLs
- [ ] Configurar variáveis de ambiente em produção
- [ ] Testar fluxo completo em produção

---

## 📊 Resumo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                     ESTADO ATUAL                            │
├─────────────────────────────────────────────────────────────┤
│ ✅ Supabase Auth (email/senha)                              │
│ ✅ Middleware de proteção                                   │
│ ✅ Tabelas: profiles, chats, messages, user_statistics      │
│ ✅ Trigger de criação automática                            │
│ ✅ RLS habilitado                                           │
└─────────────────────────────────────────────────────────────┘

                            ⬇️

┌─────────────────────────────────────────────────────────────┐
│                   FASE 1: GOOGLE OAUTH                      │
├─────────────────────────────────────────────────────────────┤
│ 🔧 Google Cloud Console                                     │
│ 🔧 Supabase Provider Config                                 │
│ 🔧 Frontend: signInWithGoogle()                             │
│ 🔧 Route: /auth/callback                                    │
└─────────────────────────────────────────────────────────────┘

                            ⬇️

┌─────────────────────────────────────────────────────────────┐
│              FASE 2: STRIPE E PLANOS                        │
├─────────────────────────────────────────────────────────────┤
│ 💳 Stripe Dashboard Setup                                   │
│ 💳 Tabelas: subscriptions, payment_history                  │
│ 💳 API: /api/create-checkout-session                        │
│ 💳 Webhook: /api/webhooks/stripe                            │
│ 💳 Página: /pricing                                         │
│ 💳 Limites e validações                                     │
└─────────────────────────────────────────────────────────────┘

                            ⬇️

┌─────────────────────────────────────────────────────────────┐
│                    RESULTADO FINAL                          │
├─────────────────────────────────────────────────────────────┤
│ ✨ Login com Email/Senha OU Google                          │
│ ✨ 3 Planos: Free, Pro (R$ 29,90), Premium (R$ 59,90)      │
│ ✨ Limites de perguntas por plano                           │
│ ✨ Pagamentos recorrentes via Stripe                        │
│ ✨ Webhooks para sincronização automática                   │
│ ✨ Histórico de pagamentos                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 Links Úteis

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Supabase OAuth with Google](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Stripe Docs](https://stripe.com/docs)
- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions/overview)
- [Next.js Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)

---

## 📝 Notas Importantes

1. **Segurança**: Sempre use `SUPABASE_SERVICE_ROLE_KEY` apenas no backend/webhooks, nunca exponha no frontend
2. **Webhooks**: Configure o endpoint do Stripe webhook ANTES de ir para produção
3. **Testes**: Use o modo de teste do Stripe durante desenvolvimento
4. **RLS**: Todas as tabelas têm Row Level Security habilitado
5. **Limites**: O reset mensal de perguntas pode ser feito via cron job ou webhook do Stripe

---

**Documento criado em**: 07/03/2026
**Versão**: 1.0
**Autor**: Atlas Concursos Team
