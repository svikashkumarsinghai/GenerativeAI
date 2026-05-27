import streamlit as st
import ollama
from docx import Document
from pypdf import PdfReader
import tempfile


# -----------------------------
# READ FILE FUNCTIONS
# -----------------------------

def read_txt(file):
    return file.read().decode("utf-8")


def read_docx(file):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text


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
        return None


# -----------------------------
# ASK OLLAMA
# -----------------------------

def ask_ollama(document_text, question, model="smollm2:latest"):

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY from the provided document.

DOCUMENT:
{document_text}

QUESTION:
{question}
"""

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -----------------------------
# STREAMLIT UI
# -----------------------------

st.set_page_config(page_title="Document Chat", layout="wide")

st.title("📄 Chat with Your Document")
st.write("Upload a PDF, DOCX, or TXT file and ask questions.")

uploaded_file = st.file_uploader(
    "Upload Document",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:

    document_text = load_document(uploaded_file)

    st.success("Document loaded successfully!")

    question = st.text_input("Ask a question about the document")

    if st.button("Get Answer"):

        if question:

            with st.spinner("Thinking..."):

                answer = ask_ollama(document_text, question)

                st.markdown("## Answer")
                st.write(answer)

        else:
            st.warning("Please enter a question.")