import requests
import openai
import urllib.parse
import os
import pandas as pd
import numpy as np
from enum import Enum
from insert_into_queries import conn
from insert_into_evaluations import insert_into_evaluations


class QueriesCol(Enum):
    q_id = "query_id"
    text = "query_text"

class DocumentsCol(Enum):
    c_id = "id"
    c_chunk = "clean_chunk"
    en_chunk = "enriched_chunk"



def data_for_judge_llm():
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

import json

def create_jsonl_lines(df, out_dir, output_file_suffix,batch_size):

    num_rows = len(df)

    splits = []

    for start in range(0, num_rows, batch_size):
        end = start + batch_size
        splits.append(df.iloc[start:end])
    
    start = 1
    for df_chunk in splits:
        dumps = []
        for _, row in df_chunk.iterrows():
            json_line = {
                "custom_id": f"{row[QueriesCol.q_id.value]}_{row[DocumentsCol.c_id.value]}",
                "method": "POST",
                "url": "/v1/responses",
                "body": {
                    "model": "gpt-4.1-nano",
                    "input": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert document analyst. Your task is to determine whether a document "
                                "contains sufficient information to directly answer a given query.\n\n"
                                "Instructions:\n"
                                "1. Analyze the QUERY against the DOCUMENT carefully.\n"
                                "2. Decide \"YES\" if the DOCUMENT fully answers the QUERY; otherwise \"NO\".\n"
                                "3. Assign a confidence score from 0 to 1 indicating your confidence in the answer.\n"
                                "4. Respond ONLY in strict JSON format like:\n"
                                "{\n"
                                "  \"answer\": \"YES\" or \"NO\",\n"
                                "  \"score\": 0.0 to 1.0\n"
                                "}\n"
                                "5. Do not include any explanation or extra text."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"QUERY:\n{row[QueriesCol.text.value]}\n\n"
                                f"DOCUMENT:\n{row[DocumentsCol.c_chunk.value]}"
                            )
                        }
                    ],
                    "temperature": 0,
                    "max_output_tokens": 100
                }
            }

            dumps.append(json.dumps(json_line, ensure_ascii=False))
        end = start + batch_size - 1
        output_file = output_file_suffix + "_" + str(start) + "_" + str(end) +".jsonl"
        file_path = os.path.join(out_dir, output_file)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(dumps))
        start = end + 1



if __name__ == "__main__":
    out_dir = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\src\eval\jsonl_files\requests"
    output_file_suffix = "gpt_4_1_nano_requests"
    
    print("Preparing data for LLM judge...")
    df = data_for_judge_llm()
    print(f"Total rows to process: {len(df)}")
    
    print("Creating JSONL files...")
    create_jsonl_lines(df, out_dir, output_file_suffix, 2000)
    
    print("JSONL files created successfully.")
