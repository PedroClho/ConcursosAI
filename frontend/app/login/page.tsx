import { login, signup } from './actions'
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
