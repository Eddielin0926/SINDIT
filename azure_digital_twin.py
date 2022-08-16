import os
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient
from dtwin.dtmachine import dtMachine
from dtwin.dtqueue import dtQueue
from dtwin.dtsensor import dtSensor
from dtwin.dttypes import dtTypes
import networkx as nx
from dtwin.dtfactory import dtFactory
import simpy
import configparser
import py2neo
import environment.settings as stngs
from enum import Enum, unique

# Read Config
config = configparser.ConfigParser()
config.read(stngs.BASE_DIR+'/sindit.cfg')
NEO4J_URI = stngs.NEO4J_FACTORY
NEO4J_USER = config['factory-neo4j']['user']
NEO4J_PASS = config['factory-neo4j']['pass']
NEED_AUTH = config['factory-neo4j']['need_auth']

PARTS_NEO4J_URI = stngs.NEO4J_PARTS
PARTS_NEO4J_USER = config['parts-neo4j']['user']
PARTS_NEO4J_PASS = config['parts-neo4j']['pass']
PARTS_NEED_AUTH = config['parts-neo4j']['need_auth']


# these groups a factory specific,
# they can be used for grouping machines, processes, and queues when visualizing
@unique
class dtGroups(Enum):
    NONE = 0
    CONTAINER_GROUP = 1
    BUFFER_GROUP = 2


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

# TODO: 'name' property should be remove from the dtdl file


class adtFac(dtFactory):
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
            dt_sensors.append(dtSensor(sensor['$dtId'], 'temperature'))
        self.sensors = dt_sensors

        dt_machines = []
        for machine in machines:
            # Find every relateship for the machine
            relationship = self.adt.get_relationship(twin['$dtId'])
            contain_sensors = []
            for relp in relationship:
                if relp['$relationshipName'] == 'containSensor':
                    contain_sensors.append(relp['$targetId'])
                elif relp['$relationshipName'] == 'nextMachine':
                    queues.append(relp)

            dt_machines.append(
                dtMachine(name=machine['$dtId'],
                          sensors=filter(
                              lambda s: s.name in contain_sensors, dt_sensors),
                          description=machine['description'],
                          type=machine['type'],  # FIXME: use dtType instead
                          num_parts_in=machine['numPartsIn'],
                          num_parts_out=machine['numPartsOut'],
                          amount_in=machine['amountIn'],
                          amount_out=machine['amountOut']))
        self.machines = dt_machines

        dt_queues = []
        for queue in queues:
            # TODO: The amount and type are not defined
            dt_queues.append(
                dtQueue(frm=self.get_machine_by_name(queue['$sourceId']),
                        to=self.get_machine_by_name(queue['$targetId']),
                        capacity=queue['capacity'],
                        amount=0,
                        name=queue['$relationshipId'],
                        qtype=dtTypes.CONTAINER,
                        description='Queue'))
        self.queues = dt_queues

        # make a graph
        self.populate_networkx_graph()

        # setting up the parts inventory
        NUM_OF_PARTS = 0
        init_parts = []
        if PARTS_NEED_AUTH.lower() == 'true':
            part_g = py2neo.Graph(PARTS_NEO4J_URI,
                                  user=PARTS_NEO4J_USER,
                                  password=PARTS_NEO4J_PASS)
        else:
            part_g = py2neo.Graph(PARTS_NEO4J_URI)

        # start fresh
        part_g.delete_all()

        # set the parts graph db as we have a buffer there
        self.get_machine_by_name('M4').py2neo_graph = part_g
        self.get_machine_by_name('M5').py2neo_graph = part_g

        ret_val = self.populate_networkx_graph()
        return True


def main():
    # Get digital twin data and create factory
    adtfac = adtFac(name='test-factory')

    # store in neo4j
    adtfac.serialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI,
                     user=NEO4J_USER, password=NEO4J_PASS, need_auth=NEED_AUTH)

    # store as json file
    adtfac.serialize(serial_type="json",
                     file_path_or_uri=f'{adtFac.name}.json')


if __name__ == '__main__':
    main()
