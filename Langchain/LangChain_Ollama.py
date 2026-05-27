import os
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="smollm2:latest",
    temperature=0,
)

response = llm.invoke("What is Machine Learning")

print(response.content)