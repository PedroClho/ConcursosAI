-- =================================================================================
-- SUPABASE SCHEMA SETUP FOR ATLAS (CONCURSOS AI)
-- =================================================================================

-- 1. Profiles Table
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL PRIMARY KEY,
  full_name TEXT,
  avatar_url TEXT,
  objective TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Chats Table
CREATE TABLE chats (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Trigger to enforce maximum of 3 chats per user
CREATE OR REPLACE FUNCTION check_chat_limit()
RETURNS trigger AS $$
DECLARE
  chat_count integer;
BEGIN
  SELECT COUNT(*) INTO chat_count FROM chats WHERE user_id = NEW.user_id;
  IF chat_count >= 3 THEN
    RAISE EXCEPTION 'Chat limit reached (maximum 3 chats per user). Please delete an existing chat first.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_chat_limit_trigger
BEFORE INSERT ON chats
FOR EACH ROW EXECUTE PROCEDURE check_chat_limit();

-- 4. Messages Table
CREATE TABLE messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  chat_id UUID REFERENCES chats(id) ON DELETE CASCADE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. User Dashboard General Statistics
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

-- 6. User Dashboard Subject Statistics
CREATE TABLE user_subject_statistics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  subject_name TEXT NOT NULL,
  questoes_respondidas INTEGER DEFAULT 0,
  acertos INTEGER DEFAULT 0,
  UNIQUE(user_id, subject_name)
);


-- =================================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =================================================================================

-- PROFILES
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

-- CHATS
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own chats" ON chats FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own chats" ON chats FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own chats" ON chats FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own chats" ON chats FOR DELETE USING (auth.uid() = user_id);

-- MESSAGES
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view messages of own chats" ON messages 
FOR SELECT USING (EXISTS (SELECT 1 FROM chats WHERE id = messages.chat_id AND user_id = auth.uid()));
CREATE POLICY "Users can insert messages to own chats" ON messages 
FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM chats WHERE id = messages.chat_id AND user_id = auth.uid()));
CREATE POLICY "Users can delete messages of own chats" ON messages 
FOR DELETE USING (EXISTS (SELECT 1 FROM chats WHERE id = messages.chat_id AND user_id = auth.uid()));

-- USER STATISTICS
ALTER TABLE user_statistics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own statistics" ON user_statistics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own statistics" ON user_statistics FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own statistics" ON user_statistics FOR UPDATE USING (auth.uid() = user_id);

-- USER SUBJECT STATISTICS
ALTER TABLE user_subject_statistics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own subject statistics" ON user_subject_statistics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own subject statistics" ON user_subject_statistics FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own subject statistics" ON user_subject_statistics FOR UPDATE USING (auth.uid() = user_id);

-- =================================================================================
-- AUTOMATIC PROFILE CREATION TRIGGER
-- =================================================================================
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
  
  -- Prevent failure if there are issues, although in production we might want it to fail
  -- initialize user stats
  INSERT INTO public.user_statistics (user_id)
  VALUES (NEW.id);
  
  -- Initialize empty subjects (Optional, frontend can create them later or we can do it here)
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Enable Realtime for relevant tables if needed (optional)
alter publication supabase_realtime add table chats;
alter publication supabase_realtime add table messages;
