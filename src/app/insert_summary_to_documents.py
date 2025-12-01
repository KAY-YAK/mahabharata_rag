
import os
import re
from psycopg2.extras import Json
from chunk_and_insert_into_documents import DocType
from chunk_and_insert_into_documents import insert_into_documents, tokenize_into_words

"""
This code reads summary data and inserts it into database.
"""

def chunk_to_row(text, filename):
    rows = []
    metadata = {}
    pattern = re.compile(r"^([A-Za-z]+)_(.+)_summary\.txt$")

    matches = pattern.match(filename)

    eighteen_parva = matches.group(1)
    hun_parva = matches.group(2)
    metadata["parva_eighteen_name"] = eighteen_parva

    if (hun_parva == "Parva"):
        metadata["parva_hundred_name"] = ""
    else:
        metadata["parva_hundred_name"] = hun_parva

    metadata["chunk_no"] = "1"
    metadata["parva_summary"] = True

    text_tokens = tokenize_into_words(text)
    # for summary BM25, the clean_text and the enriched_text is the same 
    rows.append((DocType.SUMMARY_CHUNK.value, text, text, Json(metadata), text_tokens, None))
    
    return rows


if __name__ == "__main__":

    folder = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\data_summary"
    data = []

    # Step 1 :: Read from data folder
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            filepath = os.path.join(folder, file)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
                rows = chunk_to_row(text, file)
                print(f"Chunk from {file} = {len(rows)}")

                data += rows

    # Step 6 :: Insert into postgres
    insert_into_documents(data)