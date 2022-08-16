import json
import os
from platform import machine
from pstats import SortKey
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from dtwin.dttypes import dtTypes

class DigitalTwin():
    def __init__(self) -> None:
        # Required environment variables
        # - AZURE_URL: The URL to the ADT in Azure
        # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
        # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
        # - AZURE_CLIENT_SECRET: The client secret for the registered application
        self.url = os.getenv("AZURE_URL")
        self.credential = DefaultAzureCredential()
        self.service_client = DigitalTwinsClient(self.url, self.credential)

    def get_twins(self, query: str):
        return self.service_client.query_twins(query)

    def get_relationship(self, model_id):
        return self.service_client.list_relationships(model_id)


def main():
     # Create client for digital twin to get data
    adt = DigitalTwin()

    sensors = []
    machines = []

    query = 'SELECT * FROM digitaltwins WHERE IS_DEFINED(process)'
    twins = adt.get_twins(query)
    for twin in twins:
        if twin['$metadata']['$model'] == "dtmi:com:azure:Adt:Sensor;1":
            sensors.append(twin)
        elif twin['$metadata']['$model'] == "dtmi:com:azure:Adt:Machine;1":
            machines.append(twin)

    for m in machines:
        relps = adt.get_relationship(m['$dtId'])
        for relp in relps:
            print(json.dumps(relp, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
