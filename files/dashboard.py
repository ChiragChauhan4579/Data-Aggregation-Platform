import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Query data
def get_connection():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="data_aggregation_platform",
            user="postgres",
            password="root"
        )
        return connection
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Query data using pandas
@st.cache_data
def load_data(query):
    conn = get_connection()
    if conn:
        return pd.read_sql(query, conn)
    else:
        return pd.DataFrame()


# Load tables data
queries_data = load_data("SELECT * FROM queries")
chunks_data = load_data("""
    SELECT chunks.*, queries.query_text
    FROM chunk_embeddings_relation as chunks
    JOIN queries ON chunks.query_id = queries.id
""")

# Dashboard layout
st.title("Queries & Chunks Dashboard")
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Select Page", ["Queries Overview", "Chunks Overview", "Query-wise Analysis"])

# Queries Overview
if page == "Queries Overview":
    st.subheader("Query Analytics")

    # Queries Created Over Time
    st.subheader("Queries Created Over Time")
    queries_data['created_at'] = pd.to_datetime(queries_data['created_at'])
    query_creation_time = queries_data.groupby(queries_data['created_at'].dt.date).size().reset_index(name='counts')
    fig = px.line(query_creation_time, x='created_at', y='counts', title="Queries Created Over Time")
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
    st.subheader(f"Chunk Distribution by URL for Query: {selected_query_text}")
    url_dist_query = filtered_chunks['url'].value_counts().reset_index(name='counts')
    url_dist_query.columns = ['url', 'counts']
    fig = px.bar(url_dist_query, x='url', y='counts', title=f"Chunk Distribution by URL for Query: {selected_query_text}", text_auto=True)
    st.plotly_chart(fig)

    # Chunks Created Over Time for Selected Query
    st.subheader(f"Chunks Created Over Time for Query: {selected_query_text}")
    filtered_chunks['created_at'] = pd.to_datetime(filtered_chunks['created_at'])
    chunk_creation_time_query = filtered_chunks.groupby(filtered_chunks['created_at'].dt.date).size().reset_index(name='counts')
    fig = px.line(chunk_creation_time_query, x='created_at', y='counts', title=f"Chunks Created Over Time for Query: {selected_query_text}")
    st.plotly_chart(fig)

    # Pie Chart of Chunks by URL for Selected Query
    st.subheader(f"Chunks by URL for Query: {selected_query_text}")
    url_dist_pie = filtered_chunks['url'].value_counts().reset_index(name='counts')
    url_dist_pie.columns = ['url', 'counts']
    fig = go.Figure(data=[go.Pie(labels=url_dist_pie['url'], values=url_dist_pie['counts'], hole=.3)])
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(title_text=f"Chunks by URL for Query: {selected_query_text}")
    st.plotly_chart(fig)