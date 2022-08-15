import os
import json
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient

# DefaultAzureCredential supports different authentication mechanisms and determines the appropriate credential type based of the environment it is executing in.
# It attempts to use multiple credential types in an order until it finds a working credential.

# - AZURE_URL: The URL to the ADT in Azure
url = os.getenv("AZURE_URL")

# DefaultAzureCredential expects the following three environment variables:
# - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
# - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
# - AZURE_CLIENT_SECRET: The client secret for the registered application
credential = DefaultAzureCredential()
service_client = DigitalTwinsClient(url, credential)

process_list = []
edge_list = []

query_expression = 'SELECT * FROM digitaltwins WHERE IS_DEFINED(process)'
query_result = service_client.query_twins(query_expression)

for twin in query_result:
    if not twin['process'] in process_list:
        process_list.append(twin['process'])

    edges = service_client.list_relationships(twin['$dtId'])
    for edge in edges:
        print(json.dumps(edge, indent=4, sort_keys=True))
        edge_list.append(edge)

print("process_list = ", process_list)
print("edge_list = ", edge_list)
