import pandas as pd
from enum import Enum
import numpy as np
from sentence_transformers import CrossEncoder
from insert_into_queries import conn
from insert_into_evaluations import insert_into_evaluations

class QueriesCol(Enum):
    q_id = "query_id"
    text = "query_text"

class DocumentsCol(Enum):
    c_id = "id"
    c_chunk = "clean_chunk"
    en_chunk = "enriched_chunk"

def data_for_cross_encoder():
    # Extract column names from enums
    query_cols = ",".join([col.value for col in QueriesCol])
    chunk_cols = ",".join([col.value for col in DocumentsCol])

    queries_df = pd.read_sql(f"SELECT {query_cols} FROM queries", conn)
    chunks_df = pd.read_sql(f"SELECT {chunk_cols} FROM documents", conn)

    # CROSS JOIN using dummy keys
    queries_df["__tmp"] = 1
    chunks_df["__tmp"] = 1
    df = pd.merge(queries_df, chunks_df, on="__tmp").drop(columns="__tmp")

    return df    

def compute_entailment_probs(logits):
    """Apply softmax to logits and return entailment probability"""
    exp_logits = np.exp(logits - np.max(logits))
    probs = exp_logits / np.sum(exp_logits)
    return probs[2]  # index 2 = entailment

def judge_data(df, batch_size=32, insert_every=256):
    model = CrossEncoder("cross-encoder/nli-deberta-v3-base")

    all_rows = []
    batch_pairs = []
    batch_meta = []

    for row in df.itertuples(index=False):
        query = getattr(row, QueriesCol.text.value)
        c_chunk = getattr(row, DocumentsCol.c_chunk.value)
        en_chunk = getattr(row, DocumentsCol.en_chunk.value)

        # Prepare batch pairs
        batch_pairs.append((query, c_chunk))
        batch_meta.append((getattr(row, QueriesCol.q_id.value), getattr(row, DocumentsCol.c_id.value), 'c'))

        batch_pairs.append((query, en_chunk))
        batch_meta.append((getattr(row, QueriesCol.q_id.value), getattr(row, DocumentsCol.c_id.value), 'en'))

        # Predict when batch is full
        if len(batch_pairs) >= batch_size:
            logits_batch = model.predict(batch_pairs, convert_to_numpy=True)
            for logits, meta in zip(logits_batch, batch_meta):
                prob = compute_entailment_probs(logits)
                q_id, c_id, chunk_type = meta
                if chunk_type == 'c':
                    all_rows.append((q_id, c_id, float(prob), None))
                else:
                    all_rows.append((q_id, c_id, None, float(prob)))

            batch_pairs = []
            batch_meta = []

            # Insert periodically
            if len(all_rows) >= insert_every:
                insert_into_evaluations(all_rows)
                print(f"Inserted {len(all_rows)} rows into evaluations.")
                all_rows = []

    # Final batch
    if batch_pairs:
        logits_batch = model.predict(batch_pairs, convert_to_numpy=True)
        for logits, meta in zip(logits_batch, batch_meta):
            prob = compute_entailment_probs(logits)
            q_id, c_id, chunk_type = meta
            if chunk_type == 'c':
                all_rows.append((q_id, c_id, float(prob), None))
            else:
                all_rows.append((q_id, c_id, None, float(prob)))

    if all_rows:
        insert_into_evaluations(all_rows)

if __name__ == "__main__":
    df = data_for_cross_encoder()
    judge_data(df, batch_size=32, insert_every=1000)
