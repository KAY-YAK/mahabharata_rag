from utils import read_sql_file, DB_CONFIG, DocumentsCol, embedd_query, semantic_sql_placeholder
import pandas as pd
import psycopg2

"""
This code implements the semantic search.
"""

def semantic_search(query, sql_path):
    # folder_path = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\src\app\retrieval\semantic.sql"
    print("Semantic Search for Query:", query)
    folder_path = sql_path
    sql_query = read_sql_file(folder_path)
    query_embedding = embedd_query(query)

    conn = psycopg2.connect(**DB_CONFIG)
    results = None
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query, {semantic_sql_placeholder: query_embedding})  # Example embedding
            results = cursor.fetchall()
    except Exception as e:
        conn.close()
        raise RuntimeError(f"Exception:: {e}. \n\n SQL error file path error: {folder_path} or SQL syntax error in file or DB  related issue.")
    finally:
        conn.close()
    
    semantic_df = pd.DataFrame(results, columns=[DocumentsCol.id.value,
                                                 DocumentsCol.doc_type.value,
                                                 DocumentsCol.c_chunk.value,
                                                 DocumentsCol.metadata.value,
                                                 DocumentsCol.semantic_score.value])
    
    return semantic_df