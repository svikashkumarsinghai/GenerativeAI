import streamlit as st
import ollama
import fitz

from docx import Document

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_ollama import OllamaEmbeddings

from langchain_chroma import Chroma


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="AI Document Chatbot",
    layout="wide"
)

st.title("📄 AI Document Chatbot")


# =====================================
# SESSION STATE
# =====================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "document_loaded" not in st.session_state:
    st.session_state.document_loaded = False


# =====================================
# FILE READING FUNCTIONS
# =====================================

def read_txt(file):

    return file.read().decode("utf-8")


def read_docx(file):

    doc = Document(file)

    text = "\n".join(
        [para.text for para in doc.paragraphs]
    )

    return text


def read_pdf(file):

    text = ""

    pdf = fitz.open(
        stream=file.read(),
        filetype="pdf"
    )

    for page in pdf:

        text += page.get_text()

    return text


def load_document(uploaded_file):

    file_type = (
        uploaded_file.name
        .split(".")[-1]
        .lower()
    )

    if file_type == "txt":

        return read_txt(uploaded_file)

    elif file_type == "docx":

        return read_docx(uploaded_file)

    elif file_type == "pdf":

        return read_pdf(uploaded_file)

    else:

        return ""


# =====================================
# CREATE VECTOR DATABASE
# =====================================

def create_vectorstore(text):

    # split text into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    # create embeddings model
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    # create vector database
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    return vectorstore


# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.header("⚙ Settings")

    model_name = st.selectbox(
        "Choose AI Model",
        [
            "gemma:latest",
            "smollm2:latest",
            "llama3:latest"
        ]
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:

        with st.spinner("Processing document..."):

            try:

                document_text = load_document(
                    uploaded_file
                )

                vectorstore = create_vectorstore(
                    document_text
                )

                st.session_state.vectorstore = (
                    vectorstore
                )

                st.session_state.document_loaded = True

                st.success(
                    "Document processed successfully!"
                )

            except Exception as e:

                st.error(f"Error: {e}")

    st.divider()

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# =====================================
# SHOW CHAT HISTORY
# =====================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# =====================================
# CHAT INPUT
# =====================================

user_prompt = st.chat_input(
    "Ask something about your document..."
)


# =====================================
# HANDLE USER INPUT
# =====================================

if user_prompt:

    # check document uploaded
    if not st.session_state.document_loaded:

        st.warning(
            "Please upload a document first."
        )

        st.stop()

    # show user message
    st.chat_message("user").markdown(
        user_prompt
    )

    # save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })

    # =====================================
    # RETRIEVE RELEVANT CHUNKS
    # =====================================

    docs = (
        st.session_state.vectorstore
        .similarity_search(
            user_prompt,
            k=4
        )
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # =====================================
    # LIMITED CHAT HISTORY
    # =====================================

    recent_messages = (
        st.session_state.messages[-6:]
    )

    conversation_history = ""

    for msg in recent_messages:

        conversation_history += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    # =====================================
    # FINAL PROMPT
    # =====================================

    full_prompt = f"""
You are an intelligent AI assistant.

Guidelines:
- Use the provided context as the primary source of information.
- If the context contains the answer, base your response entirely on it.
- If the answer is not found in the context, answer using your general knowledge and state that the information is not present in the uploaded document.
- Provide concise, accurate, and well-formatted responses.
- Use bullet points when appropriate.

=====================
DOCUMENT CONTEXT
=====================

{context}

=====================
CHAT HISTORY
=====================

{conversation_history}

=====================
QUESTION
=====================

{user_prompt}
"""

    # =====================================
    # ASSISTANT RESPONSE
    # =====================================

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        full_response = ""

        try:

            stream = ollama.chat(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful "
                            "document assistant."
                        )
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                stream=True
            )

            for chunk in stream:

                content = (
                    chunk["message"]["content"]
                )

                full_response += content

                message_placeholder.markdown(
                    full_response + "▌"
                )

            message_placeholder.markdown(
                full_response
            )

        except Exception as e:

            st.error(f"LLM Error: {e}")

            st.stop()

    # =====================================
    # SAVE ASSISTANT RESPONSE
    # =====================================

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })