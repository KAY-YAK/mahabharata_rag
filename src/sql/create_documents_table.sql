-- First, ensure the pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create Table
CREATE TABLE IF NOT EXISTS documents (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 

    -- Document Content
    document_type TEXT NOT NULL, -- e.g., 'content_chunk', 'summary_chunk'
    clean_chunk TEXT,
    enriched_chunk TEXT,
    
    -- Metadata (flexible and queryable)
    metadata JSONB NOT NULL,

    -- BM25 Search Vector (Generated Automatically)
    -- This column combines text and metadata for fast, weighted keyword search.
    bm25_vector text[],

    -- Semantic Search Vector
    -- IMPORTANT: Change 1536 if you use a different embedding model
    embedding vector(768)

);

