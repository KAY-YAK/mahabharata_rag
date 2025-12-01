import urllib.parse
import os
from enum import Enum
from sentence_transformers import SentenceTransformer
import spacy

"""
Config, Enums, Model Config etc are stored here
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 6543,
    "user": "myuser", 
    "password": "mypassword",
    "dbname": "mahabharat_db"
}

# USe your own client config
ngrok_url = "https://consumedly-chronogrammatical-marlin.ngrok-free.dev"
passwd = os.getenv("ngrok_desktop_llm")
passwd = urllib.parse.quote(passwd,safe="")
CLIENT_CONFIG = {
    "base_url":f"https://admin:{passwd}@consumedly-chronogrammatical-marlin.ngrok-free.dev/v1",
    "api_key":"not-needed",
    "timeout":600
}

BM25_INDEX_PATH = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\src\app\retrieval\bm25_index.pkl"


SEMANTIC_SQL_PATH = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\src\app\retrieval\semantic.sql"

class DocumentsCol(Enum):
    #actual columns
    id = "id"
    c_chunk = "clean_chunk"
    en_chunk = "enriched_chunk"
    doc_type = "document_type"
    metadata = "metadata"
    embedding = "embedding"
    # derived column
    semantic_score = "semantic_score" 
    keyword_score = "bm25_score"

class BM25Col(Enum):
    id = "ids"
    bm25 = "bm25"

class DocType(Enum):
    c_type = "content_chunk"
    s_type = "summary_chunk"

semantic_sql_placeholder = "query_embedding"
keyword_sql_placeholder = "query"

nlp = spacy.load("en_core_web_sm")

def read_sql_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_query = file.read()
    return sql_query

model = SentenceTransformer("BAAI/bge-base-en-v1.5") 
def embedd_query(query):
    # Returns a list of floats 
    return model.encode(query, normalize_embeddings=True).tolist()


def tokenize_into_words(text):
    doc = nlp(text.lower())
    
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop        # remove stopwords
        and not token.is_punct      # remove punctuation
        and token.lemma_.isalpha()  # keep words only
    ]
    
    return tokens