import numpy as np
import requests
from tqdm import tqdm
import pandas as pd
from enum import Enum
import numpy as np
import openai
from sentence_transformers import CrossEncoder
from insert_into_queries import conn
from insert_into_evaluations import insert_into_evaluations
from psycopg2.extras import execute_values

class ModelNames(Enum):
    llama = "meta-llama-3.1-8b-instruct"
    gemma = "google/gemma-2-9b"
    mistral = "mistral-7b-instruct-v0.1"

class QueriesCol(Enum):
    q_id = "query_id"
    text = "query_text"

class DocumentsCol(Enum):
    c_id = "id"
    c_chunk = "clean_chunk"
    en_chunk = "enriched_chunk"

class EvaluationsCol(Enum):
    c_chunk_llama = "clean_chunk_llama_label"
    c_chunk_gemma = "clean_chunk_gemma_label"
    c_chunk_mistral = "clean_chunk_mistral_label"
    en_chunk_llama = "enriched_chunk_llama_label"
    en_chunk_gemma = "enriched_chunk_gemma_label"
    en_chunk_mistral = "enriched_chunk_mistral_label"

client = openai.OpenAI(
    base_url=f"http://localhost:1234/v1",
    api_key="not-needed",
    timeout=600
)

def create_prompt(query, doc):

    return f"""You are an expert document analyst. Your task is to judge whether a given document contains sufficient information to directly answer a query.

    Instructions:

    Analyze the query and the document carefully.
    Determine if the document provides a direct, specific, and complete answer to the query.
    Your judgment must be based ONLY on the information within the provided document.
    Respond with ONLY "YES" or "NO" - no explanations, no additional text.
    Evaluation Criteria:
    Answer "YES" only if:

    The document explicitly states the answer to the query.
    The document contains all the specific facts, names, or details needed to formulate a direct answer.
    The information is clearly present and does not require external knowledge.
    Answer "NO" if:

    The document does not contain the information needed to answer the query.
    The document only mentions the topic of the query tangentially, without providing the specific answer.
    The information is too general or vague to answer the query directly.
    Answering the query would require knowledge not present in the document.
    Input Format:
    QUERY: {query}

    DOCUMENT: {doc}

    Output Format:
    YES or NO (Only use these two tokensto reply dont add period or anything)
    """

def data_for_cross_encoder():
    # Extract column names from enums
    query_cols = ",".join([col.value for col in QueriesCol])
    chunk_cols = ",".join([col.value for col in DocumentsCol])

    queries_df = pd.read_sql(f"SELECT {query_cols} FROM queries limit 100", conn)
    chunks_df = pd.read_sql(f"SELECT {chunk_cols} FROM documents limit 1", conn)

    # CROSS JOIN using dummy keys
    queries_df["__tmp"] = 1
    chunks_df["__tmp"] = 1
    df = pd.merge(queries_df, chunks_df, on="__tmp").drop(columns="__tmp")

    return df    


def insert_batch_to_db(df_chunk, table_name="evaluations"):
    """
    Insert batch results into PostgreSQL database without conflict handling.
    """
    try:
        cursor = conn.cursor()

        # Columns we want to insert
        insert_cols = [
            QueriesCol.q_id.value,
            DocumentsCol.c_id.value,
            EvaluationsCol.c_chunk_llama.value,
            EvaluationsCol.c_chunk_gemma.value,
            EvaluationsCol.c_chunk_mistral.value,
            EvaluationsCol.en_chunk_llama.value,
            EvaluationsCol.en_chunk_gemma.value,
            EvaluationsCol.en_chunk_mistral.value
        ]

        df = df_chunk[insert_cols]
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2000)  # avoid line wrapping

        print(df)  # or df_chunk
        

        # # Convert DataFrame to list of tuples
        # values = list(df_chunk[insert_cols].itertuples(index=False, name=None))

        # # Build simple INSERT statement
        # insert_query = f"""
        # INSERT INTO {table_name} ({', '.join(insert_cols)})
        # VALUES %s
        # """

        # execute_values(cursor, insert_query, values)
        # conn.commit()

        # print(f"Inserted {len(values)} rows into {table_name}")

    except Exception as e:
        conn.rollback()
        raise Exception(f"Error inserting batch into database: {e}")

# ---------------------------------------------------------
# LLM Call 
# ---------------------------------------------------------
def call_llm(prompt, model_name):

    resp = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=20
    )

    full_text = resp.choices[0].message.content.strip()
    final_token = full_text.splitlines()[-1].strip()
    
    return final_token

# ---------------------------------------------------------
# Process the DataFrame in batches
# ---------------------------------------------------------
def process_in_batches(df, batch_size=100):
    # Split into batch-size chunks
    splits = np.array_split(df, max(1, len(df) // batch_size))

    # for df_chunk in tqdm(splits, desc=f"Processing..."):
    for df_chunk in splits:
        res  = []
        for _, row in df_chunk.iterrows():
            models  = [ModelNames.llama.value, ModelNames.gemma.value, ModelNames.mistral.value]
            c_prompt = create_prompt(row[QueriesCol.text.value], row[DocumentsCol.c_chunk.value])
            en_prompt = create_prompt(row[QueriesCol.text.value], row[DocumentsCol.en_chunk.value])
            c_chunk_scores = [ call_llm(c_prompt, model) for model in models ]
            en_chunk_scores = [ call_llm(en_prompt, model) for model in models ]
            tup = tuple([getattr(row, QueriesCol.q_id.value), getattr(row,DocumentsCol.c_id.value)] + c_chunk_scores + en_chunk_scores)
            res.append(tup)
        for x in res:
            print(x)
        insert_into_evaluations(res)





if __name__ == "__main__":
    try:
        # 1. Get the data
        df_to_process = data_for_cross_encoder()
        
        # 2. Process it in batches and write to DB
        # The model_name argument here is not actually used inside process_in_batches
        # since you loop through all models. You could remove it if you want.
        process_in_batches(df_to_process, batch_size=100)
        
        print("All batches processed successfully.")

    except Exception as e:
        raise Exception(f"An error occurred during the main process: {e}")

    finally:
        # 3. Close the connection ONCE at the very end of the script
        if conn:
            conn.close()
            print("Database connection closed.")


