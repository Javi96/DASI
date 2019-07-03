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

import sys

class RulesRequestProtocol(FipaRequestProtocol):
    """
        Implementación del protocolo FIPA-REQUEST para el agente de reglas.
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

        super(RulesRequestProtocol, self).__init__(agent=agent,
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
        if content[0] == 'end': # terminamos la ejecución
            display_message(self.agent.aid.localname, 'terminando ejecucion ...')
            self.agent.pause_agent()

        if content[0] in self.agent.intents_rules:
            
            sender = message.sender
            reply = message.create_reply()
            reply.set_performative(ACLMessage.AGREE)
            reply.set_content(pickle.dumps(['acceptada la peticion']))
            self.agent.send(reply)

            self.agent.engine.reset()
            self.agent.define_facts()
            

            res = {}
            # procesamos en funcion de cada intent y añadimos los fatcs necesarios
            # en funcion de la intent y los datos disponiebles
            if content[0] == 'tipo_plato_dieta':
                display_message(self.agent.aid.localname, 'generando un plato ...')
                self.agent.engine.declare(Fact(intent=content[1][0]))
                self.agent.engine.run()
                res = choice(self.agent.engine.get_tipo_plato_dieta())
                res = {'primero':res['primero'], 'segundo':res['segundo'], 'postre':res['postre']}


            elif content[0] == 'pedir_plato_alergia':
                display_message(self.agent.aid.localname, 'generando un plato sin alergias ...')
                self.agent.engine.declare(UserFact(data=content[1]))
                self.agent.engine.run()
                res = choice(self.agent.engine.get_pedir_plato_alergia())
                res = {'primero':res['primero'], 'segundo':res['segundo'], 'postre':res['postre']}


            elif content[0] == 'recomendar_ingrediente':
                display_message(self.agent.aid.localname, 'generando un plato para un ingrediente ...')
                self.agent.engine.declare(Fact(intent=content[1][0]))
                self.agent.engine.run()
                res = choice(self.agent.engine.get_recomendacion_ingrediente())
                res = {'primero':res['primero'], 'segundo':res['segundo'], 'postre':res['postre']}


            elif content[0] == 'sencillo':
                display_message(self.agent.aid.localname, 'generando un plato sencillo de preparar ...')

                self.agent.engine.declare(Fact(intent=content[0]))
                self.agent.engine.run()
                res = choice(self.agent.engine.get_platos_sencillos())
                res = {'primero':res['primero'], 'segundo':res['segundo'], 'postre':res['postre']}
                
            elif content[0] == 'peso':

                display_message(self.agent.aid.localname, 'generando una dieta ...')
                self.agent.engine.declare(Fact(intent='baja_grasas'))
                self.agent.engine.declare(UserFact(data=content[1]))
                self.agent.engine.run()

                des = choice(self.agent.engine.get_desayunos())
                com = choice(self.agent.engine.get_comidas())
                cen = choice(self.agent.engine.get_cenas())
                res = {'desayuno':des, 'comida':com, 'cena':cen}

            message = ACLMessage(ACLMessage.INFORM)
            message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
            message.add_receiver(sender)
            message.set_content(pickle.dumps([content[0], res]))            
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
        if content[0] == 'response_plates':
            display_message(self.agent.aid.localname, 'se ha recibido la información de los platos')
            self.agent.facts = content[1]



class Rules(Agent):
    """
        Clase que define al agente reglas. Implementa el protocolo de comunicacion
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

        super(Rules, self).__init__(aid=aid, debug=False)
        self.intents_rules= [
            'tipo_plato_dieta',
            'pedir_plato_alergia',
            'recomendar_ingrediente',
            'sencillo',
            'peso']
        self.engine = Diet()
        self.facts = []
        self.call_later(8.0, self.launch_protocol, message)

    def launch_protocol(self, message):
        """
            Añade y configura el protocolo FIPA-REQUEST del agente.
            Parametros
            ----------
            message : pade.acl.messages.ACLMessage
                Mensaje a enviar
        """

        self.protocol = RulesRequestProtocol(self, message)
        self.behaviours.append(self.protocol)
        self.protocol.on_start()

    def define_facts(self):
        """
            Rellena la memoria del engine con los hechos disponibles.
        """

        for fact in self.facts:
            if fact['tipo'] == 'comida':
                self.engine.declare(ComidaFact(
                    primero=fact['primero'], 
                    segundo=fact['segundo'], 
                    postre=fact['postre'], 
                    dieta=fact['dieta'],
                    tipo_dieta=fact['tipo_dieta'],
                    dificultad=fact['dificultad']))
            if fact['tipo'] == 'cena':
                self.engine.declare(CenaFact(
                    primero=fact['primero'], 
                    postre=fact['postre'], 
                    dieta=fact['dieta'],
                    dificultad=fact['dificultad']))
            if fact['tipo'] == 'desayuno':
                self.engine.declare(DesayunoFact(
                    fruta = fact['fruta'] if 'fruta' in fact.keys() else '', 
                    cereal = fact['cereal'] if 'cereal' in fact.keys() else '', 
                    lacteo = fact['lacteo'] if 'lacteo' in fact.keys() else '', 
                    embutido = fact['embutido'] if 'embutido' in fact.keys() else '', 
                    dieta=fact['dieta']))
