import json
import os
from openai import OpenAI

# Local LM Studio Client
CLIENT = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed",
    timeout=600
)

# Prompt Template


# Questiion types
QUESTION_TYPES = [
    "factual", "summary", "moral", "causal", "procedural",
    "temporal", "spatial", "motivation", "relationship", "dialogue"
]

def generate_questions(passage: str):
    prompt =  f"""
        You are a question generation assistant.

        You will receive a passage from the Mahabharata. 
        Based on the content of the passage, generate questions ONLY if they can be answered 
        using the passage alone. If a question type is not possible from this passage, output 
        an empty string for that field.

        DO NOT create hypothetical questions.
        DO NOT create multi-hop questions that require information outside the passage.
        DO NOT infer events not explicitly described or strongly implied.

        For each category, generate AT MOST one question.

        Output STRICTLY in JSON with the following schema:

        {{
        "factual": "",
        "summary": "",
        "moral": "",
        "causal": "",
        "procedural": "",
        "temporal": "",
        "spatial": "",
        "motivation": "",
        "relationship": "",
        "dialogue": ""
        }}

        Category definitions:

        - factual: Question direct fact from the passage (who, what, when, where, numbers, etc.)
        - summary: A request question to summarize the passage.
        - moral: Ethical or philosophical lesson question explicitly shown or implied.
        - causal: Question about Why something in this passage happened.
        - procedural: Question about how something happened (step-by-step if present).
        - temporal: Question about when something occurred (sequence or time info).
        - spatial: Question about where something occurred.
        - motivation: Question about why a character acted a certain way.
        - relationship: Question about how characters relate to each other.
        - dialogue: Question about identifying who said something, or what someone said.

        Again:
        If the passage does not contain enough information for a category, leave that question field as "".

        Now here is the passage:
        ---
        {passage}
        ---
        """
    response = CLIENT.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048,   
        stream=False
    )

    raw = response.choices[0].message.content

    # Clean JSON
    raw = raw.strip("`\n ")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("LLM returned non-JSON for passage:")
        print(raw)
        return None

    return data


def process_passage(passage: str):
    data = generate_questions(passage)
    if not data:
        return

    for qt in QUESTION_TYPES:
        q = data.get(qt, "").strip()
        if q:
            aggregated_questions[qt].add(q)


def read_passages_from_folder(folder_path: str):
    passages = []

    for fname in os.listdir(folder_path):
        if fname.lower().endswith(".txt"):
            full_path = os.path.join(folder_path, fname)
            with open(full_path, "r", encoding="utf-8") as f:
                passages.append(f.read().strip())
    
    return passages



def save_questions(output_dir="questions_output"):
    os.makedirs(output_dir, exist_ok=True)

    for qt in QUESTION_TYPES:
        file_path = os.path.join(output_dir, f"{qt}_questions.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            for q in sorted(aggregated_questions[qt]):
                f.write(q + "\n")

    print(f"\nSaved all questions to: {output_dir}")



if __name__ == "__main__":

    source_folder = r"C:\Users\optim\OneDrive\Documents\GitHub\mahabharata_rag\data_for_questions" 
    destination_folder = r"C:\Users\optim\OneDrive\Documents\GitHub\mahabharata_rag\generated_questions"

    passages = read_passages_from_folder(source_folder)
    print(f"Loaded {len(passages)} passages from {destination_folder}")

    aggregated_questions = {qt: set() for qt in QUESTION_TYPES}

    for p in passages:
        data = generate_questions(p)
        for qt in QUESTION_TYPES:
            print(qt)
            q = data.get(qt, "").strip()
            if q:
                aggregated_questions[qt].add(q)

    save_questions(destination_folder)
