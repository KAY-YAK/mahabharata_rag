-- Table to store the results of LLM-as-Judge evaluation
CREATE TABLE IF NOT EXISTS evaluations (
    query_id UUID,
    chunk_id UUID,
    clean_chunk_label SMALLINT,
    clean_chunk_llama SMALLINT, -- 0 or 1
    clean_chunk_gemma SMALLINT,
    clean_chunk_mistral SMALLINT,
    enriched_chunk_label SMALLINT,
    enriched_chunk_llama SMALLINT, -- 0 or 1
    enriched_chunk_gemma SMALLINT,
    enriched_chunk_mistral SMALLINT
    PRIMARY KEY (query_id, chunk_id)
);