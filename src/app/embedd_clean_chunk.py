from sentence_transformers import SentenceTransformer
import psycopg2
import logging

"""
This code embedds the clean_chunk.
"""

logging.basicConfig(level=logging.INFO)
model = SentenceTransformer("BAAI/bge-base-en-v1.5")  

def get_embedding(text):
    # Returns a list of floats
    return model.encode(text, normalize_embeddings=True).tolist()

def update_embeddings(batch_size=100):
    conn = psycopg2.connect(
        host="localhost",
        port=6543,
        user="myuser",
        password="mypassword",
        dbname="mahabharat_db"
    )

    try:
        with conn.cursor() as cursor:
            # Fetch rows without embeddings
            cursor.execute("SELECT id, clean_chunk FROM documents WHERE embedding IS NULL")
            rows = cursor.fetchall()
            logging.info(f"Found {len(rows)} rows to embed.")

            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                updates = []
                for row in batch:
                    doc_id, text = row
                    emb = get_embedding(text)  # compute embedding
                    updates.append((emb, doc_id))

                # Update in batch
                cursor.executemany(
                    "UPDATE documents SET embedding = %s WHERE id = %s",
                    updates
                )
                conn.commit()
                logging.info(f"Updated batch {i // batch_size + 1} ({len(batch)} rows)")

    finally:
        conn.close()
        logging.info("Database connection closed.")


if __name__ == "__main__":
    update_embeddings()