from agent.ec2_agent import agent

response = agent.invoke(
    {
        "messages": [
            (
                "user",
                "Create an EC2 instance named employee-api-server using t3.micro"
            )
        ]
    }
)

print(response["messages"][-1].content)