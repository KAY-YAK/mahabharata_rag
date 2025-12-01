import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",  # instead of localhost
        port=6543,
        user="myuser",
        password="mypassword",
        database="mahabharat_db"
    )
    print("Connected successfully")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
