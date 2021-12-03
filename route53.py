# import boto3

# from saleor.core.exceptions import DomainIsExist

# client = boto3.client('route53',
#     aws_access_key_id="AKIAY5IP4U6KWOLKAUG6",
#     aws_secret_access_key="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",
# )

# # response = client.list_resource_record_sets(
# #     HostedZoneId='Z0262282S9NCMR75O7T9'
# # )
# def check_exist_record(name):
#     response = client.list_resource_record_sets(
#         HostedZoneId='Z0262282S9NCMR75O7T9'
#     )
#     for obj in response.get('ResourceRecordSets'):
#         print(obj)

#     # if any(obj['Name'] == name+'.' for obj in response.get('ResourceRecordSets')):
#     #     raise DomainIsExist()
#     # else:
#     #     pass

# def create_new_record(name):
#     check_exist_record(name)
#     response = client.change_resource_record_sets(
#         ChangeBatch={
#             'Changes': [
#                 {
#                     'Action': 'CREATE',
#                     'ResourceRecordSet': {
#                         'Name': name,
#                         'ResourceRecords': [
#                             {
#                                 'Value': '3.66.10.99',
#                             },
#                         ],
#                         'TTL': 60,
#                         'Type': 'A',
#                     },
#                 },
#             ],
#             'Comment': 'Web Server',
#         },
#         HostedZoneId='Z0262282S9NCMR75O7T9',
#     )
#     if(response):
#         print("successs", response)
#     else:
#         print("faillllll")
# check_exist_record("asd")
# # print(response)