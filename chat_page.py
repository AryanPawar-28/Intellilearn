import streamlit as st
from io import BytesIO
import time


from utils.pdf_reader import get_pdf_text
from utils.text_splitter import split_text as get_text_chunks
from utils.embeddings_and_search import create_vector_store, similar_search_chunks
from utils.llm_answer import generate_answer

def render_chat_page():

    st.markdown(
    """
    <div class="main-header">
        🧠 INTELLILEARN
    </div>
    <div class="sub-header">
        AI-Based PDF Analyzer 
    </div>
    """,
    unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 3])

    # -------- SESSION INIT -------- #
    if "all_chats" not in st.session_state:
        st.session_state.all_chats = {}

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = "default"

    if "index" not in st.session_state:
        st.session_state.index = None

    if "text_chunks" not in st.session_state:
        st.session_state.text_chunks = None

    current_chat = st.session_state.current_chat_id

    if current_chat not in st.session_state.all_chats:
        st.session_state.all_chats[current_chat] = []

    # -------- UPLOAD SECTION -------- #
    with left_col:

        st.subheader("📄 Upload Document")

        with st.container(border=True):

            pdf_docs = st.file_uploader(
                "Upload PDF files",
                accept_multiple_files=True
            )

            if st.button("Process Document", type="primary", use_container_width=True):

                if not pdf_docs:
                    st.warning("Please upload a PDF first.")
                else:
                    with st.spinner("🔍 Processing document..."):

                        pdf_streams = [BytesIO(pdf.getvalue()) for pdf in pdf_docs]

                        st.session_state.pdf_bytes = pdf_docs[0].getvalue()

                        raw_text = get_pdf_text(pdf_streams)
                        text_chunks = get_text_chunks(raw_text)

                        index, texts = create_vector_store(text_chunks)

                        st.session_state.index = index
                        st.session_state.text_chunks = texts

                    st.success("✅ Document processed successfully!")

    # -------- CHAT SECTION -------- #
    with right_col:

        st.subheader("💬 Chat")

        chat_container = st.container(height=500, border=True)

        # -------- INPUT -------- #
        user_question = st.chat_input("Ask about your document...")

        if user_question:

            answer = None

            # ✅ Store user message FIRST
            st.session_state.all_chats[current_chat].append({
                "role": "user",
                "content": user_question
            })

            if st.session_state.index is None:
                answer = "⚠️ Upload document first."

            else:
                with st.spinner("🤖 Thinking..."):

                    results = similar_search_chunks(
                        user_question,
                        st.session_state.index,
                        st.session_state.text_chunks
                    )

                    answer = generate_answer(user_question, results)

            # ✅ Store assistant message
            st.session_state.all_chats[current_chat].append({
                "role": "assistant",
                "content": answer
            })

        # -------- DISPLAY CHAT (SCROLLABLE) -------- #
        with chat_container:

            messages = st.session_state.all_chats[current_chat]

            for msg in messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])