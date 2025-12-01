import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        port=6543,
        user="myuser",
        password="mypassword",
        dbname="mahabharat_db")

def insert_into_queries(rows):
    try:
        with conn.cursor() as cursor:
            # Postgres generates UUID using gen_random_uuid()
            insert_sql = """
            INSERT INTO queries (
                query_id, query_text, query_type
            ) VALUES (
                gen_random_uuid(), %s, %s
            )
            """
            cursor.executemany(insert_sql, rows)

        conn.commit()
        print(f"Inserted {len(rows)} rows successfully with DB-generated UUIDs.")

    finally:
        conn.close()


def get_queries_from_text(folder_path):
    lines_list = []

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # Only process text files
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()  # Remove newline and extra spaces
                    lines_list.append((line,filename.split('_')[0]))  # Append as a tuple

    print(f"No. of queries {len(lines_list)}")

    return lines_list


if __name__ == "__main__":
    folder_path = r"C:\Users\rando\OneDrive\Documents\GitHub\mahabharata_rag\short_selected_questions"

    rows = get_queries_from_text(folder_path)

    insert_into_queries(rows)





