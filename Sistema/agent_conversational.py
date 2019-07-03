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

import dialogflow
import os
import json
from google.protobuf.json_format import MessageToJson
from termcolor import colored


from time import sleep

import sys


GOOGLE_APPLICATION_CREDENTIALS = 'credentials_old.json'

def load_credentials():
    """
        Carga las credenciales necesarias para poder usar el API de Dialogflow

        Retorno
        -------
        dict
            Credenciales para conectarse con Dialogflow
    """

    # añadimos una variable al path
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
    with open(GOOGLE_APPLICATION_CREDENTIALS) as credentials_file:  
        credentials = json.load(credentials_file)
        return credentials

def load_data():
    """
        Carga los inputs del usuario de un fichero

        Retorno
        -------
        list
            Lista con los mensajes del usuario 
    """

    with open('data.txt', 'r', encoding='utf-8') as data:
        lines = []
        for line in data:
            lines.append(line)
    return lines

def query(project_id, session_id, texts, language_code):
    """
        Procesa una línea de texto y se la envía al API de Dialogflow para extraer 
        el intent y la información relevante.

        Parametros
        ----------
        project_id : str
            Identificador de projecto (credencial del API)
        session_id : str
            Identificador de sesión (credencial del API)
        texts : list
            Lista de un elemento con el input del usuario
        language_code : str
            Idioma a usar en el API de Dialogflow

        Retorno
        -------
        str
            Respuesta del API
        str
            Intent extraída del input
        str
            Datos relevantes
    """

    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)

        response = session_client.detect_intent(session=session, 
            query_input=query_input)
        
        parameters = response.query_result.parameters
        res_intent = None
        res_data = None
        try:
            for i in parameters.keys():
                res_intent = i
                if i in ['recomendar_ingrediente', 'marcar_favorito']:
                    res_data = list(parameters[i])
                else:
                    res_data = [parameters[i]]
        except Exception as e:
            pass  
        res_response = response.query_result.fulfillment_text
    return res_response, res_intent, res_data



