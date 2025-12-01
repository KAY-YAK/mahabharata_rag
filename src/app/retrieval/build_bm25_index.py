import psycopg2
import pickle
from rank_bm25 import BM25Okapi
from utils import DB_CONFIG, BM25_INDEX_PATH, BM25Col

"""
This code fetches the records from postgres after its populated fully 
i.e. no more changes are inserted.
It then builds the inverted lookup table for BM25 along with 
the functions of the object and dumps its as a pickle file.

Note that it also stores the id from our database.

WHY?
1. Plugins need installation
2. Plugin ostgres BM25 implementataion are not good enough.
   Have tried https://github.com/tensorchord/VectorChord-bm25, 
   but the models used dilute the document converting them 
   into fixed sized tokens.
3. Implementations on ts_vector are web seacrh at best.
"""


def build_bm25_index():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, bm25_vector FROM documents;")
        rows = cursor.fetchall()
        ids = [row[0] for row in rows]
        corpus = [row[1] for row in rows]  # list of token lists
        bm25 = BM25Okapi(corpus)
    except Exception as e:
        raise RuntimeError(f"Exception:: {e}. \n\n Error building BM25 index from DB.")
    finally:
        conn.close()
    # Save the BM25 index and IDs
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump({BM25Col.bm25.value: bm25, BM25Col.id.value: ids}, f)
    

if __name__ == "__main__":
    build_bm25_index()
    print("BM25 index built and saved.")