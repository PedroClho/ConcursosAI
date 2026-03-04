/**
 * API Client para comunicação com o backend Atlas
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

interface ChatResponse {
  response: string
  sources: any[]
  timestamp: string
}

/**
 * Envia uma mensagem para o Atlas
 */
export async function sendMessage(
  message: string,
  conversationHistory: Message[] = []
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/oab/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp?.toISOString()
      })),
      concurso: 'oab'
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }))
    throw new Error(error.detail || `Erro ${response.status}`)
  }

  return response.json()
}

/**
 * Busca documentos no banco de leis
 */
export async function searchDocuments(
  query: string,
  options?: {
    kind?: string
    law_filter?: string
    top_k?: number
  }
): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/oab/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      ...options
    }),
  })

  if (!response.ok) {
    throw new Error(`Erro ao buscar: ${response.status}`)
  }

  return response.json()
}

/**
 * Obtém estatísticas do banco de dados
 */
export async function getStats(): Promise<{
  total_items: number
  laws_count: number
  available_laws: string[]
  collection_name: string
}> {
  const response = await fetch(`${API_BASE_URL}/api/oab/stats`)

  if (!response.ok) {
    throw new Error(`Erro ao obter estatísticas: ${response.status}`)
  }

  return response.json()
}

/**
 * Lista matérias disponíveis no banco de questões
 */
export async function getMaterias(): Promise<{ nome: string; total: number }[]> {
  const response = await fetch(`${API_BASE_URL}/api/questoes/materias`)

  if (!response.ok) {
    throw new Error(`Erro ao listar matérias: ${response.status}`)
  }

  return response.json()
}

/**
 * Filtra questões por critérios
 */
export async function filtrarQuestoes(filtros: {
  materia?: string
  ano?: number
  fase?: number
  limit?: number
  offset?: number
  incluir_anuladas?: boolean
}): Promise<{
  questoes: any[]
  total: number
  offset: number
  limit: number
}> {
  const response = await fetch(`${API_BASE_URL}/api/questoes/filtrar`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(filtros),
  })

  if (!response.ok) {
    throw new Error(`Erro ao filtrar questões: ${response.status}`)
  }

  return response.json()
}

/**
 * Obtém uma questão aleatória de uma matéria
 */
export async function getQuestaoAleatoria(materia: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/questoes/random/${encodeURIComponent(materia)}`)

  if (!response.ok) {
    throw new Error(`Erro ao buscar questão: ${response.status}`)
  }

  return response.json()
}
