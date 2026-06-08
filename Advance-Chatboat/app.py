
import streamlit as st
import ollama

from docx import Document
from pypdf import PdfReader

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_community.vectorstores import Chroma

from langchain_community.embeddings import (
    OllamaEmbeddings
)


# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Advanced Document Chatbot",
    layout="wide"
)

st.title("📄 Advanced AI Document Assistant")


# =========================================
# SESSION STATE
# =========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None


# =========================================
# DOCUMENT READERS
# =========================================

def read_txt(file):

    return file.read().decode("utf-8")


def read_docx(file):

    doc = Document(file)

    return "\n".join([
        para.text for para in doc.paragraphs
    ])


def read_pdf(file):

    pdf = PdfReader(file)

    text = ""

    for page in pdf.pages:

        extracted_text = page.extract_text()

        if extracted_text:
            text += extracted_text + "\n"

    return text


def load_document(uploaded_file):

    file_extension = (
        uploaded_file.name
        .split(".")[-1]
        .lower()
    )

    if file_extension == "txt":
        return read_txt(uploaded_file)

    elif file_extension == "docx":
        return read_docx(uploaded_file)

    elif file_extension == "pdf":
        return read_pdf(uploaded_file)

    else:
        return ""


# =========================================
# VECTOR DATABASE CREATION
# =========================================

def create_vector_database(document_text):

    # split document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_text(
        document_text
    )

    # create embedding model
    embedding_model = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    # create vector database
    vector_db = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model
    )

    return vector_db


# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.header("📂 Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:

        with st.spinner(
            "Processing document..."
        ):

            # load text
            document_text = load_document(
                uploaded_file
            )

            # create vector db
            st.session_state.vector_db = (
                create_vector_database(
                    document_text
                )
            )

        st.success(
            "✅ Document processed successfully!"
        )

    # clear chat button
    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# =========================================
# DISPLAY CHAT HISTORY
# =========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# =========================================
# USER INPUT
# =========================================

user_prompt = st.chat_input(
    "Ask something about your document..."
)


# =========================================
# HANDLE USER MESSAGE
# =========================================

if user_prompt:

    # no document uploaded
    if st.session_state.vector_db is None:

        st.warning(
            "⚠ Please upload a document first."
        )

        st.stop()

    # display user message
    st.chat_message("user").markdown(
        user_prompt
    )

    # save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })

    # =====================================
    # RETRIEVE RELEVANT DOCUMENT CHUNKS
    # =====================================

    retrieved_docs = (
        st.session_state.vector_db
        .similarity_search(
            user_prompt,
            k=4
        )
    )

    context = "\n\n".join([
        doc.page_content
        for doc in retrieved_docs
    ])

    # =====================================
    # CONVERSATION HISTORY
    # =====================================

    conversation_history = ""

    for msg in st.session_state.messages:

        conversation_history += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    # =====================================
    # FINAL PROMPT
    # =====================================

    full_prompt = f"""
You are an AI document assistant.

Answer the user's question ONLY
using the provided document context.

If the answer is not available
in the document context, say:

"I could not find this information in the document."

==================================
DOCUMENT CONTEXT:
{context}
==================================

CHAT HISTORY:
{conversation_history}

USER QUESTION:
{user_prompt}
"""

    # =====================================
    # ASSISTANT RESPONSE
    # =====================================

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        full_response = ""

        try:

            # stream response from ollama
            stream = ollama.chat(
                model="llama3",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful AI "
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

            # streaming tokens
            for chunk in stream:

                content = (
                    chunk["message"]["content"]
                )

                full_response += content

                message_placeholder.markdown(
                    full_response + "▌"
                )

            # final clean output
            message_placeholder.markdown(
                full_response
            )

        except Exception as error:

            full_response = (
                f"❌ Error: {str(error)}"
            )

            message_placeholder.markdown(
                full_response
            )

    # =====================================
    # SAVE ASSISTANT RESPONSE
    # =====================================

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

