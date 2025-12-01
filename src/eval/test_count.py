import psycopg2
import tiktoken
from deepseek_tokenizer import DeepSeekTokenizer
# from zhipuai_tokenizer import ZhipuTokenizer

conn = psycopg2.connect(
        host="localhost",
        port=6543,
        user="myuser",
        password="mypassword",
        dbname="mahabharat_db")

cur = conn.cursor()


# 2. Fetch chunks from DB
cursor = conn.cursor()
cursor.execute("SELECT clean_chunk, enriched_chunk FROM documents;")
rows = cursor.fetchall()

clean_chunks = [r[0] for r in rows if r[0]]
enriched_chunks = [r[1] for r in rows if r[1]]

print(f"Loaded {len(clean_chunks)} clean chunks and {len(enriched_chunks)} enriched chunks")

# GPT-5 tokenizer (same as gpt-4o tokenizer)
enc_gpt5 = tiktoken.encoding_for_model("gpt-4o-mini")

def avg_tokens_gpt5(chunks):
    toks = [len(enc_gpt5.encode(c)) for c in chunks]
    return sum(toks) / len(toks)

print("GPT-5 avg clean tokens:", avg_tokens_gpt5(clean_chunks))
print("GPT-5 avg enriched tokens:", avg_tokens_gpt5(enriched_chunks))

# DeepSeek tokenizer

enc_ds = tiktoken.get_encoding("deepseek")

def avg_tokens_deepseek(chunks):
    toks = [len(enc_ds.encode(c)) for c in chunks]
    return sum(toks) / len(toks)

print("DeepSeek avg clean tokens:", avg_tokens_deepseek(clean_chunks))
print("DeepSeek avg enriched tokens:", avg_tokens_deepseek(enriched_chunks))




# zai_tokenizer = ZhipuTokenizer.from_pretrained("glm-4-tokenizer")

# def avg_tokens_zai(chunks):
#     toks = [len(zai_tokenizer.encode(c)) for c in chunks]
#     return sum(toks) / len(toks)

# print("ZAI avg clean tokens:", avg_tokens_zai(clean_chunks))
# print("ZAI avg enriched tokens:", avg_tokens_zai(enriched_chunks))
