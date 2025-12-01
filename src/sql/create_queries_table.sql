-- Table to store validation questions
CREATE TABLE IF NOT EXISTS queries (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    query_type TEXT NOT NULL -- e.g., 'motivation', 'summary', 'spatial', 'other'
);