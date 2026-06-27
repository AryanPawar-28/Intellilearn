import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np




# ---------- LOAD MODEL (CACHED) ---------- #
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")




# ---------- CREATE VECTOR STORE ---------- #
def create_vector_store(text_chunks):


    if not text_chunks:
        return None, None


    model = load_model()


    embeddings = model.encode(text_chunks, batch_size=32)


    embeddings = np.array(embeddings).astype("float32")


    # normalize (important for better similarity)
    faiss.normalize_L2(embeddings)


    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)


    index.add(embeddings)


    return index, text_chunks




# ---------- SEMANTIC SEARCH ---------- #
def similar_search_chunks(query, index, text_chunks, k=5):


    if index is None or text_chunks is None:
        return []


    if not query.strip():
        return []


    model = load_model()


    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")


    # normalize
    faiss.normalize_L2(query_embedding)


    distances, indices = index.search(query_embedding, k)


    results = []


    for i in indices[0]:
        if i == -1:
            continue
        if i < len(text_chunks):
            results.append(text_chunks[int(i)])


    return results

