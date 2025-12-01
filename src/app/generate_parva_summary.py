import openai
import os
import re
import copy
import json
from llama_cpp import Llama
from parva_hundred import parva_hundred_dict

"""
This script performs a hierarchical summarization of the Mahabharata text corpus. 
It uses a local Large Language Model (via LM Studio) to condense individual chapters 
into "Sub-Parva" (100 Parva) summaries, and subsequently condenses those 
into "Major Parva" (18 Parva) summaries.


Hierarchical Processing: 
    Implements a two-tier summarization strategy

Bottom-Up: 
    Aggregates individual text files (chapters) to create summaries for Sub-Parvas.

Meta-Summarization: 
    Aggregates Sub-Parva summaries to create high-level summaries for the 18 Major Parvas.

Token-Aware Chunking: 
    Uses llama-cpp-python solely for accurate token counting to ensure the prompt stays within the context window (MAX_TOKEN_LEN).

Rolling Context Window: 
    If a text block exceeds the token limit, the script summarizes the 
    current buffer and appends that summary to the beginning of the next chunk. 
    This ensures context is preserved across large sections of text without losing continuity.

Local LLM Integration: 
    Connects to a local server (LM Studio) via the OpenAI API standard, 
    ensuring privacy and zero cost for heavy processing.
"""

def summarize_text(CLIENT, text: str, output_length):
    """Sends text to the local LLM for summarization."""
    prompt = f"""
        Read the following text and provide a structured and summary.

        Instructions:
        1. Summarize only what is directly provided, using simple words.
        2. Do NOT add external knowledge.
        3. Do NOT speculate about missing text.
        4. Do NOT interpret or translate non-English words unless the text itself defines them.
        5. Mention key events and characters only if they appear in the provided text.
        6. Extract philosophical or moral ideas only if explicitly stated.
        7. The total length (of summary section) must NOT exceed {output_length} words.

        Output Structure:
        **Summary**:
        [Write a brief summary in paragraph(s)]

        **Key events and characters**
        - Bullet points listing the important events and characters mentioned in the text.

        **Philosophical or Moral Ideas**
        - Bullet points listing only the ideas explicitly stated in the text.

        Text to summarize:
        {text}
    """

    print(f"Sending text for summarization (Length: {len(text)} chars)...")

    # Stream the output
    stream = CLIENT.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=8192,
        stream=True
    )

    # Accumulate chunks into one final string
    summary = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            piece = chunk.choices[0].delta.content
            print(piece, end="")  # optional real-time printing
            summary += piece

    print("\n--- Summary Complete ---")
    return summary.strip()


def save_summary_to_file(filename, summary_text):
    """Saves the summary text to a file."""
    # Write the summary to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summary_text)
    f.close()
    
    print(f"Successfully saved summary [{len(summary_text)} chars] to {filename}")

def base_prompt_token_count(tokenizer):
    prompt_text_without_paceholder = f"""
        Read the following text and provide a structured and summary.

        Instructions:
        1. Summarize only what is directly provided, using simple words.
        2. Do NOT add external knowledge.
        3. Do NOT speculate about missing text.
        4. Do NOT interpret or translate non-English words unless the text itself defines them.
        5. Mention key events and characters only if they appear in the provided text.
        6. Extract philosophical or moral ideas only if explicitly stated.
        7. The total length (of summary section) must NOT exceed words.

        Output Structure:
        **Summary**:
        [Write a brief summary in paragraph(s)]

        **Key events and characters**
        - Bullet points listing the important events and characters mentioned in the text.

        **Philosophical or Moral Ideas**
        - Bullet points listing only the ideas explicitly stated in the text.

        Text to summarize:
        """
    
    return get_token_count(tokenizer, prompt_text_without_paceholder)

def init_parva_hundred_dict():
    parva_dict_copy = copy.deepcopy(parva_hundred_dict)

    # init hundred_parva_dict to empty list
    for p_list_dict in parva_dict_copy.values():
        for k in p_list_dict.keys():
            p_list_dict[k] = []
    return parva_dict_copy

def group_files_by_parva(files):
    pattern = re.compile(r"chapter_(\d+)_([a-zA-Z]+)_(.+)_(\d+)_normalized.txt")
    
    parva_file_list_dict = init_parva_hundred_dict()

    for file in files:
        matches = pattern.match(file)
        p_eighteen_name = matches.group(2) 
        p_hundred_name = matches.group(3).replace("_"," ")
        parva_file_list_dict[p_eighteen_name][p_hundred_name].append(file)

    return parva_file_list_dict

def get_token_count(tokenizer, text):
    # Tokenize text
    tokens = tokenizer.tokenize(text.encode("utf-8"))
    return len(tokens)

