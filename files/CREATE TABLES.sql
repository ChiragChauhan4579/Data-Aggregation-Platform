CREATE TABLE queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
	engine TEXT NOT NULL,
	scrape_type TEXT NOT NULL,
	advanced_scrape TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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