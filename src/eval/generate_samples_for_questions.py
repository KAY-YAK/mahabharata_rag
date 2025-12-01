import os
import random
import re
from pathlib import Path

def get_chapter_files(folder_path):
    """Get all chapter files sorted by chapter number"""
    chapter_files = []
    for file in Path(folder_path).glob("chapter_*.txt"):
        match = re.search(r"chapter_(\d+)", file.name)
        if match:
            chapter_num = int(match.group(1))
            chapter_files.append((chapter_num, file))
    
    # Sort by chapter number
    chapter_files.sort(key=lambda x: x[0])
    return chapter_files

def select_consecutive_chapters(chapter_files, max_chapters=3):
    """Select consecutive chapters with weighted probability"""
    # Weighted probability: 1 chapter (low), 2 chapters (medium), 3 chapters (high)
    weights = [1, 2, 3]  # Higher weight for more chapters
    num_chapters = random.choices([1, 2, 3], weights=weights)[0]
    
    # range of file numbers 
    # (-num_chapters to not go out of bounds)
    max_len = len(chapter_files) - num_chapters
    if max_len < 0:
        return None
    
    start_idx = random.randint(0, max_len)
    selected_chapters = chapter_files[start_idx:start_idx + num_chapters]
    
    return selected_chapters

def generate_samples(folder_path, num_samples=200):
    chapter_files = get_chapter_files(folder_path)
    samples = []
    
    while len(samples) < num_samples:
        # Select consecutive chapters
        selected_chapters = select_consecutive_chapters(chapter_files)
        print(selected_chapters)
        if not selected_chapters:
            continue
        
        text = ""
        
        # Try to find paragraphs in each chapter
        for chapter in selected_chapters:
            # try:
            with open(chapter[1], 'r', encoding='utf-8') as f:
                text += f.read() + "\n\n"         
            # except Exception as e:
            #     print(f"Error reading {chapter_file}: {e}")
            #     continue
        samples.append(text)
     
    return samples

def save_samples(samples, output_folder):
    """Save each sample as individual txt file"""
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    for i, sample in enumerate(samples, 1):
        filename = f"sample_{i}.txt"
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sample)

# Usage
if __name__ == "__main__":
    folder_path = r"C:\Users\optim\OneDrive\Documents\GitHub\mahabharata_rag\data"  # Change this to your folder path
    output_folder = r"C:\Users\optim\OneDrive\Documents\GitHub\mahabharata_rag\data_for_questions"  # Folder where individual sample files will be saved
    
    print("Generating 200 samples...")
    samples = generate_samples(folder_path, num_samples=200)
    
    print(f"Generated {len(samples)} samples")
    
    # Save individual sample files
    print("Saving individual sample files...")
    save_samples(samples, output_folder)
    
    print(f"\nDone!")
    print(f"Individual samples saved in: {output_folder}/")
