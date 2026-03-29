-- Step 1: Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create the conditions table
CREATE TABLE IF NOT EXISTS conditions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    condition_name TEXT NOT NULL UNIQUE,
    category TEXT,
    symptoms TEXT[],
    causes TEXT[],
    dosha TEXT[],
    samprapti TEXT,
    diagnosis_logic TEXT,
    treatment_principles TEXT[],
    diet TEXT[],
    lifestyle TEXT[],
    herbs TEXT[],
    formulations TEXT[],
    search_text TEXT,
    ai_content JSONB,
    embedding VECTOR(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Step 3: Create GIN index for Full-Text Search on search_text
CREATE INDEX IF NOT EXISTS idx_conditions_search_text ON conditions USING GIN (to_tsvector('english', COALESCE(search_text, '')));

-- Step 4: Create IVFFlat or HNSW index for Vector Search (for scalability)
-- Using HNSW for better performance on similarity searches
CREATE INDEX IF NOT EXISTS idx_conditions_embedding ON conditions USING hnsw (embedding vector_cosine_ops);
