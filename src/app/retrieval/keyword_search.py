from utils import DB_CONFIG, DocumentsCol, tokenize_into_words, BM25_INDEX_PATH, BM25Col
import pandas as pd
import psycopg2
import pickle

"""
This code does the following
1. Load the invereted index for BM25 from pickle file
2. Tokenizes the query into words (not tokens of LLM)
3. Scores the query against all the chunks using BM25 and 
   returns the data sorted by score.
4. The top `limit` is then selected and the corrosponding
   `id` data is fetched from the database.
5. Data from BM25 and Database is joined on `id`, sorted
   on BM25 score and returned
"""

def keyword_search(query, limit):
    # folder_path = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\src\app\retrieval\keyword.sql"
    print("BM25 Search for Query:", query)

    # Load BM25 index
    print("Loading BM25 index...")
    with open(BM25_INDEX_PATH, "rb") as f:
        bm25_index = pickle.load(f)
    
    bm25 = bm25_index[BM25Col.bm25.value]
    ids = bm25_index[BM25Col.id.value]

    query_tokens = tokenize_into_words(query)
    scores = bm25.get_scores(query_tokens)

    top_idx = scores.argsort()[-limit:][::-1]

    top_ids = [ids[i] for i in top_idx]         # top document IDs
    top_scores = [scores[i] for i in top_idx]   # corresponding BM25 scores

    top_df = pd.DataFrame({
        "id": top_ids,
        "bm25_score": top_scores
    })


    # Connect to DB and fetch documents
    conn = psycopg2.connect(**DB_CONFIG)

    results = None
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, document_type, enriched_chunk, metadata
                FROM documents
                WHERE id = ANY(%s::uuid[])
            """, (top_ids,))
            results = cursor.fetchall()
    except Exception as e:
        conn.close()
        raise RuntimeError(f"Exception:: {e} while fetching ids from documents table")
    finally:
        conn.close()


    docs_df = pd.DataFrame(results, columns=[
        DocumentsCol.id.value,
        DocumentsCol.doc_type.value,
        DocumentsCol.en_chunk.value,
        DocumentsCol.metadata.value
    ])

    
    keyword_df = top_df.merge(docs_df, on="id", how="left")
    keyword_df = keyword_df.sort_values("bm25_score", ascending=False)

    return keyword_df
