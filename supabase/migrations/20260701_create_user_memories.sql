CREATE TABLE IF NOT EXISTS user_memories (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  workspace_id int REFERENCES workspaces(id) ON DELETE CASCADE,
  content text NOT NULL,
  embedding vector(1536),
  created_at timestamp with time zone DEFAULT now()
);

-- Enable RLS
ALTER TABLE user_memories ENABLE ROW LEVEL SECURITY;

-- Workspace isolation policy
CREATE POLICY "Users can access memories for their workspaces"
  ON user_memories
  FOR ALL
  USING (
    workspace_id IN (
      SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    )
  );

-- Index for similarity search
CREATE INDEX IF NOT EXISTS user_memories_embedding_idx ON user_memories
  USING hnsw (embedding vector_cosine_ops);

-- RPC for similarity search
CREATE OR REPLACE FUNCTION match_memories (
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  p_workspace_id int
)
RETURNS TABLE (
  id uuid,
  content text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    user_memories.id,
    user_memories.content,
    1 - (user_memories.embedding <=> query_embedding) AS similarity
  FROM user_memories
  WHERE user_memories.workspace_id = p_workspace_id
    AND 1 - (user_memories.embedding <=> query_embedding) > match_threshold
  ORDER BY user_memories.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
