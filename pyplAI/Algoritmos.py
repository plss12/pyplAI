"""Algoritmos de búsqueda para juegos de mesa: MCTS, Minimax, SO-ISMCTS y MO-ISMCTS.

Referencias:
    [1] Browne et al. A survey of Monte Carlo tree search methods. IEEE TCIAIG 4(1), 2012.
    [2] Knuth y Moore. An analysis of alpha-beta pruning. Artificial Intelligence 6(4), 1975.
    [4] Cowling, Powley y Whitehouse. Information set Monte Carlo tree search. IEEE TCIAIG 4(2), 2012.
"""

from __future__ import annotations

import math
import random
import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

#Valor de una victoria en Minimax. Las heurísticas deben devolver valores de menor magnitud
VICTORIA = 1e9


@dataclass
class EvaluacionMovimiento:
    """Evaluación de un movimiento de la raíz tras la búsqueda."""
    movimiento: Any
    #Número de visitas del nodo (0 en Minimax, que no muestrea)
    visitas: int
    #Recompensa media del jugador que mueve en MCTS e ISMCTS (entre 0 y 1) o valor minimax
    valor: float


@dataclass
class ResultadoAnalisis:
    """Resultado de analizar un estado: movimiento elegido y ranking de todos los movimientos."""
    movimiento: Any
    #Movimientos ordenados de mejor a peor según el criterio de elección del algoritmo
    movimientos: List[EvaluacionMovimiento] = field(default_factory=list)
    #Iteraciones de búsqueda (Monte Carlo) o estados evaluados (Minimax)
    iteraciones: int = 0
    nodos: int = 0
    tiempo: float = 0.0


def _generador(semilla: Optional[int]) -> Any:
    #Sin semilla se usa el módulo random, así random.seed() sigue controlando la biblioteca
    return random if semilla is None else random.Random(semilla)


def _comprueba_movimientos(movimientos: list, estado: Any) -> None:
    if len(movimientos) == 0:
        raise ValueError(
            "El estado no es final pero no tiene movimientos posibles. Todo estado no final "
            "debe tener al menos un movimiento (estado: " + repr(estado) + ")")


def _recompensa(gana_jugador: Callable, estado: Any, jugadores: List[int]) -> List[float]:
    #Vector de recompensas: 1 para cada ganador, 0 para el resto y 0.5 para todos si hay empate
    res = [1.0 if gana_jugador(estado, jugador) else 0.0 for jugador in jugadores]
    if 1.0 not in res:
        res = [0.5] * len(jugadores)
    return res


class _Presupuesto:
    """Controla el límite de la búsqueda: un tiempo en segundos o un número fijo de iteraciones."""

    def __init__(self, tiempoEjecucion: float, iteraciones: Optional[int]):
        if iteraciones is not None and iteraciones < 1:
            raise ValueError("iteraciones debe ser un entero mayor que 0")
        self.tiempoEjecucion = tiempoEjecucion
        self.iteraciones = iteraciones
        self.t0 = time.perf_counter()
        self.realizadas = 0

    def inicia(self) -> None:
        self.t0 = time.perf_counter()
        self.realizadas = 0

    def continua(self) -> bool:
        #Se llama tras cada iteración, así siempre se hace al menos una y la raíz tiene algún hijo
        self.realizadas += 1
        if self.iteraciones is not None:
            return self.realizadas < self.iteraciones
        return time.perf_counter() - self.t0 < self.tiempoEjecucion

    def transcurrido(self) -> float:
        return time.perf_counter() - self.t0


