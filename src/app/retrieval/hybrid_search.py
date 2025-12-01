from keyword_search import keyword_search
from semantic_search import semantic_search
from utils import DocumentsCol, SEMANTIC_SQL_PATH
import numpy as np
import warnings
import pandas as pd

"""
This code implements hybrid search using
    1. semantic_search function
    2. keyword_search function (BM25 search)
"""

warnings.filterwarnings("ignore")

def hybrid_search(query, score_col_name):
    print("Hybrid Search for Query:", query)
    df_semantic = semantic_search(query, SEMANTIC_SQL_PATH)
    df_keyword = keyword_search(query, 20)

    # print(len(df_semantic))
    # print(len(df_keyword))

    semantic_marker = '_semantic'
    keyword_marker = '_keyword'

    # Join the dataframes on the 'id' column
    df_hybrid = pd.merge(df_semantic, df_keyword, on=DocumentsCol.id.value,how='outer', suffixes=(semantic_marker, keyword_marker))

    # print(df_hybrid)
    # Combine the chunks, doc_type, and metadata columns

    df_hybrid_semantic_na = df_hybrid[df_hybrid[DocumentsCol.c_chunk.value].isna()]
    df_hybrid_keyword_na = df_hybrid[df_hybrid[DocumentsCol.en_chunk.value].isna()]
    df_hybrid_both_chunk_not_na = (df_hybrid[df_hybrid[DocumentsCol.c_chunk.value].notna() & df_hybrid[DocumentsCol.en_chunk.value].notna()])

    df_hybrid_semantic_na[score_col_name] = df_hybrid_semantic_na[DocumentsCol.en_chunk.value]
    df_hybrid_semantic_na[DocumentsCol.metadata.value] = df_hybrid_semantic_na[DocumentsCol.metadata.value + keyword_marker]
    df_hybrid_semantic_na[DocumentsCol.doc_type.value] = df_hybrid_semantic_na[DocumentsCol.doc_type.value + keyword_marker]

    df_hybrid_keyword_na[score_col_name] = df_hybrid_keyword_na[DocumentsCol.c_chunk.value]
    df_hybrid_keyword_na[DocumentsCol.metadata.value] = df_hybrid_keyword_na[DocumentsCol.metadata.value + semantic_marker]
    df_hybrid_keyword_na[DocumentsCol.doc_type.value] = df_hybrid_keyword_na[DocumentsCol.doc_type.value + semantic_marker]

    df_hybrid_both_chunk_not_na[score_col_name] = df_hybrid_both_chunk_not_na[DocumentsCol.en_chunk.value]
    df_hybrid_both_chunk_not_na[DocumentsCol.metadata.value] = df_hybrid_both_chunk_not_na[DocumentsCol.metadata.value + semantic_marker]
    df_hybrid_both_chunk_not_na[DocumentsCol.doc_type.value] = df_hybrid_both_chunk_not_na[DocumentsCol.doc_type.value + semantic_marker]

    df_hybrid_final = pd.concat(
        [
            df_hybrid_semantic_na,
            df_hybrid_keyword_na,
            df_hybrid_both_chunk_not_na
        ],
        ignore_index=True   # optional: resets the index
    )

    return df_hybrid_final[[DocumentsCol.id.value,
                           DocumentsCol.doc_type.value,
                           DocumentsCol.metadata.value,
                           score_col_name]]
    
