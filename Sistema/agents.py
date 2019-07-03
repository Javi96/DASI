from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from sys import argv
from pade.acl.filters import Filter
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol

from pade.behaviours.protocols import TimedBehaviour

from datetime import datetime

from time import sleep


from agent_database import Database
from agent_rules import Rules
from agent_cluster import Cluster
from agent_conversational import Conversational

import pickle


if __name__ == '__main__':
    agents = list()
    
    # AIDs de los agentes involucrados en el proyecto
    database_aid = AID(name='database_agent@localhost:8095')
    rules_aid = AID(name='rules_agent@localhost:8096')
    cluster_aid = AID(name='cluster_agent@localhost:8097')
    conversation_aid = AID(name='conversation_agent@localhost:8098')
    aid_rem = AID(name='remitente@localhost:8099')



    database_agent = Database(database_aid)
    
    # mensaje para solicitar los platos de la base de datos
    message_rules = ACLMessage(ACLMessage.REQUEST)
    message_rules.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message_rules.add_receiver(database_agent.aid)
    message_rules.set_content(pickle.dumps(['request_plates']))

    # mensaje para solicitar los usuarios de la base de datos
    message_cluster = ACLMessage(ACLMessage.REQUEST)
    message_cluster.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message_cluster.add_receiver(database_agent.aid)
    message_cluster.set_content(pickle.dumps(['request_users']))

    # mensaje para solicitar la información del usuario de la base de datos
    message_conversational = ACLMessage(ACLMessage.REQUEST)
    message_conversational.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    message_conversational.add_receiver(database_agent.aid)
    message_conversational.set_content(pickle.dumps(['request_user']))

    rules_agent = Rules(rules_aid, message_rules)
    cluster_agent = Cluster(cluster_aid, message_cluster)


    aids = {'database':database_agent.aid, 'rules':rules_agent.aid, 'cluster':cluster_agent.aid}

    conversation_agent = Conversational(conversation_aid, message_conversational, aids)

    
    agents.append(database_agent)
    agents.append(rules_agent)
    agents.append(cluster_agent)
    agents.append(conversation_agent)

    
    start_loop(agents)