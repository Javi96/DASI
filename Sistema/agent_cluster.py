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

from rules.main import Diet
from rules.main import ComidaFact
from rules.main import CenaFact
from rules.main import DesayunoFact
from rules.main import UserFact
from termcolor import colored
from random import choice
from pyknow import *
import pickle





from sklearn.cluster import KMeans 
import pandas as pd
import json

import sys

class ClusterRequestProtocol(FipaRequestProtocol):
    """
        Implementación del protocolo FIPA-REQUEST para el agente cluster.
    """

    def __init__(self, agent, message):
        """
            Constructor de clase.
            Parametros
            ----------
            agent : pade.core.agent.Agent
                Agente que implementa el protocolo
            mensaje : pade.acl.messages.ACLMessage
                Mensaje a enviar
        """

        super(ClusterRequestProtocol, self).__init__(agent=agent,
            message=message,
            is_initiator=True)

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
        if content[0] == 'end': # fin de ejecución, paramos el agente
            display_message(self.agent.aid.localname, 'terminando ejecucion ...')
            self.agent.pause_agent()
        
        if content[0] == 'cluster_request': # petición al cluster para completar un perfil
            user_profile = content[1]
            res = self.agent.fill_group(user_profile['age'], user_profile['height'], user_profile['weight'])

            display_message(self.agent.aid.localname, 'generando perfil ....')
            sender = message.sender
            reply = message.create_reply()
            reply.set_performative(ACLMessage.AGREE)
            reply.set_content(pickle.dumps(['acceptada la peticion']))
            self.agent.send(reply) 

            message = ACLMessage(ACLMessage.INFORM)
            message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            message.add_receiver(sender)
            message.set_content(pickle.dumps(['user_profile', res]))
            self.agent.send(message)

    def handle_inform(self, message):
        """
            Procesa los mensajes con performativa ACLMessage.INFORM.
            Parametros
            ----------
            message : pade.acl.messages.ACLMessage
                Mensaje a procesar
        """

        # deserializamos el contenido del mensaje
        content = pickle.loads(message.content)
        if content[0] == 'response_users': # el contenido son los perfiles de usuario
            self.agent.init_cluster(content[1])
            display_message(self.agent.aid.localname, 'se ha recibido la información de los usuarios')
        

class Cluster(Agent):
    """
        Clase que define al agente cluster. Implementa el protocolo de comunicacion
        FIPA-REQUEST.
    """

    def __init__(self, aid, message):
        """
            Constructor de clase.
            Parametros
            ----------
            aid : pade.acl.aid.AID
                Identificador del agente
            mensaje : pade.acl.messages.ACLMessage
                Mensaje a enviar
        """

        super(Cluster, self).__init__(aid=aid, debug=False)
        self.intents_cluster= ['tipo_plato_dieta']

        self.call_later(8.0, self.launch_protocol, message)

    def launch_protocol(self, message):
        """
            Añade y configura el protocolo FIPA-REQUEST del agente.
            Parametros
            ----------
            message : pade.acl.messages.ACLMessage
                Mensaje a enviar
        """

        self.protocol = ClusterRequestProtocol(self, message)
        self.behaviours.append(self.protocol)
        self.protocol.on_start()
    
    def init_cluster(self, data):
        """
            Crea e inicializa el cluster de perfiles.
            Parametros
            ----------
            data : list
                datos a usar para crear el cluster
        """

        self.data = data
        df_main = pd.DataFrame.from_dict(self.data, orient='columns')

        self.df = df_main[['age', 'height', 'weight']]

        clusters = 10
        self.kmeans = KMeans(n_clusters = clusters) 
        self.kmeans.fit(self.df) 

        self.df["cluster"] = self.kmeans.labels_

    def asign_cluster(self, fill_age, fill_height, fill_weight):
        """
            Rellena el perfil de usuario con la media de los valores del cluster si es necesario.
            Parametros
            ----------
            fill_age : float
                Edad del usuario
            fill_height : float
                Altura del usuario
            fill_weight : float
                Peso del usuario
        """
        
        # Si algún campo no se ha rellenado se completa con la media global
        if fill_age == "":
            fill_age = self.df["age"].mean()
        if fill_height == "":
            fill_height = self.df["height"].mean()
        if fill_weight == "":
            fill_weight = self.df["weight"].mean()
            
        # Comprobamos a qué cluster pertenece el usuario
        return self.kmeans.predict([[fill_age, fill_height, fill_weight]])

    def fill_group(self, fill_age, fill_height, fill_weight):
        """
            Rellena el perfil de usuario con la media del cluster asignado al usuario.
            Parametros
            ----------
            fill_age : float
                Edad del usuario
            fill_height : float
                Altura del usuario
            fill_weight : float
                Peso del usuario
        """

        # Comprobamos a qué cluster pertenece el usuario    
        fill_cluster = self.asign_cluster(fill_age, fill_height, fill_weight)
        
        # Ajustamos la información respecto a los miembros del mismo cluster
        filter_cluster = self.df['cluster'] == fill_cluster[0]
        aux = self.df[filter_cluster]
        
        if fill_age == "":
            fill_age = aux["age"].mean()
        if fill_height == "":
            fill_height = aux["height"].mean()
        if fill_weight == "":
            fill_weight = aux["weight"].mean()
            
        # Devolvemos un perfil completo
        return [round(fill_age), round(fill_height, 2), round(fill_weight, 2)]