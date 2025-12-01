# The Mahabharata RAG

The **mahabharata_rag** is a tool that lets you ask questions about the Mahabharata and get accurate answers. It works by first finding the right parts of the text and then using them to generate a clear, reliable response. It’s an easy way to explore the stories, characters, and ideas in the epic.

#### How to run this?
1. Run the docker.
2. Run `create_documents_table.sql`
3. Run `constraints.sql` 
4. Install everything from `requirements.txt`
5. Extract and load data from `mahabharat_db_dump.zip`
6. Open the `src/app/retrieval/rag_pipeline.py` and replace query in line 71.
 
 **Stack used**
 1. Postgres for vector database
 2. Docker to run postgres
 3. Python


## The retrieval process
```
query → router
          ├→ sanity check → answer
          ├→ summary check → bm25 search → llm → answer
          └→ hybrid search → llm → answer

```

1. `router.py` - Checks sanity and if the question asks for a summary.
2. `query_engineering.py` - Used to check sanity and see if the query asks for specific summary
3. `semantic_search.py` - Implmentation of semantic search
4. `keyword_search.py` - Implementation of BM25 search
5. `hybrid_search.py` - Implements hybrid search using both Semantic and BM25 search.
6. `build_context.py` - Builds the context for the llm after retrieval(search)
7. `build_bm25_index.py` - This builds BM25 index from the database. Postgress has implementations of BM25 which either requires a extension and they are not exactly BM25.
8. `utils.py` - Contains configs and enums
9. `rag_pipeline.py` - Implements the full pipeline combining everything above

Read comments within the files for more details.

## The data
The project for parsing the data is [here](https://github.com/KAY-YAK/the_mahabharata_parsing). 

 - The `/data` folder has 1995 Chapters. They have footnotes attched to them.
 - The Mahabharata has two classification of its chapters
	 - The 100 Parva classification (only 95 Parvas in the book)
	 - The 18 Parva classification
	 - The chapters and their association can be found in the `Mahabharat_parva_classification.csv` file
 - The `/data_summary` folder contains a summary in 100 parvas and in 18 parvas.

## Vector DB and Chunking
The mean words per chapter is 1017. This is without footnotes. 
Dr. Bibek Debroy's Mahabharata translation is about 2 million words in length.
For chunking I took *1800 character chunk with 200 character overlap*. The overlap is however within each chapter.

### 1️⃣ `clean_chunk`
-   **Definition:** A text chunk cleaned of footnotes, formatting noise, and non-essential annotations.
-   **Purpose:** Embedding for **semantic search**.
-   **Why:** Semantic embeddings capture the meaning/context of the text. Footnotes, epithets, and non-canon names may dilute the embedding quality and introduce noise.

### 2️⃣ `enriched_chunk`
-   **Definition:** `clean_chunk` + footnotes
-   **Purpose:** **BM25 keyword search**. 
-   **Why:** BM25 relies on exact term matches. Queries using epithets or non-canonical names (like `Bibhatsu` for Arjuna) may not appear in the main text. Including footnotes ensures hits are captured.

### 3️⃣ `document_type`
 -   There are two types 
	- *content_chunk* [These are from the 1995 chapters]
	- *summary_chunk* [These are from summaries generated from parvas]
	
### 4️⃣ `embedding`
 - This is the embedding of *clean_chunk* 
### 5️⃣ `bm25_vector`
 - This *enriched_chunk* tokenized into words for BM25 search to work.
 
### 5️⃣ `metadata`
 - This is just metadata. Example is provided below
	  * 
```
clean_chunk example	
		{
			"chunk_no":  "4", 
			"chapter_no":  "1290",  
			"parva_hundred_no":  "78",  
			"parva_eighteen_no":  "10",  
			"parva_hundred_name":  "Souptika",  
			"parva_eighteen_name":  "Souptika"
		}
```
```
enriched_chunk example
		{
			"chunk_no":  "1",  
			"parva_summary":  true,  
			"parva_hundred_name":  "Parvasamgraha",  
			"parva_eighteen_name":  "Adi"
		}
```

 