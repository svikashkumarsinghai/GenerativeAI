from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name='BAAI/bge-small-en-v1.5')

documents = [
    "Delhi is the capital of India",
    "Kolkata is the capital of West Bengal",
    "Paris is the capital of France"
]

vector = embedding.embed_documents(documents)

#print(str(vector))
print(len(vector))      # 3 documents
print(len(vector[0]))   # 384 dimensions