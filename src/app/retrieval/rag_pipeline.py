from router import create_appropriate_context
import openai 

"""
This code stitches everything to build the rag pipeline
query -> router -> search -> context -> llm -> result 
"""

def rag_pipeline(query):
    llm = openai.OpenAI(
        base_url=f"http://localhost:1234/v1",
        api_key="not-needed",
        timeout=600
    )

    # Step 1: Route the query
    chapter_context, summary_context= create_appropriate_context(query, "final_chunk", llm)

    response = ""
    if chapter_context == "Cannot interpret your question. Please provide a valid query.":
        response = chapter_context
    else:
    # Step 2: Generate response using RAG
        PROMPT_TEMPLATE = f"""You are an expert assistant answering questions strictly using the provided context passages.

            Below are two types of context(One of them may be empty):

            ------------------------------------------------------------
            CHAPTER_CONTEXT  
            (The paragraphs below appear in the exact narrative order of the Mahabharata.  
            Treat earlier paragraphs as occurring before later ones.)
            {chapter_context}

            ------------------------------------------------------------
            SUMMARY_CONTEXT  
            (These paragraphs contain concise explanations.  
            Treat earlier paragraphs as higher-level summaries and later paragraphs as details.)
            {summary_context}
            ------------------------------------------------------------

            INSTRUCTIONS:
            1. Read **all paragraphs** in both CHAPTER_CONTEXT and SUMMARY_CONTEXT. 
            2. If CHAPTER_CONTEXT is empty answer only using SUMMARY_CONTEXT
            3. If SUMMARY_CONTEXT is empty answer only using CHAPTER_CONTEXT
            4. Treat the paragraphs **as ordered sequences** — earlier paragraphs give earlier events, later paragraphs continue the narrative.
            5. Use the meaning of **each paragraph**; do not rely on only the first or last.
            6. Answer **only** using information found directly in the provided contexts.
            7. If the answer is not explicitly supported by the context, say:  
            "**Sorry I don't have this information.**"
            8. Do not add outside knowledge, interpretations, mythology, or assumptions.

            Now answer the user question below using ONLY the context above:

            Question: {query}
            """
    

        response = llm.chat.completions.create(
            model="local-model",  # or your server's model
            messages=[
                {"role": "user", "content": PROMPT_TEMPLATE}
            ],
        temperature=0.7  
        ).choices[0].message.content
        

    return response


if __name__ == "__main__":
    test_query = "How was Drona Killed?"
    answer = rag_pipeline(test_query)
    print("RAG Pipeline Answer:\n", answer)