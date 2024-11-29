import psycopg2

class PostgresDB:
    def __init__(self):
        # connect to the database
        # self.connection = psycopg2.connect(
        #     host="localhost",
        #     database="data_aggregation_platform",
        #     user="postgres",
        #     password="root"
        # )
        self.connection = psycopg2.connect("postgresql://postgres:root@host.docker.internal:5432/data_aggregation_platform")
        self.cursor = self.connection.cursor()

    def store_query(self, query_text,engine, scrape_type, advanced_scrape):
        # store the queries
        insert_query = "INSERT INTO queries (query_text,engine,scrape_type,advanced_scrape) VALUES (%s,%s,%s,%s) RETURNING id"
        self.cursor.execute(insert_query, (query_text,engine, scrape_type, advanced_scrape))
        self.connection.commit()
        return self.cursor.fetchone()[0]  # Return the generated query ID

    def store_chunk_embeddings_relation(self, url,title, chunk, query_id, chroma_id):
        # store the relation of query, chunk and embedding id in the vector db
        insert_query = "INSERT INTO chunk_embeddings_relation (url,title, chunk, query_id, chroma_id) VALUES (%s, %s, %s, %s, %s) RETURNING id"
        self.cursor.execute(insert_query, (url,title, chunk, query_id, chroma_id))
        self.connection.commit()
        return self.cursor.fetchone()[0]  # Return the generated chunk_embeddings_rel_id

    # def store_summary(self, title, summary, query_id, embedding_id):
    #     insert_query = "INSERT INTO summaries (title, summary, query_id, chunk_embeddings_rel_id) VALUES (%s, %s, %s, %s)"
    #     self.cursor.execute(insert_query, (title, summary, query_id, embedding_id))
    #     self.connection.commit()
    #     return self.cursor.fetchone()[0] # Return the generated summary ID

    # def close(self):
    #     self.cursor.close()
    #     self.connection.close()

"""

CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE chunk_embeddings_relation (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    query_id INT,
    chroma_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE
);

CREATE TABLE summaries (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    summary TEXT,
    query_id INT,
    chunk_embeddings_rel_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE,
    FOREIGN KEY (chunk_embeddings_rel_id) REFERENCES embeddings(id) ON DELETE CASCADE
);
"""