import os
import re
import matplotlib.pyplot as plt
import glob
import numpy as np
import seaborn as sns # Using seaborn for plots
from scipy import stats # We can still import stats for other things

# --- THIS FUNCTION IS THE FIX ---
def calculate_mode(data):
    """
    Calculates the mode(s) of a list of data.
    Handles cases with multiple modes. Does not require scipy.multimode.
    """
    if not data:
        return []
    values, counts = np.unique(data, return_counts=True)
    max_count = np.max(counts)
    modes = values[counts == max_count]
    return list(modes)

def count_words(text):
    """Counts words in a string after removing punctuation."""
    clean_text = re.sub(r'[^\w\s]', '', text)
    return len(clean_text.split())

def place_legend_top_right(ax, mean_val, median_val, max_val, min_val, mode_val):
    """Helper function to place a legend at the top right."""
    legend_text = (
        f"Mean: {mean_val:.2f}\n"
        f"Median: {median_val:.2f}\n"
        f"Max: {max_val}\n"
        f"Min: {min_val}\n"
        f"Mode(s): {mode_val}"
    )
    ax.legend([legend_text], loc='upper right', frameon=True, fancybox=True, shadow=True)

def plot_word_counts(source_dir, output_dir):
    """Generates three plots: chronological, sorted, and bucketed word counts."""
    print("Starting word count analysis...")
    
    all_counts = []
    
    search_pattern = os.path.join(source_dir, f"*_normalized.txt")
    chapter_files = sorted(glob.glob(search_pattern))
    
    print(f"Found {len(chapter_files)} files to process.")

    for chapter_file_path in chapter_files:
        try:
            with open(chapter_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            all_counts.append(count_words(content))
        except Exception as e:
            print(f"Error processing {chapter_file_path}: {e}")

    if not all_counts:
        print("No files were processed. Cannot generate plots.")
        return

    # Calculate statistics
    mean_count = np.mean(all_counts)
    median_count = np.median(all_counts)
    max_count = np.max(all_counts)
    min_count = np.min(all_counts)
    
    # --- USE OUR CUSTOM FUNCTION INSTEAD OF stats.multimode ---
    mode_result = calculate_mode(all_counts)
    mode_str = ', '.join(map(str, mode_result))

    print(f"\nTotal chapters processed: {len(all_counts)}")
    print(f"Mean: {mean_count:.2f}, Median: {median_count:.2f}, Max: {max_count}, Min: {min_count}, Mode(s): {mode_str}")

    # --- PLOT 1: CHRONOLOGICAL ORDER ---
    print("Generating chronological plot...")
    fig1, ax1 = plt.subplots(figsize=(20, 10))
    ax1.bar(range(len(all_counts)), all_counts, color='skyblue')
    ax1.set_title('Word Count per Chapter (Chronological Order)', fontsize=16)
    ax1.set_xlabel('Chapter Number', fontsize=12)
    ax1.set_ylabel('Word Count', fontsize=12)
    place_legend_top_right(ax1, mean_count, median_count, max_count, min_count, mode_str)
    
    tick_indices = list(range(0, len(all_counts), 50))
    if (len(all_counts) - 1) not in tick_indices:
        tick_indices.append(len(all_counts) - 1)
    ax1.set_xticks(tick_indices)
    ax1.set_xticklabels([str(i + 1) for i in tick_indices], rotation=45, ha='right')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    plot_path1 = os.path.join(output_dir, 'word_count_chronological.png')
    plt.savefig(plot_path1)
    print(f"Chronological plot saved to: {plot_path1}")
    plt.close(fig1)

    # --- PLOT 2: SORTED ORDER ---
    print("Generating sorted plot...")
    fig2, ax2 = plt.subplots(figsize=(20, 10))
    sorted_counts = sorted(all_counts)
    ax2.bar(range(len(sorted_counts)), sorted_counts, color='lightgreen')
    ax2.set_title('Word Count per Chapter (Sorted by Length)', fontsize=16)
    ax2.set_xlabel('Chapter (Sorted by Word Count)', fontsize=12)
    ax2.set_ylabel('Word Count', fontsize=12)
    place_legend_top_right(ax2, mean_count, median_count, max_count, min_count, mode_str)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    plot_path2 = os.path.join(output_dir, 'word_count_sorted.png')
    plt.savefig(plot_path2)
    print(f"Sorted plot saved to: {plot_path2}")
    plt.close(fig2)

    # --- PLOT 3: BUCKETED WORD COUNTS ---
    print("Generating bucketed plot...")
    bucket_increments = [200, 250, 300, 350, 400]
    
    for increment in bucket_increments:
        fig3, ax3 = plt.subplots(figsize=(15, 8))
        max_count = max(all_counts)
        bins = range(0, max_count + increment, increment)
        
        sns.histplot(all_counts, bins=bins, kde=False, ax=ax3, color='salmon')
        
        ax3.set_title(f'Distribution of Chapter Word Counts (Bucket Size: {increment})', fontsize=16)
        ax3.set_xlabel(f'Word Count Bins (e.g., 1-{increment}, {increment+1}-{2*increment})', fontsize=12)
        ax3.set_ylabel('Number of Chapters', fontsize=12)
        ax3.grid(axis='y', alpha=0.75)
        
        stats_text = f"Mean: {mean_count:.2f}\nMedian: {median_count:.2f}\nMode(s): {mode_str}"
        ax3.text(0.98, 0.95, stats_text, transform=ax3.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        plot_path3 = os.path.join(output_dir, f'word_count_buckets_{increment}.png')
        plt.savefig(plot_path3)
        print(f"Bucketed plot ({increment}) saved to: {plot_path3}")
        plt.close(fig3)

    print("\nAll plots generated successfully.")




# --- SCRIPT EXECUTION ---
source_dir = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\data"
output_dir = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\util\chapter_length_analysis"

plot_word_counts(source_dir, output_dir)