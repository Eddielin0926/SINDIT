import os
from unicodedata import name
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from dtwin.dttypes import dtTypes
import networkx as nx
import simpy
import configparser
import py2neo
import environment.settings as stngs
from enum import Enum, unique

# these groups a factory specific,
# they can be used for grouping machines, processes, and queues when visualizing
@unique
class dtGroups(Enum):
    NONE = 0
    CONTAINER_GROUP = 1
    BUFFER_GROUP = 2

class Machine():
    def __init__(self, name, sensors, description, type, num_parts_in, num_parts_out, amount_in, amount_out) -> None:
        self.name = name

class DigitalTwin():
    def __init__(self) -> None:
        # Required environment variables
        # - AZURE_URL: The URL to the ADT in Azure
        # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
        # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
        # - AZURE_CLIENT_SECRET: The client secret for the registered application
        self.url = os.getenv("AZURE_URL")
        print(self.url)
        self.credential = DefaultAzureCredential()
        self.service_client = DigitalTwinsClient(self.url, self.credential)

    def get_twins(self, query: str):
        return self.service_client.query_twins(query)

    def get_relationship(self, model_id):
        return self.service_client.list_relationships(model_id)

# TODO: 'name' property should be remove from the dtdl file


class adtFac():
    def __init__(self, name='SINTEF factory', graph=nx.DiGraph(), digital_twin=DigitalTwin(), env=simpy.Environment(), sim_hours=40):
        self.name = name
        self.graph = graph
        self.adt = digital_twin

        # discrete event simulation
        self.env = env
        self.sim_hours = sim_hours

        self.machines = []
        self.queues = []
        self.sensors = []
        self.parts = []
        self.groups = [e.name for e in dtGroups]

        # Creat factory graph from Azure Digital Twin
        self.create_factory_graph()

    # define the machines, processes, sensors, and queues
    def create_factory_graph(self):
        sensors = []
        machines = []
        queues = []

        query = 'SELECT * FROM digitaltwins WHERE IS_DEFINED(process)'
        twins = self.adt.get_twins(query)
        # Classify the twins
        for twin in twins:
            if twin['$metadata']['$model'] == "dtmi:com:azure:Adt:Sensor;1":
                sensors.append(twin)
            elif twin['$metadata']['$model'] == "dtmi:com:azure:Adt:Machine;1":
                machines.append(twin)

        dt_sensors = []
        for sensor in sensors:
            pass
            # print(sensor['$dtId'])
            # dt_sensors.append(dtSensor(sensor['$dtId'], 'temperature'))
        self.sensors = dt_sensors

        dt_machines = []
        for machine in machines:
            # Find every relateship for the machine
            relationship = self.adt.get_relationship(machine['$dtId'])
            contain_sensors = []
            for relp in relationship:
                print(relp)
                if relp['$relationshipName'] == 'containSensor':
                    contain_sensors.append(relp['$targetId'])
                elif relp['$relationshipName'] == 'nextMachine':
                    queues.append(relp)

            dt_machines.append(
                Machine(name=machine['$dtId'],
                        sensors=filter(
                            lambda s: s.name in contain_sensors, dt_sensors),
                        description=machine['description'],
                        type=dtTypes(int(machine['type'])),
                        num_parts_in=machine['numPartsIn'],
                        num_parts_out=machine['numPartsOut'],
                        amount_in=machine['amountIn'],
                        amount_out=machine['amountOut']))
        self.machines = dt_machines

        dt_queues = []
        for queue in queues:
            print('{')
            print('from: ', self.get_machine_by_name(queue['$sourceId']))
            print('to: ', self.get_machine_by_name(queue['$targetId']))
            print('capacity: ', queue['capacity'])
            print('amount: ', 0)
            print('name: ', queue['$relationshipId'])
            print('qtype: ', dtTypes.CONTAINER)
            print('description: ', 'Queue')
            print('}')
            # TODO: The amount and type are not defined
            # dt_queues.append(
            #     dtQueue(frm=self.get_machine_by_name(queue['$sourceId']),
            #             to=self.get_machine_by_name(queue['$targetId']),
            #             capacity=queue['capacity'],
            #             amount=0,
            #             name=queue['$relationshipId'],
            #             qtype=dtTypes.CONTAINER,
            #             description='Queue'))
        self.queues = dt_queues

        return True

    def get_machine_by_name(self, name=''):
        for m in self.machines:
            if m.name == name:
                return m


def main():
    # Get digital twin data and create factory
    adtfac = adtFac(name='test-factory')


if __name__ == '__main__':
    main()
