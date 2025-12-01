from utils import DocumentsCol, DocType
import pandas as pd


"""
This code builds the follwoing
1. chapter_context:
    This is text from `document_type` = content_chunk concatinated
    together but ordered by chapter_no and chunk_no as order to chapter
    chunk is important.
2. summary_context:
    This is text from `document_type` = summary_chunk concatinated.
    Their order isn't imporatant here.

It then returns a tuple
"""

def build_context(df, col_name):
    chapter_context = ""
    summary_context = ""

    # Filter context chunk and summary chunk
    content_chunk_df = df[df[DocumentsCol.doc_type.value] == DocType.c_type.value]
    summary_chunk_df = df[df[DocumentsCol.doc_type.value] == DocType.s_type.value]

    # reorder context chunks based on metadata.
    # order by chapter no and chunk no within chapter
    if not content_chunk_df.empty:
        # content_chunk_df['chapter_no'] = content_chunk_df.to_numeric(content_chunk_df[DocumentsCol.metadata.value].str.extract(r"'chapter_no': '(\d+)'")[0])
        # content_chunk_df['chunk_no'] = content_chunk_df.to_numeric(content_chunk_df[DocumentsCol.metadata.value].str.extract(r"'chunk_no': '(\d+)'")[0])
        content_chunk_df['chapter_no'] = pd.to_numeric(
            content_chunk_df[DocumentsCol.metadata.value].str.extract(r"'chapter_no': '(\d+)'")[0]
        )

        content_chunk_df['chunk_no'] = pd.to_numeric(
            content_chunk_df[DocumentsCol.metadata.value].str.extract(r"'chunk_no': '(\d+)'")[0]
        )
        content_chunk_df_sorted = content_chunk_df.sort_values(['chapter_no', 'chunk_no']).reset_index(drop=True)

        chapter_context = content_chunk_df_sorted[col_name].str.cat(sep='\n\n')

    if not summary_chunk_df.empty:
        summary_context = summary_chunk_df[col_name].str.cat(sep='\n\n')


    return (chapter_context, summary_context)



    
                
    