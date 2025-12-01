import os
import re
import glob
import csv
import string
import numpy as np
import matplotlib.pyplot as plt

# Count words while removing punctuation only
def word_count_clean(paragraph):
    table = str.maketrans('', '', string.punctuation)
    clean = paragraph.translate(table)
    return len(clean.split())

# Load paragraphs and keep chapter grouping
def load_paragraphs_by_chapter(source_dir):
    chapters_data = {}
    search_pattern = os.path.join(source_dir, "*_normalized.txt")
    chapter_files = sorted(glob.glob(search_pattern))

    print(f"Found {len(chapter_files)} chapter files.")

    for chapter_path in chapter_files:
        try:
            with open(chapter_path, "r") as f:
                content = f.read()

            chapter = os.path.basename(chapter_path)
            # Split by one or more newlines to get paragraphs
            paragraphs = re.split(r'\n\n', content)
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            # This line is also good to keep
            paragraphs = [p.replace("\n"," ") for p in paragraphs ]
            chapters_data[chapter] = paragraphs

        except Exception as e:
            print(f"Error reading {chapter_path}: {e}")
    
    # ... rest of the function is fine
    with open(r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\util\obs.txt","w") as f:
        f.write(str(chapters_data))

    return chapters_data

# Export CSV and gather all paragraph counts
def export_csv_and_collect_counts(chapters_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "paragraph_word_counts.csv")

    all_counts = []

    s = ""
    for x in list(chapters_data.keys()):
        s += x + "\n"
    with open(r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\util\obs.txt","w") as f:
        f.write(s)

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["chapter", "paragraph_index", "word_count"])
        lst = [["chapter","para_count","tot_word_count"]]

        for chapter, paragraphs in chapters_data.items():
            sum = 0
            for idx, para in enumerate(paragraphs, start=1):
                wc = word_count_clean(para)
                sum += wc
                writer.writerow([chapter, idx, wc])
                all_counts.append(wc)
            lst.append([chapter, len(paragraphs), sum])
        
        with open(r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\util\summary.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(lst)

    print(f"CSV exported: {csv_path}")
    return all_counts, csv_path

# Plot sorted counts
def plot_sorted_counts(all_counts, output_dir):
    print(f"\nTotal paragraphs: {len(all_counts)}")
    print(f"Mean: {np.mean(all_counts):.2f}")
    print(f"Median: {np.median(all_counts):.2f}")
    print(f"Max: {np.max(all_counts)}, Min: {np.min(all_counts)}")

    sorted_counts = sorted(all_counts)

    plt.figure(figsize=(24, 10))
    plt.plot(sorted_counts, marker='.', linestyle='-', linewidth=0.7)
    plt.title("Word Count of Each Paragraph (Sorted)", fontsize=16)
    plt.xlabel("Paragraph Index (sorted by length)", fontsize=12)
    plt.ylabel("Word Count", fontsize=12)
    plt.grid(alpha=0.4)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "paragraph_word_counts_sorted.png")
    plt.savefig(plot_path)
    plt.show()
    
    print(f"📊 Plot saved: {plot_path}")

# Report chapters with zero paragraphs
def report_empty_chapters(chapters_data):
    empty = [ch for ch, paras in chapters_data.items() if len(paras) == 0]
    if empty:
        print("\n⚠️ Chapters with NO paragraphs found:")
        for ch in empty:
            print(" -", ch)
    else:
        print("\n✅ All chapters have paragraphs")


source_dir = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\data"
output_dir = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\util\paragraph_length_analysis"

chapters_data = load_paragraphs_by_chapter(source_dir)
report_empty_chapters(chapters_data)

if chapters_data:
    all_counts, csv_path = export_csv_and_collect_counts(chapters_data, output_dir)
    if all_counts:
        plot_sorted_counts(all_counts, output_dir)
else:
    print("No chapter data found.")