class MCTS:
    """Monte Carlo Tree Search con UCT (algoritmo 2 de Browne et al., 2012).

    Las recompensas son un vector con una entrada por jugador y cada nodo se elige con la
    recompensa del jugador que mueve en su padre, lo que permite más de dos jugadores.
    """
    k = 1/math.sqrt(2) #Coeficiente de exploración Cp

    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, numeroJugadores, tiempoEjecucion, estadisticas=False, *, iteraciones=None, semilla=None, seleccion_final="media"):
        if seleccion_final not in ("media", "visitas"):
            raise ValueError("seleccion_final debe ser 'media' o 'visitas'")
        self.aplicar_movimiento = aplicar_movimiento
        self.obtener_movimientos = obtener_movimientos
        self.es_estado_final = es_estado_final
        self.gana_jugador = gana_jugador
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.tiempoEjecucion = tiempoEjecucion
        self.estadisticas = estadisticas
        self.seleccion_final = seleccion_final
        self.presupuesto = _Presupuesto(tiempoEjecucion, iteraciones)
        self.rng = _generador(semilla)

    class nodo:
        def __init__(self,padre,mov=None):
            self.mov=mov #Movimiento que ha generado el nodo
            self.n = 0 #Número de veces que se ha visitado el nodo
            self.q = [] #Vector de recompensas acumuladas
            self.hijos = [] #Lista de nodos hijos
            self.padre = padre #Nodo padre

    @staticmethod
    def movs_restantes(v,movs):
        res=list(movs)
        for hijo in v.hijos:
            if(hijo.mov in res):
                res.remove(hijo.mov)
        return res

    @staticmethod
    def nodos_creados(v):
        suma = 1
        pendientes = list(v.hijos)
        while pendientes:
            hijo = pendientes.pop()
            suma += 1
            pendientes.extend(hijo.hijos)
        return suma

    def busca(self, s0):
        """Ejecuta la búsqueda desde s0 y devuelve el nodo raíz."""
        v0 = self.nodo(None)
        v0.q = [0]*len(self.jugadores)
        movimientos = self.obtener_movimientos(s0)
        self.presupuesto.inicia()
        while True:
            v1, s1, movs = self.tree_policy(v0, s0, movimientos)
            delta = self.default_policy(s1, movs, self.jugadores)
            self.backup(v1, delta, self.jugadores)
            if not self.presupuesto.continua():
                break
        return v0

    def _ordena_hijos(self, v0, jugador):
        if self.seleccion_final == "visitas":
            #Robust child: el hijo más visitado
            return sorted(v0.hijos, key=lambda h: h.n, reverse=True)
        #BESTCHILD(v0, 0) de Browne et al.: el hijo con mayor recompensa media
        return sorted(v0.hijos, key=lambda h: h.q[jugador]/h.n, reverse=True)

    def analiza(self, s0):
        """Busca desde s0 y devuelve un ResultadoAnalisis con el ranking de movimientos. No imprime nada."""
        if self.es_estado_final(s0) or len(self.obtener_movimientos(s0)) == 0:
            return ResultadoAnalisis(None)
        v0 = self.busca(s0)
        jugador = s0.jugadorActual-1
        hijos = self._ordena_hijos(v0, jugador)
        return ResultadoAnalisis(
            movimiento=hijos[0].mov,
            movimientos=[EvaluacionMovimiento(h.mov, h.n, h.q[jugador]/h.n) for h in hijos],
            iteraciones=v0.n,
            nodos=self.nodos_creados(v0),
            tiempo=self.presupuesto.transcurrido())

    def ejecuta(self, s0):
        movimientos=self.obtener_movimientos(s0)
        if(len(movimientos)==1):
            return movimientos[0]
        elif(len(movimientos)==0 or self.es_estado_final(s0)):
            return None
        resultado = self.analiza(s0)
        if(self.estadisticas):
            print("\nTiempo de ejecución: ", resultado.tiempo)
            print("Número de nodos creados: ", resultado.nodos)
            print("Número de nodos visitados: ", resultado.iteraciones)
        return resultado.movimiento

    def tree_policy(self, v,s,movimientos):
        while(self.es_estado_final(s)==False):
            _comprueba_movimientos(movimientos, s)
            movs_sin_visitar = self.movs_restantes(v,movimientos)
            if(0<len(movs_sin_visitar)):
                return self.expand(v,s,movs_sin_visitar)
            else:
                jugador=s.jugadorActual-1
                mejorHijo = self.best_child(v, MCTS.k ,jugador)
                copiaEstado=deepcopy(s)
                s = self.aplicar_movimiento(copiaEstado,mejorHijo.mov)
                movimientos = self.obtener_movimientos(s)
                v = mejorHijo
        return [v,s,movimientos]

    def expand(self, v,s,movRestantes):
        copiaEstado=deepcopy(s)
        mov = self.rng.choice(movRestantes)
        s = self.aplicar_movimiento(copiaEstado, mov)
        movs = self.obtener_movimientos(s)
        hijo = self.nodo(v,mov)
        hijo.q = [0]*len(v.q)
        v.hijos.append(hijo)
        return [hijo,s,movs]

    @staticmethod
    def best_child(v,c,jugador):
        #UCT: Q(v')/N(v') + c * sqrt(2 ln N(v) / N(v'))
        mejorHijo = None
        maximo = -math.inf
        for hijo in v.hijos:
            heuristica = hijo.q[jugador]/hijo.n + (c * math.sqrt((2*math.log(v.n))/hijo.n))
            if(heuristica>maximo):
                maximo = heuristica
                mejorHijo = hijo
        return mejorHijo

    def default_policy(self, s,movs,jugadores):
        while(self.es_estado_final(s)==False):
            _comprueba_movimientos(movs, s)
            a = self.rng.choice(movs)
            s = self.aplicar_movimiento(s,a)
            movs = self.obtener_movimientos(s)
        return _recompensa(self.gana_jugador, s, jugadores)

    @staticmethod
    def backup(v,delta,jugadores):
        while(v is not None):
            v.n = v.n+1
            for i in range(len(jugadores)):
                v.q[i]+=delta[i]
            v = v.padre


