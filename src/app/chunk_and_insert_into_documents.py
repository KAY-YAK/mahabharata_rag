
import os
import re
import psycopg2
import spacy
import logging
from psycopg2.extras import Json
from enum import Enum
from parva_eighteen import parva_eighteen_dict
from parva_hundred import parva_hundred_dict

"""
This code doe sthe following
1. Reads all the data from the folder [Chapter data enriched with footnotes]
2. It then removes the footnotes with placeholders creating a text and stores 
   this information in a dictionary.
3. Then it takes the above text and breaks it into sentences.
4. Chunks are created taking 1800 charcaters from sentence(s)
5. Enriched chunks are created using the placeholders dictionary
6. Clean chunk and Enriched chunk are then insreted into the database
"""


# Setup logging
logging.basicConfig(level=logging.INFO)
nlp = spacy.load("en_core_web_sm")

conn = psycopg2.connect(
        host="localhost",
        port=6543,
        user="myuser",
        password="mypassword",
        dbname="mahabharat_db")

class DocType(Enum):
    CONTENT_CHUNK = "content_chunk"
    SUMMARY_CHUNK = "summary_chunk"



def footnote_placeholder_parser(text):
    all_placeholders = {}
    protected_content = re.findall(r'\[.*?\]', text, flags=re.DOTALL)
    placeholder_counter = 1
    safe_text = text
    for content in protected_content:
        placeholder = f"__FN_{placeholder_counter}__"
        all_placeholders[placeholder] = content
        safe_text = safe_text.replace(content, placeholder, 1)
        placeholder_counter += 1

    # print(protected_content)
    return (safe_text, all_placeholders)

def sentence_parser(safe_text):
    # MUST DO:: if file doesn't end in \n end with \n to indicate its a paragraph end as new chapter starts
    if not safe_text.endswith("\n"):
        safe_text += "\n"

    base = [".","!","?","..."]
    addition = ["\'","\"","\'\"","\"\'","\'\"\'", "\"\'\"\'", "\"\'\"", "\'\" \'","\" \'"]

    combo = []
    for x in base:
        for y in addition:
            combo.append(x+y)
    # print(combo)

    tot_combo = base + combo
    # print(tot_combo)
    reg_exp = "(" + "|".join(re.escape(p) for p in sorted(tot_combo, key=len, reverse=True)) + r")(\s*)"
    pattern = re.compile(reg_exp)

    parts = pattern.split(safe_text)
    sentences = ["".join(parts[i:i+3]) for i in range(0, len(parts)-1, 3)]

    return sentences

def chunk_text(sentences):
    CHUNKS = []
    chunk = []
    overlap = []

    len_sent = len(sentences)
    i=0

    while i < len_sent:
        sentence = sentences[i]
        sentence_without_placeholder = re.sub(r"__FN_(\d+)__","",sentence)
        
        if len(sentence_without_placeholder) > 1800:
            # what if chunk was nearing 1800 when we encounter this?

            # add overlap last sentence, chunk and sentence as a new chunk
            last_overlap = overlap[-1] if overlap else ""
            CHUNKS.append(" ".join((last_overlap, " ".join(chunk), sentence)))
            
            # add sentence and next sentence as another chunk 
            if i+1 < len_sent:
                curr_sentence = sentences[i+1]
                # CHUNKS.append(" ".join(("OVRLP",sentence, "CHNK", curr_sentence)))
                CHUNKS.append(" ".join((sentence, curr_sentence)))

            # increament loop var
            i = i + 1
                
            # this ABig BigC is added where A is chunk Big is the sentence>1800
            # C is next sentence.  
            overlap = [curr_sentence] 
            
            # empty chunk
            chunk = [] 
            
            continue
        
        chunk_len = len(" ".join(chunk))
        
        if len(sentence_without_placeholder) + chunk_len < 1800:
            chunk.append(sentence)
        else:
            # store chunk in CHUNKS
            overlap_str = "".join(overlap)
            chunk_str = "".join(chunk)
            # lstrip because overlap can be empty at start
            # CHUNKS.append(" ".join(("OVRLP",overlap_str, "CHNK",chunk_str)).lstrip(" "))
            CHUNKS.append("".join((overlap_str, chunk_str)).lstrip(" "))
            
            overlap = []
            
            # create new overlap 
            chars = 0
            for x in reversed(chunk):
                len_x = len(x)
                if chars == 0 and len_x > 200:
                    overlap = [x]
                    chars = len_x
                elif chars + len(x) < 200:
                    overlap = [x] + overlap
                    chars += len_x
                else:
                    break
            # reset chunk to new sentence
            chunk = [sentence]
        i+=1

    # add leftover chunk!!
    if chunk:
        overlap_str = "".join(overlap)
        chunk_str = "".join(chunk)
        CHUNKS.append("".join((overlap_str, chunk_str)))

    return CHUNKS

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