def summarize_text_hiererchically(client, tokenizer, list_text, output_length):

    # idea is this
    """
    keep adding chapter till spill over 8192
    when spill send to summarize
    then, use summary + chapters till 8192 and summarize again
    keep repeating
    """
    prompt_token_len = base_prompt_token_count(tokenizer)

    summary = ""
    text_for_summary = ""
    tot_token_len = prompt_token_len

    for text in list_text:
        # every text should end with \n
        if not text.endswith("\n"):
            text += "\n"

        # get text token length
        text_token_len = get_token_count(tokenizer, text)

        # try to restrict to MAX_TOKEN_LEN. The llm has 10x more tokens
        if tot_token_len + text_token_len > MAX_TOKEN_LEN:
            # When text itself is more than MAX at start
            if text_for_summary:
                print(f"Summarizing started for {len(text.split(" "))} words, {tot_token_len} tokens")
                summary = summarize_text(client, text, output_length)
            else:
            # summarize
                print(f"Summarizing started for {len(text_for_summary.split(" "))} words, {tot_token_len} tokens")
                summary = summarize_text(client, text_for_summary, output_length)
            # put summary and current text for next summary block
            text_for_summary = summary + "\n" + text
            tot_token_len = prompt_token_len + get_token_count(tokenizer, text_for_summary)
        else:
            text_for_summary += text
            tot_token_len += text_token_len

    if text_for_summary:
        summary = summarize_text(client, text_for_summary, output_length)


    return summary



# --- Example Usage ---
if __name__ == "__main__":
    MAX_TOKEN_LEN = 20000
    # tokenizer
    tokenizer = Llama(
        # model_path="C:\\Users\\rando\\.lmstudio\\models\\bartowski\\Meta-Llama-3.1-8B-Instruct-GGUF\\Meta-Llama-3.1-8B-Instruct-Q4_K_S.gguf",
        model_path="C:\\Users\\optim\\.lmstudio\\models\\bartowski\\Meta-Llama-3.1-8B-Instruct-GGUF\\Meta-Llama-3.1-8B-Instruct-Q4_K_S.gguf",
        vocab_only=True,
        use_mmap=False,
        n_ctx=1,
        verbose=False
    )

    # Point to your local LM Studio server
    client = openai.OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="not-needed",
        timeout = 600
    )

    # source_directory = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\data" 
    # destination_directory = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\data_summary"  

    source_directory = r"C:\Users\optim\OneDrive\Documents\GitHub\mahabharata_rag\data" 
    destination_directory = r"C:\Users\optim\OneDrive\Documents\GitHub\mahabharata_rag\data_summary"  

    files = []

    for file in os.listdir(source_directory):
        if file.endswith(".txt"):
            files.append(file)

    parva_files_grouped_dict = group_files_by_parva(files)

    parva_hundred_summary_dict = init_parva_hundred_dict()

    # get summary for 100 parva
    for parva_eighteen, parva_hundred_list in parva_files_grouped_dict.items():
        for parva_hundred in parva_hundred_list.keys():
            lst_files = parva_hundred_list[parva_hundred]
            print("---------------------------")
            print(lst_files)
            lst_text = []

            # create write file name
            write_file = f"{parva_eighteen}_{parva_hundred}_summary.txt"
            write_path = os.path.join(destination_directory, write_file)
            
            # create list of text(chapter text)
            for read_file in lst_files:
                read_path = os.path.join(source_directory, read_file)
                with open(read_path, "r", encoding="utf-8") as f:
                    lst_text.append(f.read())
            
            summary = summarize_text_hiererchically(client, tokenizer, lst_text, 500)
            parva_hundred_summary_dict[parva_eighteen][parva_hundred] = summary
            print(f"Summarized {parva_hundred} in {len(summary.split())} words")
            
            header = f"Summary of {parva_hundred} parva (under {parva_eighteen} parva)\n\n"
            save_summary_to_file(write_path, header + summary)

    # dump_json_path = r"C:\Users\optim\OneDrive\Documents\GitHub\mahabharata_rag\summary_dump.json"
    # with open(dump_json_path, "w") as f:
    #     json.dump(parva_hundred_summary_dict, f, indent=4)

    print(">> " * 50)
    print(f"Save 100 parva summary text to {destination_directory}\n\n")
    # use the previous dictionary to summerize for 18 parva
    for parva_eighteen, parva_hundred_summary in parva_hundred_summary_dict.items():
        lst_text = []
        for parva_hundred in parva_hundred_summary.keys():
            lst_text.append(parva_hundred_summary_dict[parva_eighteen][parva_hundred])
        summary = summarize_text_hiererchically(client, tokenizer, lst_text, 2000)
        print(f"Summarized {parva_eighteen} in {len(summary.split())} words")
        write_file = f"{parva_eighteen}_Parva_summary.txt"
        write_path = os.path.join(destination_directory, write_file)
        header = f"Summary of {parva_eighteen} parva. This is the summary of main parva, {parva_eighteen} parva.\n\n"
        save_summary_to_file(write_path, header + summary)
    print(">> " * 50)
    print(f"Save 18 parva summary text to {destination_directory}\n\n")
    


                

                



                