class Minimax:
    """Minimax con poda alfa-beta (Knuth y Moore, 1975).

    Con más de dos jugadores es paranoico: el resto de jugadores minimiza el valor del jugador
    que busca. profundidadBusqueda es el número de niveles (jugadas) que se exploran.
    """

    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, heuristica, numeroJugadores, profundidadBusqueda, estadisticas=False):
        if profundidadBusqueda < 1:
            raise ValueError("profundidadBusqueda debe ser un entero mayor que 0")
        self.aplicar_movimiento = aplicar_movimiento
        self.obtener_movimientos = obtener_movimientos
        self.es_estado_final = es_estado_final
        self.gana_jugador = gana_jugador
        self.heuristica = heuristica
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.profundidadBusqueda = profundidadBusqueda
        self.estadisticas = estadisticas

    def evaluate(self,estado,jugadorMax,nivel=0):
        #Las victorias valen más cuanto antes llegan y las derrotas, cuanto más tarde
        if(self.es_estado_final(estado)):
            for jugador in self.jugadores:
                if(self.gana_jugador(estado,jugador)):
                    if(jugador==jugadorMax):
                        return VICTORIA - nivel
                    else:
                        return -VICTORIA + nivel
            return 0
        return self.heuristica(estado,jugadorMax)

    def alfabeta(self, estado, nivel, jugadorMax, alpha, beta, contador):
        """Valor minimax de estado, situado a nivel jugadas de la raíz."""
        contador[0] += 1
        if(self.es_estado_final(estado) or nivel>=self.profundidadBusqueda):
            return self.evaluate(estado,jugadorMax,nivel)
        movs = self.obtener_movimientos(estado)
        _comprueba_movimientos(movs, estado)
        if(estado.jugadorActual==jugadorMax):
            best = -math.inf
            for mov in movs:
                hijo = self.aplicar_movimiento(deepcopy(estado),mov)
                best = max(best, self.alfabeta(hijo, nivel+1, jugadorMax, alpha, beta, contador))
                alpha = max(alpha, best)
                if(beta<=alpha):
                    break
        else:
            best = math.inf
            for mov in movs:
                hijo = self.aplicar_movimiento(deepcopy(estado),mov)
                best = min(best, self.alfabeta(hijo, nivel+1, jugadorMax, alpha, beta, contador))
                beta = min(beta, best)
                if(beta<=alpha):
                    break
        return best

    def _busca(self, estado, completo):
        t0 = time.perf_counter()
        jugadorMax = estado.jugadorActual
        contador = [1]
        evaluaciones = []
        alpha = -math.inf
        for mov in self.obtener_movimientos(estado):
            hijo = self.aplicar_movimiento(deepcopy(estado),mov)
            #Con completo=True cada movimiento se evalúa con ventana completa y su valor es exacto;
            #si no, los movimientos peores que el mejor encontrado solo se acotan (poda en la raíz)
            ventana = -math.inf if completo else alpha
            valor = self.alfabeta(hijo, 1, jugadorMax, ventana, math.inf, contador)
            evaluaciones.append(EvaluacionMovimiento(mov, 0, valor))
            alpha = max(alpha, valor)
        mejor = evaluaciones[0]
        for evaluacion in evaluaciones:
            if(evaluacion.valor>mejor.valor):
                mejor = evaluacion
        ordenadas = sorted(evaluaciones, key=lambda e: e.valor, reverse=True)
        return ResultadoAnalisis(mejor.movimiento, ordenadas, contador[0], contador[0], time.perf_counter()-t0)

    def analiza(self, estado):
        """Valor exacto de cada movimiento de la raíz y movimiento elegido. No imprime nada."""
        if self.es_estado_final(estado) or len(self.obtener_movimientos(estado)) == 0:
            return ResultadoAnalisis(None)
        return self._busca(estado, True)

    def ejecuta(self, estado):
        movs = self.obtener_movimientos(estado)
        if(len(movs)==1):
            return movs[0]
        elif(len(movs)==0 or self.es_estado_final(estado)):
            return None
        resultado = self._busca(estado, False)
        if(self.estadisticas):
            print("\nTiempo de ejecución: ", resultado.tiempo)
            print("Número de estados evaluados: ", resultado.iteraciones)
        return resultado.movimiento


