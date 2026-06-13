from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

llm = OpenAI(model='gpt-5.4-mini', temperature=0.9, max_completion_tokens=10)

result = llm.invoke("What is the capital of India")

print(result)