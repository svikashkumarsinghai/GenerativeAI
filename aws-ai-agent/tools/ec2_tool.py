from langchain_core.tools import tool
from services.aws_service import create_ec2

@tool
def create_ec2_instance(
    instance_name: str,
    instance_type: str = "t3.micro"
) -> str:
    """
    Create an EC2 instance in AWS.
    """
    return create_ec2(instance_name, instance_type)