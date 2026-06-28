import boto3
from config.settings import AWS_REGION

ec2_client = boto3.client(
    "ec2",
    region_name=AWS_REGION
)

def create_ec2(
        instance_name,
        instance_type="t3.micro",
        ami_id="ami-0f918f7e67a3323f0"  # Amazon Linux 2023 (verify for region)
):
    response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": instance_name
                    }
                ]
            }
        ]
    )

    instance_id = response["Instances"][0]["InstanceId"]

    return (
        f"EC2 Instance created successfully.\n"
        f"Instance ID: {instance_id}\n"
        f"Instance Type: {instance_type}"
    )