def chunk_to_clean_text_and_en_text(chunks, placeholders, filename):
    rows = []
    clean_chunk = "" 
    en_chunk= ""
    keys = placeholders.keys()

    pattern = re.compile('(' + '|'.join(map(re.escape, keys)) + ')')

    chunk_no = 1
    for chunk in chunks:
        clean_chunk = pattern.sub(lambda m: "", chunk)
        en_chunk = pattern.sub(lambda m: placeholders.get(m.group(0), ""), chunk)
        en_chunk_tokens = tokenize_into_words(en_chunk)
        metadata = generate_basic_metadata(filename)
        metadata["chunk_no"] = str(chunk_no)
        rows.append((DocType.CONTENT_CHUNK.value, clean_chunk, en_chunk, Json(metadata), en_chunk_tokens,None))
        chunk_no+=1
    
    return rows

def generate_basic_metadata(filename):
    pattern = re.compile(r"chapter_(\d+)_([a-zA-Z]+)_(.+)_(\d+)_normalized.txt")

    metadata = {}

    matches = pattern.match(filename)
    p_eighteen_name = matches.group(2)
    p_hundred_name = matches.group(3).replace("_"," ")

    metadata["chapter_no"] = matches.group(1)
    metadata["parva_eighteen_name"] = p_eighteen_name
    metadata["parva_hundred_name"] = p_hundred_name
    # fetch the 18 parva no and 100 parva no form a dictionary

    p_eighteen_no = parva_eighteen_dict[p_eighteen_name]
    p_hundred_no = parva_hundred_dict[p_eighteen_name][p_hundred_name]

    metadata["parva_eighteen_no"] = p_eighteen_no
    metadata["parva_hundred_no"] = p_hundred_no

    return metadata    



def insert_into_documents(rows):
    try:
        with conn.cursor() as cursor:
            # Postgres generates UUID using gen_random_uuid()
            insert_sql = """
            INSERT INTO documents (
                id, document_type, clean_chunk, enriched_chunk, metadata, bm25_vector, embedding
            ) VALUES (
                gen_random_uuid(), %s::text, %s::text, %s::text, %s::jsonb, %s::text[], %s
            )
            """
            cursor.executemany(insert_sql, rows)

        conn.commit()
        print(f"Inserted {len(rows)} rows successfully with DB-generated UUIDs.")

    finally:
        conn.close()

if __name__ == "__main__":

    folder = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\data"
    data = []

    # Step 1 :: Read from data folder
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            filepath = os.path.join(folder, file)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

                # Step 2 :: Get safe text and footnotes dictionary
                safe_text, placeholders = footnote_placeholder_parser(text)

                # Step 3 :: Break safe text into sentences
                sentences = sentence_parser(safe_text)

                # Step 4 :: Create chunks out of sentences
                CHUNKS = chunk_text(sentences)

                # Step 5 :: From chunks, add back footnotes 
                # add metadata, add document type etc and 
                # create list of tuple for the chapter.
                rows = chunk_to_clean_text_and_en_text(CHUNKS, placeholders, file)
                print(f"Chunks from {file} = {len(rows)}")

                data += rows

    # Step 6 :: Insert into postgres
    insert_into_documents(data)
