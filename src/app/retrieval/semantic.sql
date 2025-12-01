SELECT
    id,
    document_type,
    clean_chunk,
    metadata,
    1 - (embedding <=> %(query_embedding)s::vector) AS semantic_score
FROM documents
ORDER BY embedding <=> %(query_embedding)s::vector
LIMIT 50;
