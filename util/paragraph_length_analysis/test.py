import re

def final_semantic_chunking(text, target_chunk_size=1800):
    """
    A robust chunking strategy that prioritizes semantic blocks.
    1. Protects [] content.
    2. Identifies and protects large, atomic blocks (like lists).
    3. Splits by paragraph.
    4. Combines paragraphs into chunks of a target size.
    5. Restores all protected content.
    """
    all_placeholders = {}
    safe_text = text
    placeholder_counter = 0

    # --- Stage 1: Protect All Atomic Content ---

    # 1a. Protect the original [] footnotes
    protected_content = re.findall(r'\[.*?\]', text, flags=re.DOTALL)
    for content in protected_content:
        placeholder = f"__PROTECTED_{placeholder_counter}__"
        all_placeholders[placeholder] = content
        safe_text = safe_text.replace(content, placeholder, 1)
        placeholder_counter += 1

    # 1b. Find and protect large semantic blocks (like the list of names)
    # We find them in the original text to get their full content, then replace in safe_text
    semantic_blocks = re.findall(list_pattern, text)
    for block in semantic_blocks:
        # Only treat it as a special block if it's reasonably large
        if len(block) > target_chunk_size / 2:
            placeholder = f"__SEMANTIC_BLOCK_{placeholder_counter}__"
            all_placeholders[placeholder] = block
            # We must replace the block in the safe_text, not the original text
            # So we find the corresponding block in safe_text and replace it
            safe_text = safe_text.replace(block, placeholder, 1)
            placeholder_counter += 1

    # --- Stage 2: Chunk the "Safe" Text ---

    # 2a. Split by paragraph
    paragraphs = [p.strip() for p in safe_text.split('\n\n') if p.strip()]

    # 2b. Combine paragraphs into chunks of target size
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) > target_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    # --- Stage 3: Restore All Protected Content ---
    final_chunks = []
    for chunk in chunks:
        restored_chunk = chunk
        for placeholder, content in all_placeholders.items():
            restored_chunk = restored_chunk.replace(placeholder, content)
        final_chunks.append(restored_chunk)
        
    return final_chunks
