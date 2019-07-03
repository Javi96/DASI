from termcolor import colored
from random import choice
from pyknow import *

class UserFact(Fact):
    """
        Clase que hereda de Fact y que define a un usuario.
    """
    pass

class CenaFact(Fact):
    """
        Clase que hereda de Fact y que define las cenas.
    """
    pass

class ComidaFact(Fact):
    """
        Clase que hereda de Fact y que define las comidas.
    """
    pass

class DesayunoFact(Fact):
    """
        Clase que hereda de Fact y que define los desayunos.
    """
    pass

class Diet(KnowledgeEngine):
    """
        Clase que hereda de KnowledgeEngine encargada de ejecutar el motor de reglas
    """ 

    """
        Atributos de clase
    """
    desayunos = list()
    comidas = list()    
    cenas = list()
    tipo_plato_dieta = list()
    pedir_plato_alergia = list()
    recomendacion_ingrediente = list()
    platos_sencillos = list()

    def get_platos_sencillos(self):
        """
            Devuelve una lista de platos sencillos de preparar.

            Retorno
            -------
            list
                lista de platos sencillos de preparar
        """
        return self.platos_sencillos 

    def get_recomendacion_ingrediente(self):
        """
            Devuelve una lista de platos sencillos de preparar.

            Retorno
            -------
            list
                lista de platos sencillos de preparar
        """
        return self.recomendacion_ingrediente 

    def get_pedir_plato_alergia(self):
        """
            Devuelve una lista de platos aptos para una alergia.

            Retorno
            -------
            list
                lista de platos aptos para una alergia
        """
        return self.pedir_plato_alergia 

    def get_tipo_plato_dieta(self):
        """
            Devuelve una lista de platos aptos para una dieta.

            Retorno
            -------
            list
                lista de platos aptos para una dieta
        """
        return self.tipo_plato_dieta 

    def get_desayunos(self):
        """
            Devuelve una lista de desayunos.

            Retorno
            -------
            list
                lista de desayunos
        """
        return self.desayunos

    def get_comidas(self):
        """
            Devuelve una lista de comidas.

            Retorno
            -------
            list
                lista de comidas
        """
        return self.comidas

    def get_cenas(self):
        """
            Devuelve una lista de cenas.

            Retorno
            -------
            list
                lista de platos cenas
        """
        return self.cenas

    @Rule(
        AS.desayuno << DesayunoFact(
            fruta = MATCH.fruta, 
            cereal = MATCH.cereal,
            lacteo = MATCH.lacteo,
            embutido = MATCH.embutido,
            dieta = MATCH.intent
            ),
        Fact(
            intent = MATCH.intent
            ),
        UserFact(
            data__name = MATCH.name,
            data__imc = MATCH.imc & GE(24.9),
            data__allergies = MATCH.allergies
            ))
    def match_desayunos(self, desayuno):
        """
            Filtra los desayunos denifidos en el sistema en base a una intent y el perfil del usuario.
            Parametros
            ----------
            desayuno : DesayunoFact
                Desayuno que ha encajado en la regla
        """

        self.desayunos.append(desayuno)

    @Rule(
        AS.cena << CenaFact(
            primero= MATCH.primero,
            postre = MATCH.postre,
            dieta = MATCH.intent
            ),
        Fact(
            intent = MATCH.intent
            ),
        UserFact(
            data__name = MATCH.name,
            data__imc = MATCH.imc & GE(24.9),
            data__allergies = MATCH.allergies
            ))
    def match_cenas(self, cena, primero, postre, allergies):
        """
            Filtra las cenas denifidas en el sistema en base a un intent y el perfil del usuario.
            Parametros
            ----------
            cena : CenaFact
                Cena que ha encajado en la regla
            primero : string
                Plato que ha encajado con la regla
            postre : string
                Plato que ha encajado con la regla
            allergies : list
                Lista de alergias del usuario
        """

        allergies = list(allergies)
        if primero not in allergies and postre not in allergies:
            self.cenas.append(cena)

    @Rule(
        AS.comida << ComidaFact(
            primero= MATCH.primero, 
            segundo= MATCH.segundo, 
            postre = MATCH.postre,
            dieta = MATCH.intent
            ),
        Fact(
            intent = MATCH.intent
            ),
        UserFact(
            data__name = MATCH.name,
            data__imc = MATCH.imc & GE(24.9),
            data__allergies = MATCH.allergies
            ))
    def match_comidas(self, comida):
        """
            Filtra las comidas denifidas en el sistema en base a un intent y el perfil del usuario.
            Parametros
            ----------
            comida : CenaFact
                Comida que ha encajado en la regla
        """

        self.comidas.append(comida)


    @Rule(
        AS.comida << ComidaFact(
            primero= MATCH.primero, 
            segundo= MATCH.segundo, 
            postre = MATCH.postre,
            tipo_dieta = MATCH.intent
            ),
        Fact(
            intent = MATCH.intent
            ))
    def intent_tipo_plato_dieta(self, comida):
        """
            Filtra los menus en el sistema en base a un intent y el perfil del usuario para un tipo de dieta.
            Parametros
            ----------
            comida : ComidaFact
                Cena que ha encajado en la regla
        """

        self.tipo_plato_dieta.append(comida)

    @Rule(
        AS.comida << ComidaFact(
            primero= MATCH.primero, 
            segundo= MATCH.segundo, 
            postre = MATCH.postre,
            ),
        UserFact(
            data__allergies = MATCH.allergies
            ))
    def intent_pedir_plato_alergia(self, comida, primero, segundo, postre, allergies):
        """
            Filtra los menus en base a las alergias del usuario.
            Parametros
            ----------
            comida : ComidaFact
                Menu que encaja con la regla
            primero : string
                Plato que ha encajado con la regla
            segundo : string
                Plato que ha encajado con la regla
            postre : string
                Plato que ha encajado con la regla
            allergies : list
                Lista de alergias del usuario
        """

        if allergies != [] and primero not in allergies and segundo not in allergies and postre not in allergies:
            self.pedir_plato_alergia.append(comida)

    @Rule(
        AS.comida << ComidaFact(
            primero= MATCH.intent, 
            ),
        Fact(
            intent = MATCH.intent
            ))
    def intent_recomendar_ingrediente_prim(self, comida):
        """
            Recomienda platos en base a un intent.
            Parametros
            ----------
            comida : ComidaFact
                Menu que encaja con la regla
        """

        self.recomendacion_ingrediente.append(comida)

    @Rule(
        AS.comida << ComidaFact(
            segundo= MATCH.intent, 
            ),
        Fact(
            intent = MATCH.intent
            ))
    def intent_recomendar_ingrediente_seg(self, comida):
        """
            Recomienda platos en base a un intent.
            Parametros
            ----------
            comida : ComidaFact
                Menu que encaja con la regla
        """

        self.recomendacion_ingrediente.append(comida)
        

    @Rule(
        AS.comida << ComidaFact(
            primero= MATCH.primero, 
            segundo= MATCH.segundo, 
            postre = MATCH.postre,
            dificultad = MATCH.intent
            ),
        Fact(
            intent = MATCH.intent
            ))
    def intent_plato_sencillo(self, comida):
        """
            Filtra platos en base a su dificultad.
            Parametros
            ----------
            comida : ComidaFact
                Menu que encaja con la regla
        """

        self.platos_sencillos.append(comida)
