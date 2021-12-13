import boto3
import os
from saleor.core.exceptions import DomainIsExist

client = boto3.client('route53',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

# response = client.list_resource_record_sets(
#     HostedZoneId='Z0262282S9NCMR75O7T9'
# )
def check_exist_record(name):
    response = client.list_resource_record_sets(
        HostedZoneId=os.environ.get("HOSTED_ZONE_ID")
    )
    if any(obj['Name'] == name+'.' for obj in response.get('ResourceRecordSets')):
        return True
    else:
        return False

def create_new_record(name):
    # if check_exist_record(name): 
    #     raise DomainIsExist()
    response = client.change_resource_record_sets(
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'ResourceRecords': [
                            {
                                'Value': os.environ.get('STATIC_IP'),
                            },
                        ],
                        'TTL': 60,
                        'Type': 'A',
                    },
                },
            ],
            'Comment': 'Web Server',
        },
        HostedZoneId=os.environ.get("HOSTED_ZONE_ID"),
    )
    if response:
        print("successs", response)
    else:
        print("faillllll")

def delete_record(name):
    if not check_exist_record(name):
        raise DomainIsExist(message="Domain doesn't exist")
    response = client.change_resource_record_sets(
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': name,
                        'ResourceRecords': [
                            {
                                'Value': os.environ.get('STATIC_IP'),
                            },
                        ],
                        'TTL': 60,
                        'Type': 'A',
                    },
                },
            ],
            'Comment': 'delete record',
        },
        HostedZoneId=os.environ.get("HOSTED_ZONE_ID"),
    )
    print(response)

def update_record(name,old_name):
    delete_record(old_name)
    if check_exist_record(name):
        raise DomainIsExist(message="Domain does exist")
    create_new_record(name)