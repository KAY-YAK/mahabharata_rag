from insert_into_queries import conn

def insert_into_evaluations(rows):
    with conn.cursor() as cursor:
        # Postgres generates UUID using gen_random_uuid()
        insert_sql = """
        INSERT INTO evaluations (
            query_id UUID,
            chunk_id UUID,
            clean_chunk_llama,
            clean_chunk_gemma,
            clean_chunk_mistral,
            enriched_chunk_llama,
            enriched_chunk_gemma,
            enriched_chunk_mistral
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        cursor.executemany(insert_sql, rows)

    conn.commit()
    print(f"Inserted {len(rows)} rows successfully with DB-generated UUIDs.")








