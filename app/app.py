import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
# import seaborn as sns
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
import requests
from urllib.parse import urlparse

FASTAPI_URL = "http://fastapi:8000"

# Query data
def get_connection():
    try:
        # connection = psycopg2.connect(
        #     host="localhost",
        #     database="data_aggregation_platform",
        #     user="postgres",
        #     password="root"
        # )
        connection = psycopg2.connect("postgresql://postgres:root@host.docker.internal:5432/data_aggregation_platform")
        return connection
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Query data using pandas
def load_data(query):
    conn = get_connection()
    if conn:
        return pd.read_sql(query, conn)
    else:
        return pd.DataFrame()

def process_query(query: str,engine: str, scrape_type: str, advanced_scrape: str):
    endpoint = f"{FASTAPI_URL}/rag/process_query"
    response = requests.post(endpoint, json={"query": query,"engine":engine,"scrape_type":scrape_type,"advanced_scrape":advanced_scrape})
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error calling API: {response.text}")
        return None

def generate_chat_response(query_id: int, collection_name: str, chat_query: str):
    endpoint = f"{FASTAPI_URL}/rag/predict"
    response = requests.post(endpoint, json={
        "query_id": query_id,
        "collection_name": collection_name,
        "chat_query": chat_query
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error generating chat response: {response.text}")
        return None


# Load tables data
queries_data = load_data("SELECT * FROM queries")
chunks_data = load_data("""
    SELECT chunks.*, queries.query_text
    FROM chunk_embeddings_relation as chunks
    JOIN queries ON chunks.query_id = queries.id
""")

# Dashboard layout
st.title("Data Aggregation Platform")
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select Page", ["Data Collector","Chat","Queries Overview", "Chunks Overview", "Query-wise Analysis"])

# Queries Overview
if page == "Data Collector":
    st.subheader("Query Interaction with Backend")

    # Query input from the user
    user_query = st.text_input("Enter your query:")
    engine = st.selectbox(
            "What Search Engine you want to use?",
            ("Google", "DuckDuckGo"),
        )
    scrape_type = st.selectbox(
            "Scrape the site or use snippet?",
            ("Scrape", "Snippet"),
        )

    scrape_type = "Full" if scrape_type == 'Scrape' else "Half"

    advanced_scrape = st.selectbox(
            "Enable intelligent scraper?",
            ("No", "Yes"),
        )
    
    if st.button("Process Query"):
        print(user_query,engine,scrape_type,advanced_scrape)
        collection_name = process_query(user_query,engine,scrape_type,advanced_scrape)
        
        if collection_name:
            st.success(f"Processed query: Collection created with name {collection_name}. To chat with the data go to the Chat Option from the navigation")
            
if page == "Chat":
    
    queries_data = load_data("SELECT query_text FROM queries")
    selector_collection = st.selectbox("Select your search query:",queries_data)

    # chat_query = st.text_input("Enter a follow-up chat query:")
    if selector_collection:
        collection_name = "collection_" + selector_collection.replace(" ","_").replace("'","")[:40]

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if chat_query := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": chat_query})
            with st.chat_message("user"):
                st.markdown(chat_query)
            with st.chat_message("assistant"):
                with st.spinner('Responding'):
                    message_placeholder = st.empty()
                    full_response = ""
                    try:
                        llm_answer = generate_chat_response(query_id=1, collection_name=collection_name, chat_query=chat_query)
                        message_placeholder.markdown(llm_answer)
                        st.session_state.messages.append({"role": "assistant", "content": llm_answer})
                    except:  # noqa: E722
                        st.warning("Something unexpected happened. Please try again!")

    # if st.button("Generate Chat Response"):
    #     chat_response = generate_chat_response(query_id=1, collection_name=collection_name, chat_query=chat_query)
                
    #     if chat_response:
    #         st.write("Chat Response:")
    #         st.write(chat_response)

# Queries Overview
if page == "Queries Overview":
    st.subheader("Query Analytics")

    # Queries Created Over Time
    st.subheader("Queries Created Over Time")
    queries_data['created_at'] = pd.to_datetime(queries_data['created_at'])
    query_creation_time = queries_data.groupby(queries_data['created_at'].dt.date).size().reset_index(name='counts')
    fig = px.line(query_creation_time, x='created_at', y='counts', title="Queries Created Over Time")
    st.plotly_chart(fig)

    # Queries Created Over Time
    st.subheader("Queries By Engine, Scrape Type and Intelligent Scraping")
    fig = px.sunburst(
        queries_data,
        path=['engine', 'scrape_type', 'advanced_scrape','query_text'],
        title="Sunburst Chart of Query Parameters"
    )
    st.plotly_chart(fig)

    # Distribution of Query Length
    st.subheader("Distribution of Query Text Length")
    queries_data['query_length'] = queries_data['query_text'].apply(len)
    fig = px.histogram(queries_data, x='query_length', nbins=30, title="Distribution of Query Text Length")
    st.plotly_chart(fig)

    # Most Frequent Query Words
    st.subheader("Most Common Words in Queries")
    from collections import Counter
    word_count = Counter(" ".join(queries_data['query_text']).split())
    common_words = pd.DataFrame(word_count.most_common(20), columns=['Word', 'Frequency'])
    fig = px.bar(common_words, x='Word', y='Frequency', title="Top 20 Most Frequent Words in Queries")
    st.plotly_chart(fig)

# Chunks Overview
if page == "Chunks Overview":
    st.subheader("Chunks and Embeddings Analytics")

    # Distribution of Chunks per Query (using query_text)
    st.subheader("Distribution of Chunks per Query")
    chunk_dist = chunks_data.groupby('query_text').size().reset_index(name='chunk_count')
    fig = px.histogram(chunk_dist, x='chunk_count', nbins=20, title="Distribution of Chunks per Query")
    st.plotly_chart(fig)

    # Most Frequent URLs
    st.subheader("Top 10 Most Frequent URLs")
    url_dist = chunks_data['url'].value_counts().head(10).reset_index(name='counts')
    url_dist.columns = ['url', 'counts']
    fig = px.bar(url_dist, x='url', y='counts', title="Top 10 Most Frequent URLs", text_auto=True)
    st.plotly_chart(fig)

    # Chunks Created Over Time
    st.subheader("Chunks Created Over Time")
    chunks_data['created_at'] = pd.to_datetime(chunks_data['created_at'])
    chunk_creation_time = chunks_data.groupby(chunks_data['created_at'].dt.date).size().reset_index(name='counts')
    fig = px.line(chunk_creation_time, x='created_at', y='counts', title="Chunks Created Over Time")
    st.plotly_chart(fig)

    # Donut Chart of Chunks by Query Text
    st.subheader("Chunks by Query Text (Donut Chart)")
    chunk_count_query = chunks_data['query_text'].value_counts().reset_index(name='counts')
    chunk_count_query.columns = ['query_text', 'counts']
    fig = go.Figure(data=[go.Pie(labels=chunk_count_query['query_text'], values=chunk_count_query['counts'], hole=.4)])
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(title_text="Chunks by Query Text")
    st.plotly_chart(fig)

    # Scatter Plot: Chunk Length vs. Creation Time
    st.subheader("Chunk Length vs. Time Created")
    chunks_data['chunk_length'] = chunks_data['chunk'].apply(len)
    fig = px.scatter(chunks_data, x='created_at', y='chunk_length', color='query_text', title="Chunk Length vs. Time Created")
    st.plotly_chart(fig)

# Query-wise Analysis
if page == "Query-wise Analysis":
    st.subheader("Detailed Query Analysis")

    selected_query_text = st.selectbox("Select Query", queries_data['query_text'])
    filtered_chunks = chunks_data[chunks_data['query_text'] == selected_query_text]

    # Chunk Distribution by URL for Selected Query
    # st.subheader(f"Chunk Distribution by URL for Query: {selected_query_text}")
    url_dist_query = filtered_chunks['url'].value_counts().reset_index(name='counts')
    url_dist_query.columns = ['url', 'counts']
    fig = px.bar(url_dist_query, x='url', y='counts', title=f"Chunk Distribution by URL for Query: {selected_query_text}", text_auto=True)
    st.plotly_chart(fig)

    # Chunks Created Over Time for Selected Query
    # st.subheader(f"Chunks Created Over Time for Query: {selected_query_text}")
    filtered_chunks['created_at'] = pd.to_datetime(filtered_chunks['created_at'])
    chunk_creation_time_query = filtered_chunks.groupby(filtered_chunks['created_at'].dt.date).size().reset_index(name='counts')
    fig = px.line(chunk_creation_time_query, x='created_at', y='counts', title=f"Chunks Created Over Time for Query: {selected_query_text}")
    st.plotly_chart(fig)

    # Pie Chart of Chunks by URL for Selected Query
    # st.subheader(f"Chunks by URL for Query: {selected_query_text}")
    filtered_chunks['domain'] = filtered_chunks['url'].apply(lambda url: urlparse(url).netloc)
    url_dist_pie = filtered_chunks['domain'].value_counts().reset_index(name='counts')
    url_dist_pie.columns = ['domain', 'counts']
    fig = go.Figure(data=[go.Pie(labels=url_dist_pie['domain'], values=url_dist_pie['counts'], hole=.3)])
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(title_text=f"Chunks by Domain for Query: {selected_query_text}")
    st.plotly_chart(fig)