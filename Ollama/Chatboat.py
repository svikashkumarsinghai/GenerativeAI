import streamlit as st
import ollama
from docx import Document
from pypdf import PdfReader


# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Document Chatbot",
    layout="wide"
)

st.title("📄 AI Document Chatbot")


# -----------------------------------
# SESSION STATE
# -----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_text" not in st.session_state:
    st.session_state.document_text = ""


# -----------------------------------
# READ DOCUMENT FUNCTIONS
# -----------------------------------

def read_txt(file):
    return file.read().decode("utf-8")


def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def read_pdf(file):
    pdf = PdfReader(file)

    text = ""

    for page in pdf.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text


def load_document(uploaded_file):

    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "txt":
        return read_txt(uploaded_file)

    elif file_type == "docx":
        return read_docx(uploaded_file)

    elif file_type == "pdf":
        return read_pdf(uploaded_file)

    else:
        return ""


# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:

    st.header("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose file",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file:

        st.session_state.document_text = load_document(uploaded_file)

        st.success("Document uploaded!")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# -----------------------------------
# SHOW CHAT HISTORY
# -----------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------------
# CHAT INPUT
# -----------------------------------

user_prompt = st.chat_input("Ask something about your document...")

if user_prompt:

    # show user message
    st.chat_message("user").markdown(user_prompt)

    # save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })

    # prepare conversation history
    conversation_history = ""

    for msg in st.session_state.messages:
        conversation_history += f"{msg['role']}: {msg['content']}\n"


    # final prompt
    full_prompt = f"""
You are an AI assistant.

Use the document and chat history to answer.

DOCUMENT:
{st.session_state.document_text}

CHAT HISTORY:
{conversation_history}

USER QUESTION:
{user_prompt}
"""


    # assistant response area
    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        full_response = ""

        # streaming response
        stream = ollama.chat(
            model="smollm2:latest",
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            stream=True
        )

        for chunk in stream:

            content = chunk["message"]["content"]

            full_response += content

            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)


    # save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })