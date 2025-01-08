import ollama
import chromadb
from sentence_transformers import util
from nltk.tokenize import sent_tokenize
from storage.database import PostgresDB
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import requests
import json

class RelevanceModel:
    def __init__(self):
        # retrive the necessary modules
        self.client = chromadb.PersistentClient("/app/storage/vectordb/")
        self.db = PostgresDB()

    def embed_text(self, input_text):
        # embeds text into 1024 dimension and returns the embedding vector as a response
        # response = ollama.embeddings(model='bge-m3:latest', prompt=input_text)
        url = "http://host.docker.internal:11434/api/embeddings"
    
        payload = json.dumps({
            "model": "bge-m3:latest",
            "prompt": input_text
        })
        headers = {
        'Content-Type': 'application/json'
        }
    
        response = requests.request("POST", url, headers=headers, data=payload)
      
        return response.json()['embedding']

    def get_collection_for_query(self, query):
        # finds the collection or create the new collection
        final_query = query.replace(' ','_').replace("'","")[:40]
        collection_name = f"collection_{final_query}"
        ef = OllamaEmbeddingFunction(
            model_name="bge-m3",
            url="http://host.docker.internal:11434/api/embeddings")
        return self.client.get_or_create_collection(name=collection_name,metadata={"hnsw:space": "cosine"},embedding_function=ef),collection_name

    def store_embedding(self, collection,url, title, index,chunk_embedding,chunk):
        # stores the embedding in the particular vectordb collection
        
        collection.add(documents=[chunk],
                       embeddings=[chunk_embedding],
                       metadatas=[{'url':url,'title': title, 'chunk_index': index}],
                       ids=[f"{title}_{index}"])

    def chunk_text(self, text, chunk_size=4096):
        # chunks the text with nltk sentence tokenizer and returns the list of chunks
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size:
                chunks.append(current_chunk)
                current_chunk = ""
            current_chunk += sentence + " "
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def check_relevance(self,query_id,query,scraped_articles, query_embedding, threshold=0.35):
        # Receives the articles and create chunks which are checked for relevance against the query with the embeddings model. 
        # Cosine similarity is used to the relevance.
        # Stores the embeddings for relevant chunk into vectordb and stores the relation of the query, chunk and embeddings in database.
        relevant_chunks = []
        collection,collection_name = self.get_collection_for_query(query)

        print("Length of articles",len(scraped_articles))
        
        index = 0
        for article in scraped_articles:
            chunks = self.chunk_text(article['content'])

            if len(chunks) == 0:
                continue

            print("Length of chunks",(len(chunks)))

            for chunk in chunks:
                if len(chunk) < 2:
                    continue
                
                print("processing chunk")
                chunk_embedding = self.embed_text(chunk)

                similarity = util.pytorch_cos_sim(query_embedding, chunk_embedding)
                print(similarity)
                if similarity > threshold:
                    
                    relevant_chunks.append({'url': article['url'],'title': article['title'], 'chunk': chunk, 'similarity': similarity.item()})

                    print(article['url'], article['title'], index, chunk_embedding,chunk)
                    self.store_embedding(collection,article['url'], article['title'], index, chunk_embedding,chunk)
                    
                    chunk_embeddings_rel_id = self.db.store_chunk_embeddings_relation(
                        url=article['url'],
                        title=article['title'],
                        chunk=chunk,
                        query_id=query_id,
                        chroma_id=index
                    )

                    index += 1

                    # summary = self.summarizer.summarize(chunk)
                            
                    # summary_id = self.db.store_summary(
                    #             title=article['title'],
                    #             summary=summary,
                    #             query_id=self.query_id,
                    #             chunk_embeddings_rel_id=chunk_embeddings_rel_id
                    #         )

            # summary = self.summarizer.summarize(article['content'])
                    
            # summary_id = self.db.store_summary(
            #             title=article['title'],
            #             summary=summary,
            #             query_id=self.query_id,
            #             chunk_embeddings_rel_id=chunk_embeddings_rel_id
            #         )

        return relevant_chunks, collection_name