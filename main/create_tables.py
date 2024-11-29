import psycopg2

create_queries_table = """
CREATE TABLE IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_chunk_embeddings_table = """
CREATE TABLE chunk_embeddings_relation (
    id SERIAL PRIMARY KEY,
    url VARCHAR(1000),
    title VARCHAR(1000),
    chunk TEXT,
    query_id INT,
    chroma_id VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE
);
"""

# Connect to the database
try:
    connection = psycopg2.connect(
                host="localhost",
                database="data_aggregation_platform", # change the database name
                user="postgres", # change the username
                password="root" # change the password
            )

    cursor = connection.cursor()

    # Execute table creation queires
    cursor.execute(create_queries_table)
    cursor.execute(create_chunk_embeddings_table)

    # Commit changes
    connection.commit()

    print("Tables created successfully.")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the cursor and connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()
