
"""
This function just rectifies the query if worded wrongly 
or returns "Cannot interpret your question." if the query 
is non-sense or delulu.
"""
def query_rectifier(query: str, llm):
    print("Rectifying query:", query)
    prompt = f"""You are a Query Rectifier. Your job is to rewrite a user's query into a clear, meaningful question.

            Decision Rules:
            1. MODIFY THE QUERY WHEN:
            - Spelling/grammar errors that change meaning
            - Incomplete phrases or fragmented questions
            - Poor phrasing that makes the query unclear
            - Ambiguous but salvageable queries

            2. KEEP QUERY UNCHANGED WHEN:
            - Already clear and well-formed
            - Proper names/terms are correctly spelled
            - Specific technical terms are used properly
            - The query is coherent and meaningful as-is

            3. OUTPUT "Cannot interpret your question." WHEN:
            - Not in English
            - Completely nonsensical or random words
            - No coherent meaning can be inferred
            - Mixed languages without clear context
            - Gibberish or random characters
            - Empty or single unrelated words

            Do NOT answer the question or provide any explanations.
            OUTPUT ONLY the unchanged question, improved question, or "Cannot interpret your question."

            QUERY: {query}
            """
    response = llm.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8192
    )

    rectified_query = response.choices[0].message.content.strip()
    return rectified_query

def detect_summary_questions(query, llm):
    print("Detecting if query asks for summary:", query)

    prompt = f"""
        You are an assistant that converts natural language questions into a concise "Summarize <Topic>" form **if the question is asking for a summary**. 

        Instructions:
        1. If the user query is asking for a summary of a topic, rephrase it as "Summarize <Topic>".
        2. Extract the main topic from the query.
        3. Ignore extra words, examples, or filler phrases.
        4. If the query is not a summary question, LEAVE IT UNCHANGED.
        5. Always output only the final rephrased query or the original if not a summary question.

        Examples:
        - Input: "Describe the events in Adi Parva"
        Output: "Summarize Adi Parva"

        - Input: "What happened in Adi Parva?"
        Output: "Summarize Adi Parva"

        - Input: "Give a brief summary of the Mahabharata war"
        Output: "Summarize Mahabharata war"

        - Input: "Explain the main points of the Bhagavad Gita"
        Output: "Summarize Bhagavad Gita"

        - Input: "Who are the main characters in Adi Parva?"
        Output: "Who are the main characters in Adi Parva?"

        Now, rephrase the following query in the same format:
        "{query}"
    """

    response = llm.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8192
    )

    new_query = response.choices[0].message.content.strip()
    return new_query