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


from pymongo import MongoClient
from pprint import pprint
from termcolor import colored
import json
import pickle

from bson.objectid import ObjectId

import sys

class DatabaseRequestProtocol(FipaRequestProtocol):
    """
        Implementación del protocolo FIPA-REQUEST para el agente base de datos.
    """

    def __init__(self, agent):
        """
            Constructor de clase.
            Parametros
            ----------
            agent : pade.core.agent.Agent
                Agente que implementa el protocolo
        """

        super(DatabaseRequestProtocol, self).__init__(agent=agent,
            message=None,
            is_initiator=False)
        
    def handle_request(self, message):
        """
            Procesa los mensajes con performativa ACLMessage.REQUEST.
            Parametros
            ----------
            message : pade.acl.messages.ACLMessage
                Mensaje a procesar
        """

        # deserializamos el contenido del mensaje
        content = pickle.loads(message.content)
        display_message(self.agent.aid.localname, 'petición recibida de ' + str(message.sender.name))
        if content[0] == 'end':
            display_message(self.agent.aid.localname, 'terminando ejecucion ...')
            self.agent.pause_agent()

        if content[0] == 'request_plates':
            self.response_plates(message)
        elif content[0] == 'request_users':
            self.response_users(message)
        elif content[0] == 'request_user':
            self.response_user(message)
        elif content[0] == 'database_request':
            display_message(self.agent.aid.localname, 'se ha actualizado la información del usuario')
            self.agent.collection_users.replace_one({'_id':content[1]['_id']}, content[1])


    def response_plates(self, message):
        """
            Envía los platos de la base de datos al agente solicitante.
            Parametros
            ----------
            message : pade.acl.messages.ACLMessage
                Mensaje a procesar
        """

        display_message(self.agent.aid.localname, 'obteniendo platos de la base de datos')
        # obtenemos todos los platos de la BD
        plates = [x for x in self.agent.collection_plates.find()]

        sender = message.sender
        reply = message.create_reply()
        reply.set_performative(ACLMessage.AGREE)
        reply.set_content(pickle.dumps(['acceptada la peticion']))
        
        message = ACLMessage(ACLMessage.INFORM)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(sender)
        message.set_content(pickle.dumps(['response_plates', plates]))

        self.agent.send(message)

        self.agent.send(reply)

    def response_users(self, message):
        """
            Envía todos los usuarios de la base de datos al agente solicitante.
            Parametros
            ----------
            message : pade.acl.messages.ACLMessage
                Mensaje a procesar
        """
        display_message(self.agent.aid.localname, 'obteniendo usuarios de la base de datos')
        # obtenemso todos los usuarios
        users = [x for x in self.agent.collection_users.find()]

        sender = message.sender
        reply = message.create_reply()
        reply.set_performative(ACLMessage.AGREE)
        reply.set_content(pickle.dumps(['acceptada la peticion']))
        

        message = ACLMessage(ACLMessage.INFORM)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(sender)
        message.set_content(pickle.dumps(['response_users', users]))

        self.agent.send(message)

        self.agent.send(reply)

    def response_user(self, message):
        """
            Envía la información del usuario actual de la sesión al agente solicitante.
            Parametros
            ----------
            message : pade.acl.messages.ACLMessage
                Mensaje a procesar
        """

        display_message(self.agent.aid.localname, 'obteniendo información del usuario actual de la base de datos')
        
        # extrae de la base de datos el perfil de usuario numero 1
        user = [self.agent.collection_users.find_one({"_id": '1'})]
   
        sender = message.sender
        reply = message.create_reply()
        reply.set_performative(ACLMessage.AGREE)
        reply.set_content(pickle.dumps(['acceptada la peticion']))
        

        message = ACLMessage(ACLMessage.INFORM)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(sender)
        message.set_content(pickle.dumps(['response_user', user]))

        self.agent.send(message)

        self.agent.send(reply)

class Database(Agent):
    """
        Clase que define al agente base de datos. Implementa el protocolo de comunicacion
        FIPA-REQUEST.
    """

    def __init__(self, aid):
        """
            Constructor de clase.
            Parametros
            ----------
            aid : pade.acl.aid.AID
                Identificador del agente
        """

        super(Database, self).__init__(aid=aid, debug=False)
        self.client = None
        self.protocol = DatabaseRequestProtocol(self)
        self.behaviours.append(self.protocol)

        self.connect()
        self.load_users()
        self.load_plates()

    def load_users(self):
        """
            Vuelca los usuarios en una colleción de la base de datos.
        """

        with open('mongo/users.json', 'r', encoding='utf-8') as users:
            self.collection_users.drop()
            data = json.loads(users.read())
            self.collection_users.insert_many(data)

    def connect(self):
        """
            Establece conexión con la base de datos y accede a las collecciones pertinentes.
        """

        self.client = MongoClient("localhost", 27017, maxPoolSize=50)
        db = self.client.localhost
        self.collection_users = db['users']
        self.collection_plates = db['plates']


    def load_plates(self):
        """
            Vuelca los platos en una colleción de la base de datos.
        """

        with open('mongo/plates.json', 'r', encoding='utf-8') as plates:
            self.collection_plates.drop()
            data = json.loads(plates.read())
            self.collection_plates.insert_many(data)
