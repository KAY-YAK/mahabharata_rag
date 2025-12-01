-- For Semantic (Vector) Search
-- Uses the HNSW algorithm for fast Approximate Nearest Neighbor search.
-- vector_l2_ops is the operator class for the <=> (L2 distance) operator.
CREATE INDEX idx_documents_embedding ON documents USING hnsw (embedding vector_l2_ops);

-- A standard B-tree index on specific JSONB keys.
-- This makes filtering by chapter_no extremely fast.
CREATE INDEX idx_documents_metadata_chapter ON documents USING btree ((metadata ->> 'chapter_no'));

