from keyword_search import keyword_search
from build_context import build_context
from utils import DocumentsCol
from hybrid_search import hybrid_search
from query_engineering import query_rectifier, detect_summary_questions
from utils import tokenize_into_words

"""
This function take the query then
1. Checks for sanity
2. Checks if its a summary question
    a. If its summary question just utilizes BM25 based on certain keyword
    b. If not goes to full hybrid search
3. Does hybrid search

It returns a tuple.
"""

def create_appropriate_context(query: str, col_name, llm):
    # rectify query
    query = query_rectifier(query, llm)
    low_query = query.strip().lower()
    no_pass_query = "Cannot interpret your question.".lower()

    df = None
    if low_query == no_pass_query:
        return ("Cannot interpret your question. Please provide a valid query.",-1)
    else:
        new_query = detect_summary_questions(low_query, llm).lower()
        word_tokens = tokenize_into_words(new_query)
        print(word_tokens)
        if ("summary" in word_tokens or "summarize" in word_tokens or "summarization" in word_tokens) and "parva" in word_tokens:
            df = keyword_search(new_query, 8)
            df = df.rename(columns={DocumentsCol.en_chunk.value: col_name})
        else:
            #hybrid search
            df = hybrid_search(query, col_name)
    return build_context(df, col_name)
    
        
