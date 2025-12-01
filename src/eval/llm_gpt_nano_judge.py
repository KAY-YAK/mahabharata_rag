import os
import time
import json
from openai import OpenAI

# ------------------------------
# CONFIG
# ------------------------------
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment")

client = OpenAI(api_key=API_KEY)

jsonl_folder = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\src\eval\jsonl_files\requests"
output_folder = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\src\eval\jsonl_files\responses"
poll_interval = 5  # seconds between polling batch job

os.makedirs(output_folder, exist_ok=True)

# ------------------------------
# Helper functions
# ------------------------------
def upload_jsonl(file_path):
    print(f"Uploading {file_path}...")
    with open(file_path, "rb") as f:
        upload = client.files.create(file=f, purpose="batch")
    return upload.id

def create_batch(upload_id):
    batch = client.batches.create(
        input_file_id=upload_id, 
        endpoint="/v1/responses",
        completion_window="24h")
    return batch.id

def wait_for_batch(batch_id):
    print(f"Waiting for batch {batch_id} to finish...")
    while True:
        batch = client.batches.retrieve(batch_id)
        status = batch.status

        print(batch.status)
         
        if status == "completed":
            print(f"Batch {batch_id} completed.")
            return batch
        elif status == "failed":
            print(batch.error_file_id)
            print(batch.errors)
            raise RuntimeError(f"Batch {batch_id} failed")
        time.sleep(poll_interval)

def download_results(batch, save_path):
    content = client.files.content(batch.output_file_id)
    with open(save_path, "wb") as f:
        f.write(content)
    print(f"Results saved to {save_path}")
    return save_path

def check_stop_condition(result_file):
    """Return True if any answer is NO"""
    with open(result_file, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            try:
                text = r["response"]["output"][0]["content"][0]["text"]
                parsed = json.loads(text)
                if parsed.get("answer", "").upper() == "NO":
                    print("Found 'NO' in batch. Stopping further processing.")
                    return True
            except Exception as e:
                print(f"Warning: failed to parse line: {e}")
    return False

def ask_user_continue():
    """Ask user permission to continue"""
    while True:
        resp = input("Continue to next batch? [Y/N]: ").strip().upper()
        if resp in ["Y", "N"]:
            return resp == "Y"
        print("Please enter Y or N.")

# ------------------------------
# Main sequential pipeline
# ------------------------------
for jsonl_file in sorted(os.listdir(jsonl_folder)):
    if not jsonl_file.endswith(".jsonl"):
        continue

    file_path = os.path.join(jsonl_folder, jsonl_file)
    upload_id = upload_jsonl(file_path)
    batch_id = create_batch(upload_id)
    batch = wait_for_batch(batch_id)

    # Create output filename with _response_ and .json
    base_name = os.path.splitext(jsonl_file)[0]
    result_file = os.path.join(output_folder, f"{base_name}_response.json")
    download_results(batch, result_file)

    # Stop immediately if any NO
    if check_stop_condition(result_file):
        print("Stopping pipeline due to 'NO'")
        break

    # Ask user before continuing to next batch
    if not ask_user_continue():
        print("User chose to stop the pipeline.")
        break

print("All done!")
