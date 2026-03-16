import { createClient } from './supabase/client'

export async function getUserChats() {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return []

    const { data, error } = await supabase
        .from('chats')
        .select('*')
        .eq('user_id', user.id)
        .order('updated_at', { ascending: false })

    if (error) {
        console.error('Error fetching chats:', error)
        return []
    }

    return data
}

export async function createNewChat(title: string) {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('User not logged in')

    // O limite de 3 chats é verificado pelo banco de dados (Trigger)
    const { data, error } = await supabase
        .from('chats')
        .insert([{ user_id: user.id, title }])
        .select()
        .single()

    if (error) {
        throw new Error(error.message)
    }

    return data
}

export async function deleteChat(chatId: string) {
    const supabase = createClient()
    const { error } = await supabase
        .from('chats')
        .delete()
        .eq('id', chatId)

    if (error) {
        throw new Error('Erro ao deletar chat: ' + error.message)
    }
}

export async function getChatMessages(chatId: string) {
    const supabase = createClient()
    const { data, error } = await supabase
        .from('messages')
        .select('*')
        .eq('chat_id', chatId)
        .order('created_at', { ascending: true })

    if (error) {
        console.error('Error fetching messages:', error)
        return []
    }

    return data.map(msg => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.created_at)
    }))
}

export async function saveMessage(chatId: string, role: 'user' | 'assistant', content: string) {
    const supabase = createClient()
    const { error } = await supabase
        .from('messages')
        .insert([{ chat_id: chatId, role, content }])

    if (error) {
        console.error('Error saving message:', error)
    }

    // Atualiza updated_at do chat
    await supabase
        .from('chats')
        .update({ updated_at: new Date().toISOString() })
        .eq('id', chatId)
}