class SOISMCTS:
    """Single Observer Information Set MCTS (algoritmo 2 de Cowling, Powley y Whitehouse, 2012)."""
    k = 1/math.sqrt(2) #Coeficiente de exploración

    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, determinization, numeroJugadores, tiempoEjecucion, estadisticas=False, *, iteraciones=None, semilla=None):
        self.aplicar_movimiento = aplicar_movimiento
        self.obtener_movimientos = obtener_movimientos
        self.es_estado_final = es_estado_final
        self.gana_jugador = gana_jugador
        self.determinization = determinization
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.tiempoEjecucion = tiempoEjecucion
        self.estadisticas = estadisticas
        self.presupuesto = _Presupuesto(tiempoEjecucion, iteraciones)
        self.rng = _generador(semilla)

    class nodo:
        def __init__(self,padre,accion=None):
            self.a = accion #Acción que crea el nodo
            self.c = [] #Hijos del nodo
            self.n = 0 #Número de visitas
            self.nP = 1 #Número de veces que estuvo disponible (n' en el artículo)
            self.r = [] #Vector de recompensa total
            self.padre = padre #Padre del nodo

        def actions_of_determinization_without_children(self,movs): #u(v,d)
            acciones = list(movs)
            for child in self.c:
                if(child.a in acciones):
                    acciones.remove(child.a)
            return acciones

    @staticmethod
    def nodos_creados(v):
        suma = 1
        pendientes = list(v.c)
        while pendientes:
            hijo = pendientes.pop()
            suma += 1
            pendientes.extend(hijo.c)
        return suma

    def busca(self, s0):
        """Ejecuta la búsqueda desde s0 y devuelve el nodo raíz."""
        v0=self.nodo(None)
        v0.r=[0]*len(self.jugadores)
        self.presupuesto.inicia()
        while True:
            d0=self.determinization(s0) #Determinización aleatoria del conjunto de información de s0
            movs = self.obtener_movimientos(d0)
            (v,d,movs,actionsWithoutChildren)=self.select(v0,d0,movs)
            if(len(actionsWithoutChildren)!=0):
                (v,d)=self.expand(v,d,actionsWithoutChildren,movs)
                movs = self.obtener_movimientos(d)
            r=self.simulate(d,movs)
            self.backpropagate(r,v,self.jugadores)
            if not self.presupuesto.continua():
                break
        return v0

    def analiza(self, s0):
        """Busca desde s0 y devuelve un ResultadoAnalisis con el ranking de movimientos. No imprime nada."""
        legales = self.obtener_movimientos(s0)
        if self.es_estado_final(s0) or len(legales) == 0:
            return ResultadoAnalisis(None)
        v0 = self.busca(s0)
        jugador = s0.jugadorActual-1
        #Solo se eligen acciones legales en el estado real
        hijos = [c for c in v0.c if c.a in legales] or v0.c
        hijos = sorted(hijos, key=lambda c: c.n, reverse=True)
        return ResultadoAnalisis(
            movimiento=hijos[0].a,
            movimientos=[EvaluacionMovimiento(c.a, c.n, c.r[jugador]/c.n) for c in hijos],
            iteraciones=v0.n,
            nodos=self.nodos_creados(v0),
            tiempo=self.presupuesto.transcurrido())

    def ejecuta(self,s0):
        movs=self.obtener_movimientos(s0)
        if(len(movs)==1):
            return movs[0]
        elif(len(movs)==0 or self.es_estado_final(s0)):
            return None
        resultado = self.analiza(s0)
        if(self.estadisticas):
            print("\nTiempo de ejecución: ", resultado.tiempo)
            print("Número de nodos creados: ", resultado.nodos)
            print("Número de nodos visitados: ", resultado.iteraciones)
        return resultado.movimiento   #Acción del hijo de la raíz más visitado

    @staticmethod
    def best_child(v,movs,jugador,k):
        hijosCompatibles = [c for c in v.c if c.a in movs]
        mejorHijo = None
        maximo = -math.inf
        for hijo in hijosCompatibles:
            heuristica = (hijo.r[jugador]/hijo.n) + (k * math.sqrt(math.log(hijo.nP)/hijo.n))
            if(heuristica>maximo):
                maximo = heuristica
                mejorHijo = hijo
        #Todos los hijos compatibles con la determinización estaban disponibles: se incrementa su n'
        for hijo in hijosCompatibles:
            hijo.nP += 1
        return mejorHijo

    def select(self,v,d,movs):
        accionesSinHijos = v.actions_of_determinization_without_children(movs)
        while(self.es_estado_final(d)==False and len(accionesSinHijos)==0):
            _comprueba_movimientos(movs, d)
            jugador = d.jugadorActual-1
            c=self.best_child(v,movs,jugador,SOISMCTS.k)
            v=c
            d=deepcopy(d)
            d=self.aplicar_movimiento(d,c.a)
            movs = self.obtener_movimientos(d)
            accionesSinHijos = v.actions_of_determinization_without_children(movs)
        return v,d,movs,accionesSinHijos

    def expand(self,v,d,actionsWithoutChildren,movs=None):
        if movs is not None:
            #Los hijos que ya existen y son compatibles también estaban disponibles
            for hijo in v.c:
                if hijo.a in movs:
                    hijo.nP += 1
        d=deepcopy(d)
        a=self.rng.choice(actionsWithoutChildren)
        w=self.nodo(v,a)
        v.c.append(w)
        w.r = [0]*len(w.padre.r)
        d=self.aplicar_movimiento(d,a)
        return w,d

    def simulate(self,d,movs):
        while(self.es_estado_final(d)==False):
            _comprueba_movimientos(movs, d)
            a=self.rng.choice(movs)
            d=self.aplicar_movimiento(d,a)
            movs=self.obtener_movimientos(d)
        return _recompensa(self.gana_jugador, d, self.jugadores)

    @staticmethod
    def backpropagate(r,v1,jugadores):
        while(v1 is not None):
            v1.n+=1
            for i in range(len(jugadores)):
                v1.r[i]+=r[i]
            v1=v1.padre


