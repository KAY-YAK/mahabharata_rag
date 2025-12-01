import os
import shutil
from pathlib import Path

def copy_files_with_verification(source_base, destination_path, expected_count=1995):
    """
    Copy files from Volume_1 to Volume_10 under folder_here to destination_path
    and verify the total count matches expected_count.
    
    Args:
        source_base: Base path where Volume_1 to Volume_10 are located
        destination_path: Path where files will be copied
        expected_count: Expected total number of files (default: 1995)
    """
    # Create destination directory if it doesn't exist
    os.makedirs(destination_path, exist_ok=True)
    
    total_files_copied = 0
    
    # Iterate through Volume_1 to Volume_10
    for volume_num in range(1, 11):
        volume_name = f"Volume_{volume_num}"
        source_folder = os.path.join(source_base, volume_name, "chapters_cleaned")
        
        # Check if source folder exists
        if not os.path.exists(source_folder):
            print(f"Warning: {source_folder} does not exist. Skipping.")
            continue
        
        # Copy all files from the source folder
        for filename in os.listdir(source_folder):
            source_file = os.path.join(source_folder, filename)
            
            # Skip directories, only copy files
            if os.path.isfile(source_file):
                destination_file = os.path.join(destination_path, filename)
                
                # Handle duplicate filenames by appending volume number
                # if os.path.exists(destination_file):
                #     name, ext = os.path.splitext(filename)
                #     destination_file = os.path.join(destination_path, f"{name}_vol{volume_num}{ext}")
                
                shutil.copy2(source_file, destination_file)
                total_files_copied += 1
                
                # Progress indicator
                if total_files_copied % 100 == 0:
                    print(f"Copied {total_files_copied} files...")
    
    print(f"Copy operation completed. Total files copied: {total_files_copied}")
    
    # Verification
    if total_files_copied == expected_count:
        print(f"Verification successful: Copied exactly {expected_count} files as expected.")
        return True
    else:
        print(f"Verification failed: Expected {expected_count} files, but copied {total_files_copied} files.")
        return False

# Example usage
if __name__ == "__main__":
    # Replace these paths with your actual paths
    source_base_path = r"C:\Users\rando\OneDrive\Desktop\RAG\corpus\Volume Split Cleaned"  # Path where Volume_1 to Volume_10 are located
    destination_directory = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\data"  # Path where you want to copy the files
    
    success = copy_files_with_verification(source_base_path, destination_directory)
    
    if success:
        print("Operation completed successfully!")
    else:
        print("Operation completed with issues. Please check the file count.")