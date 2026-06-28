from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from tools.ec2_tool import create_ec2_instance

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

tools = [create_ec2_instance]

agent = create_react_agent(
    model=llm,
    tools=tools
)