class MOISMCTS:
    """Multiple Observer Information Set MCTS (algoritmo 3 de Cowling, Powley y Whitehouse, 2012)."""
    k=1/math.sqrt(2)

    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, determinization, accion_visible, numeroJugadores, tiempoEjecucion, estadisticas=False, *, iteraciones=None, semilla=None):
        self.aplicar_movimiento = aplicar_movimiento
        self.obtener_movimientos = obtener_movimientos
        self.es_estado_final = es_estado_final
        self.gana_jugador = gana_jugador
        self.determinization = determinization
        self.accion_visible = accion_visible
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.tiempoEjecucion = tiempoEjecucion
        self.estadisticas = estadisticas
        self.presupuesto = _Presupuesto(tiempoEjecucion, iteraciones)
        self.rng = _generador(semilla)

    class nodo:
        def __init__(self,padre,jugador,accion=None):
            self.jugador = jugador #Jugador dueño del árbol al que pertenece el nodo
            self.a = accion #Acción que crea el nodo, o "?" si su dueño no la puede ver
            self.c = [] #Hijos del nodo
            self.n = 0 #Número de visitas
            self.nP = 1 #Número de veces que estuvo disponible (n' en el artículo)
            self.r = [] #Vector de recompensa total
            self.padre = padre #Padre del nodo

        def actions_of_determinization_without_children(self,movs): #u(v,d)
            acciones = list(movs)
            for child in self.c:
                if(child.a in acciones):
                    acciones.remove(child.a)
            return acciones

    @staticmethod
    def nodos_creados(v):
        suma = 1
        pendientes = list(v.c)
        while pendientes:
            hijo = pendientes.pop()
            suma += 1
            pendientes.extend(hijo.c)
        return suma

    def find_or_create_child(self,n,a,jugadorAccion):
        #Cada jugador ve sus propias acciones; las del resto solo si son visibles, si no se agrupan en "?"
        if(jugadorAccion!=n.jugador and not self.accion_visible(a)):
            a = "?"
        for child in n.c:
            if(child.a==a):
                return child
        v1 = MOISMCTS.nodo(n,n.jugador,a)
        n.c.append(v1)
        v1.r = [0]*len(n.r)
        return v1

    def busca(self, s0):
        """Ejecuta la búsqueda desde s0 y devuelve las raíces de los árboles de cada jugador."""
        jugadores = self.jugadores
        nodos0 = []
        for jugador in jugadores:
            v0=self.nodo(None,jugador)
            v0.r=[0]*len(jugadores)
            nodos0.append(v0)
        self.presupuesto.inicia()
        while True:
            d0=self.determinization(s0)
            movs = self.obtener_movimientos(d0)
            (nodos,d,movs,actionsWithoutChildren)=self.select(nodos0,d0,movs)
            if(len(actionsWithoutChildren)!=0):
                (nodos,d)=self.expand(nodos,d,actionsWithoutChildren,movs)
                movs = self.obtener_movimientos(d)
            r=self.simulate(d,movs)
            for v in nodos:
                self.backpropagate(r,v,jugadores)
            if not self.presupuesto.continua():
                break
        return nodos0

    def analiza(self, s0):
        """Busca desde s0 y devuelve un ResultadoAnalisis con el ranking de movimientos. No imprime nada."""
        legales = self.obtener_movimientos(s0)
        if self.es_estado_final(s0) or len(legales) == 0:
            return ResultadoAnalisis(None)
        nodos0 = self.busca(s0)
        jugador = s0.jugadorActual-1
        raiz = nodos0[jugador]
        hijos = [c for c in raiz.c if c.a in legales] or raiz.c
        hijos = sorted(hijos, key=lambda c: c.n, reverse=True)
        return ResultadoAnalisis(
            movimiento=hijos[0].a,
            movimientos=[EvaluacionMovimiento(c.a, c.n, c.r[jugador]/c.n) for c in hijos],
            iteraciones=raiz.n,
            nodos=sum(self.nodos_creados(v) for v in nodos0),
            tiempo=self.presupuesto.transcurrido())

    def ejecuta(self,s0):
        movs=self.obtener_movimientos(s0)
        if(len(movs)==1):
            return movs[0]
        elif(len(movs)==0 or self.es_estado_final(s0)):
            return None
        resultado = self.analiza(s0)
        if(self.estadisticas):
            print("\nTiempo de ejecución: ", resultado.tiempo)
            print("Número de nodos creados: ", resultado.nodos)
            print("Número de nodos visitados: ", resultado.iteraciones)
        return resultado.movimiento

    @staticmethod
    def best_child(v,movs,jugador,k):
        hijosCompatibles = [c for c in v.c if c.a in movs]
        mejorHijo = None
        maximo = -math.inf
        for hijo in hijosCompatibles:
            heuristica = ((hijo.r[jugador])/hijo.n) + (k * math.sqrt(math.log(hijo.nP)/hijo.n))
            if(heuristica>maximo):
                maximo = heuristica
                mejorHijo = hijo
        for hijo in hijosCompatibles:
            hijo.nP += 1
        return mejorHijo

    def select(self,nodos,d,movs):
        n=nodos[d.jugadorActual-1] #Nodo del árbol del jugador que tiene el turno
        accionesSinHijos = n.actions_of_determinization_without_children(movs)
        while(self.es_estado_final(d)==False and len(accionesSinHijos)==0):
            _comprueba_movimientos(movs, d)
            jugador = d.jugadorActual
            c=self.best_child(n,movs,jugador-1,MOISMCTS.k)
            d=deepcopy(d)
            d=self.aplicar_movimiento(d,c.a)
            movs = self.obtener_movimientos(d)
            #Se desciende en el árbol de cada jugador con la acción vista desde su punto de vista
            nodos = [self.find_or_create_child(nodo,c.a,jugador) for nodo in nodos]
            n = nodos[d.jugadorActual-1]
            accionesSinHijos = n.actions_of_determinization_without_children(movs)
        return nodos,d,movs,accionesSinHijos

    def expand(self,nodos,d,actionsWithoutChildren,movs=None):
        jugador = d.jugadorActual
        if movs is not None:
            for hijo in nodos[jugador-1].c:
                if hijo.a in movs:
                    hijo.nP += 1
        d=deepcopy(d)
        a=self.rng.choice(actionsWithoutChildren)
        newNodos = [self.find_or_create_child(nodo,a,jugador) for nodo in nodos]
        d=self.aplicar_movimiento(d,a)
        return newNodos,d

    def simulate(self,d,movs):
        while(self.es_estado_final(d)==False):
            _comprueba_movimientos(movs, d)
            a=self.rng.choice(movs)
            d=self.aplicar_movimiento(d,a)
            movs=self.obtener_movimientos(d)
        return _recompensa(self.gana_jugador, d, self.jugadores)

    @staticmethod
    def backpropagate(r,v1,jugadores):
        while(v1 is not None):
            v1.n+=1
            for i in range(len(jugadores)):
                v1.r[i]+=r[i]
            v1=v1.padre