class ConversationalRequestProtocol(FipaRequestProtocol):
    """
        Implementación del protocolo FIPA-REQUEST para el agente conversational.
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

        super(ConversationalRequestProtocol, self).__init__(agent=agent,
            message=message,
            is_initiator=True)

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
        if content[0] == 'response_user': # el contenido es el perfil del usuario activo
            self.agent.user = content[1][0]
            display_message(self.agent.aid.localname, 'se ha recibido información del usuario actual')

            # se envía el perfil al cluster para que sea completado si es necesario
            message = ACLMessage(ACLMessage.REQUEST)
            message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            message.add_receiver(self.agent.aids['cluster'])
            message.set_content(pickle.dumps(['cluster_request', self.agent.user]))
            self.agent.send(message)

        elif content[0] == 'user_profile': # el contenido es la respuesta del cluster
            display_message(self.agent.aid.localname, 'se ha recibido el perfil completo del cluster')
            self.agent.user['age'] = float(content[1][0])
            self.agent.user['height'] = content[1][1]
            self.agent.user['weight'] = content[1][2]
        elif content[0] == 'tipo_plato_dieta':
            display_message(self.agent.aid.localname, 'plato para una dieta ' + json.dumps(content[1]))
        elif content[0] == 'pedir_plato_alergia':
            display_message(self.agent.aid.localname, 'plato sin alergias ' + json.dumps(content[1]))
        elif content[0] == 'recomendar_ingrediente':
            display_message(self.agent.aid.localname, 'plato con recomentado en base a ingredientes ' + json.dumps(content[1]))
        elif content[0] == 'sencillo':
            display_message(self.agent.aid.localname, 'plato sencillo ' + json.dumps(content[1]))
        elif content[0] == 'peso':
            display_message(self.agent.aid.localname, 'dieta ' + json.dumps(content[1]))




class ComportTemporal(TimedBehaviour):
    """
        Comportamiento temporal implementado por el agente conversacional.
        Se ejecuta cada cierto tiempo y se encarga de envíar el input del
        usuario a otros agentes
    """

    def __init__(self, agent, time):
        """
            Constructor de clase.
            Parametros
            ----------
            agent : pade.core.agent.Agent
                Agente que implementa el protocolo
            time : float
                Tiempo de espera entre ejecución del comportamiento
        """
        super(ComportTemporal, self).__init__(agent, time)

    def on_time(self):
        """
            Método que es ejecutado de forma cíclica cada cierto tiempo.
        """
        super(ComportTemporal, self).on_time()

        if self.agent.current_request < len(self.agent.data):
            # se muestra el input del usuario y la información de Dialogflow
            print(colored('====================================================================', 'blue'))
            print('user: {}'.format(self.agent.data[self.agent.current_request]))
            responseB, intentB, dataB = query(self.agent.credentials['project_id'], '1', [self.agent.data[self.agent.current_request]], 'en')
            self.agent.current_request += 1
            print('response:  {}'.format(responseB))
            print('intent:  {}'.format(intentB))
            print('data:  {}'.format(dataB))



            # se manda un mensaje a donde proceda en base al intent detectado
            info = ACLMessage(ACLMessage.REQUEST)
            info.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)

            
            if intentB in self.agent.intents_rules: # siempre recomendar algo
                self.agent.send_to_rules(info, intentB, dataB)

            if intentB in self.agent.intents_cluster: # siempre completar perfil
                self.agent.send_to_cluster(info, intentB, dataB)

            if intentB in self.agent.intents_database: # siempre guardar datos
                self.agent.send_to_database(info, intentB, dataB)

        elif self.agent.current_request == len(self.agent.data):
            # se finaliza la ejecución de todos los agentes, incluída la del conversacional
            self.agent.current_request += 1
            end = ACLMessage(ACLMessage.REQUEST)
            end.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            end.set_content(pickle.dumps(['end']))
            end.add_receiver(self.agent.aids['database'])
            end.add_receiver(self.agent.aids['cluster'])
            end.add_receiver(self.agent.aids['rules'])
            self.agent.send(end)
            display_message(self.agent.aid.localname, 'terminando ejecucion ...')
            self.agent.pause_agent()

class Conversational(Agent):
    """
        Clase que define al agente conversacional. Implementa el protocolo de comunicacion
        FIPA-REQUEST.
    """

    def __init__(self, aid, message, aids):
        """
            Constructor de clase.
            Parametros
            ----------
            aid : pade.acl.aid.AID
                Identificador del agente
            mensaje : pade.acl.messages.ACLMessage
                Mensaje a enviar
            aids : dict
                Diccionario con los AIDs del resto de agentes
        """
        super(Conversational, self).__init__(aid=aid, debug=False)
        self.behaviours.append(ComportTemporal(self, 15))
        self.current_request = 0
        self.aids = aids
        self.intents_database = [
            'marcar_favorito',
            'pedir_plato_alergia',
            'altura',
            'peso']
        self.intents_rules= [
            'tipo_plato_dieta',
            'pedir_plato_alergia',
            'recomendar_ingrediente',
            'sencillo',
            'peso']
        self.intents_cluster = []
        self.data = {}
        self.user = {}
        self.credentials = {}
        self.credentials = load_credentials()
        self.data = load_data()
        self.call_later(10.0, self.get_user_info, message)
           
    def send_to_cluster(self, message, intent, data):
        """
            Envía un mensaje al agente cluster.
            Parametros
            ----------
            message : pade.cacl.messages.ACLMessage
                Mensaje a enviar
            intent : str
                Intent detectado por Dialogflow
            data : list
                Lista de datos a incluir en el mensaje
        """

        message.add_receiver(self.aids['cluster'])
        message.set_content(pickle.dumps(['cluster_request', self.user]))
        message.set_content(pickle.dumps(['user_profile', res]))
        self.send(message)

    def send_to_database(self, message, intent, data):
        """
            Envía un mensaje al agente base de datos.
            Parametros
            ----------
            message : pade.cacl.messages.ACLMessage
                Mensaje a enviar
            intent : str
                Intent detectado por Dialogflow
            data : list
                Lista de datos a incluir en el mensaje
        """

        message.add_receiver(self.aids['database'])
        if intent == 'marcar_favorito':
            for elem in data:
                # si ya es favorito no lo añadimos de nuevo ni actualizamos la BD
                if elem not in self.user['favourites']:
                    self.user['favourites'].append(elem)
                    message.set_content(pickle.dumps(['database_request', self.user]))
                    self.send(message)
        else:
            # en otro caso actualizamos el perfil del usuario y avisamos a la BD
            if intent == 'altura':
                self.user['height'] = data[0]
            elif intent == 'peso':
                self.user['weight'] = data[0]
            message.set_content(pickle.dumps(['database_request', self.user]))
            self.send(message)

    def send_to_rules(self, message, intent, data):
        """
            Envía un mensaje al agente reglas.
            Parametros
            ----------
            message : pade.cacl.messages.ACLMessage
                Mensaje a enviar
            intent : str
                Intent detectado por Dialogflow
            data : list
                Lista de datos a incluir en el mensaje
        """

        message.add_receiver(self.aids['rules'])
        if intent == 'altura':
            self.user['height'] = data[0]
        if intent == 'pedir_plato_alergia':
            if data[0] not in self.user['allergies']:
                self.user['allergies'].append(data[0])
            message.set_content(pickle.dumps([intent, self.user]))
        elif intent == 'peso':
            self.user['weight'] = data[0]
            self.user['imc'] = round(float(self.user['weight'])/pow(float(self.user['height']), 2), 2)
            message.set_content(pickle.dumps([intent, self.user]))
        else:
            message.set_content(pickle.dumps([intent, data]))
        self.send(message)


    def get_user_info(self, message):
        """
            Obtiene la información del usuario actual del agente base de datos.
            Parametros
            ----------
            message : pade.cacl.messages.ACLMessage
                Mensaje a enviar
        """

        self.protocol = ConversationalRequestProtocol(self, message)
        self.behaviours.append(self.protocol)
        self.protocol.on_start()