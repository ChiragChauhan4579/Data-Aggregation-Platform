from fastapi import FastAPI
from pydantic import BaseModel
from query_process.query_processing import ProcessSystem
import uvicorn
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import opik
opik.configure(use_local=False)
os.environ["OPIK_PROJECT_NAME"] = "Data_Aggregation_Platform"
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
import ollama
import chromadb
import requests
import json
import time
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from opik.integrations.langchain import OpikTracer
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
client = chromadb.PersistentClient('/app/storage/vectordb/')
ef = OllamaEmbeddingFunction(
        model_name="bge-m3",
        url="http://host.docker.internal:11434/api/embeddings")

# start the app
app = FastAPI()

Instrumentator().instrument(app).expose(app)

opik_tracer = OpikTracer(tags=["langchain", "ollama"])

class QueryRequest(BaseModel):
    query: str
    engine: str
    scrape_type: str
    advanced_scrape: str

class ChatRequest(BaseModel):
    query_id: int
    collection_name: str
    chat_query: str

def ollama_embed(prompt):
    url = "http://host.docker.internal:11434/api/embeddings"

    payload = json.dumps({
        "model": "bge-m3:latest",
        "prompt": prompt
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()

def retriever_func(chat_query,collection_name):
    # Get the collection
    collection = client.get_collection(name=collection_name, embedding_function=ef)
    # response = ollama.embeddings(model='bge-m3:latest', prompt=chat_query)
    response = ollama_embed(chat_query)
    # Retrieve the top 5 matches based on similarity
    retriver_response = collection.query(
            query_embeddings=[response['embedding']],
            n_results=5)

    return retriver_response

def generate_response_with_ollama(retriever_response, chat_query):
    # Initialize the Ollama model with LangChain
    ollama_llm = Ollama(model="gemma:2b",base_url='http://host.docker.internal:11434/').with_config({"callbacks": [opik_tracer]})

    # Convert retriever response into a list of documents
    docs = []
    for item in retriever_response['documents'][0]:
        docs = [Document(item)]
    
    # Create the LangChain prompt template
    prompt_template = """
    Given the following retrieved documents and the user query, generate a comprehensive response.
    
    Query: {query}
    
    Retrieved Documents:
    {retrieved_documents}

    Chat History:
    {chat_history}

    Response:
    """

    # Create a function to format the retrieved documents for the prompt
    def format_documents(docs):
        return "\n".join([f"Document {i+1}: {doc.page_content}" for i, doc in enumerate(docs)])

    memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True,input_key="query",k=3)

    # Prepare the prompt with the retrieved documents and user query
    formatted_documents = format_documents(docs)

    prompt = PromptTemplate(
        input_variables=["query","retrieved_documents","chat_history"],
        template=prompt_template,
    )

    # Initialize LangChain's LLMChain
    llm_chain = LLMChain(llm=ollama_llm, prompt=prompt,memory=memory,verbose=True)

    response = llm_chain.run(query=chat_query, retrieved_documents=formatted_documents)

    return response

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application with Prometheus metrics!"}

# process the input user queries
@app.post("/rag/process_query")
def process_query(request: QueryRequest):
    try:
        system = ProcessSystem()
        collection_name = system.process_query(request.query,request.engine,request.scrape_type,request.advanced_scrape)
        return collection_name
    except Exception as e:
        raise e

@app.post("/rag/predict")
def generate(request: ChatRequest):
    try:
        retriver_response = retriever_func(request.chat_query,collection_name=request.collection_name)
        chat_response = generate_response_with_ollama(retriever_response=retriver_response,chat_query=request.chat_query)
        return chat_response
    except Exception as e:
        raise e

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False,workers=2)

    # to stop the app reloading at every code change, change reload=False.