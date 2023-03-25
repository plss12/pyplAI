import random
from copy import deepcopy
import time
import math

class MCTS:
    k = 1/math.sqrt(2) #Coeficiente de exploracion

    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, numeroJugadores, tiempoEjecucion, estadisticas=True):
        self.aplicar_movimiento = staticmethod(aplicar_movimiento)
        self.obtener_movimientos = staticmethod(obtener_movimientos)
        self.es_estado_final = staticmethod(es_estado_final)
        self.gana_jugador = staticmethod(gana_jugador)
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.tiempoEjecucion = tiempoEjecucion
        self.estadisticas = estadisticas

    class nodo:
        def __init__(self,padre,mov=None):
            self.mov=mov #Movimiento que ha generado el nodo
            self.n = 0 #Numero de veces que se ha visitado el nodo
            self.q = [] #Vector de recompensas acumuladas
            self.hijos = [] #Lista de nodos hijos
            self.padre = padre #Nodo padre

    @staticmethod
    def movs_restantes(v,movs):
        res=movs.copy()
        for hijo in v.hijos:
            if(hijo.mov in movs):
                res.remove(hijo.mov)
        return res
        
    @staticmethod
    def nodos_creados(v):
        if(len(v.hijos)==0):
            return 1
        else:
            suma = 1
            for hijo in v.hijos:
                suma = suma + MCTS.nodos_creados(hijo)
            return suma

    def ejecuta(self, s0):
        movimientos=self.obtener_movimientos(s0)
        if(len(movimientos)==1):
            return movimientos[0]
        elif(len(movimientos)==0):
            return None
        else:
            v0 = self.nodo(None)
            vector = [0]*len(self.jugadores)
            v0.q = vector
            t0 = time.time()
            while( time.time() - t0 < self.tiempoEjecucion):
                tree = self.tree_policy(v0,s0,movimientos)
                v1=tree[0]
                s1=tree[1]
                movs=tree[2]
                delta = self.default_policy(s1,movs,self.jugadores)
                self.backup(v1,delta,self.jugadores)
            jugador = s0.jugadorActual-1
            mejorNodo = self.best_child(v0,0,jugador)
            if(self.estadisticas):
                numeroNodosCreados = self.nodos_creados(v0)
                print("\nTiempo de ejecución: ", self.tiempoEjecucion)
                print("Número de nodos creados: ",numeroNodosCreados)
                print("Número de nodos visitados: ",v0.n)
            mov=mejorNodo.mov
            return mov
    
    def tree_policy(self, v,s,movimientos):
        while(self.es_estado_final(s)==False):
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
        mov = random.choice(movRestantes)
        s = self.aplicar_movimiento(copiaEstado, mov)
        movs = self.obtener_movimientos(s)
        hijo = self.nodo(v,mov)
        vector = [0]*len(v.q)
        hijo.q = vector
        v.hijos.append(hijo)
        return [hijo,s,movs]

    @staticmethod
    def best_child(v,c,jugador):
        indiceMejorHijo=0
        contador=0
        max=-math.inf
        for hijo in v.hijos:
            heuristica = hijo.q[jugador]/hijo.n + (c * math.sqrt((2*math.log(v.n))/hijo.n))
            if(heuristica>max):
                max = heuristica
                indiceMejorHijo=contador
            contador+=1
        return v.hijos[indiceMejorHijo]

    def default_policy(self, s,movs,jugadores):
        #El jugador que queremos comprobar es el anterior al del estado actual, ya que se ha cambiado en tree_policy
        while(self.es_estado_final(s)==False):
            a = random.choice(movs)
            s = self.aplicar_movimiento(s,a)
            movs = self.obtener_movimientos(s)

        #Crea una lista de 0s del tamaño de la lista de jugadores
        res = [0] * len(jugadores)
        #Cambia los valores de la lista de 0s a la recompensa que obtiene cada jugador
        for jugador in jugadores:
            if(self.gana_jugador(s,jugador)):
                res[jugadores.index(jugador)]=1

        #Si no hay ningún ganador, todos los jugadores empatan
        if (1 not in res):
            res = [0.5] * len(jugadores)
        return res

    @staticmethod
    def backup(v,delta,jugadores):
        while(v != None):
            v.n = v.n+1
            #Incrementa la recompensa del nodo para cada jugador
            for jugador in jugadores:
                v.q[jugadores.index(jugador)]+=delta[jugadores.index(jugador)]
            v = v.padre

class Minimax:
    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, heuristica, numeroJugadores, profundidadBusqueda, estadisticas=True):
        self.aplicar_movimiento = staticmethod(aplicar_movimiento)
        self.obtener_movimientos = staticmethod(obtener_movimientos)
        self.es_estado_final = staticmethod(es_estado_final)
        self.gana_jugador = staticmethod(gana_jugador)
        self.heuristica = staticmethod(heuristica)
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.profundidadBusqueda = profundidadBusqueda
        self.estadisticas = estadisticas

    def evaluate(self,estado,jugadorMax):
        if(self.es_estado_final(estado)):
            for jugador in self.jugadores:
                if(self.gana_jugador(estado,jugador)):
                    if(jugador==jugadorMax):
                        return math.inf
                    else:
                        return -math.inf
            return 0
        return self.heuristica(estado,jugadorMax)

    def minimax(self, estado, depth, movMax, jugadorMax, profundidadBusqueda, alpha, beta, estadosEvaluados):
        movs = self.obtener_movimientos(estado)
        score = self.evaluate(estado,jugadorMax)
        jugador=estado.jugadorActual
        newEstado=deepcopy(estado)

        if(self.es_estado_final(estado)):
            return ((score - depth), movMax, estadosEvaluados)

        if(depth<=profundidadBusqueda):
            if(jugadorMax==jugador):
                best = -math.inf
                for i in range(len(movs)):
                    s = self.aplicar_movimiento(newEstado,movs[i])
                    value=self.minimax(s, depth+1, movMax, jugadorMax, profundidadBusqueda, alpha, beta, estadosEvaluados+1)
                    if(value[0]>best):
                        movMax=movs[i]
                    best = max(best, value[0])
                    alpha = max(alpha, best)
                    newEstado=deepcopy(estado)
                    estadosEvaluados=value[2]
                    if (beta <= alpha):
                        break
                return (best, movMax, estadosEvaluados)
            
            else:
                best = math.inf
                for i in range(len(movs)):
                    s = self.aplicar_movimiento(newEstado,movs[i])
                    value=self.minimax(s,  depth+1, movMax, jugadorMax, profundidadBusqueda, alpha, beta, estadosEvaluados+1)
                    best = min(best,value[0])
                    beta = min(beta, best)
                    newEstado=deepcopy(estado)
                    estadosEvaluados=value[2]
                    if (beta <= alpha):
                        break
                return (best, movMax, estadosEvaluados)
        else:
            return ((score - depth), movMax, estadosEvaluados)

    def ejecuta(self, estado):
        t0 = time.time()
        alpha=-math.inf #Maximizar
        beta=math.inf #Minimizar
        jugadorMax = estado.jugadorActual
        movs = self.obtener_movimientos(estado)
        newEstado = deepcopy(estado)
        if(len(movs)==1):
            return movs[0]
        elif(len(movs)==0):
            return None
        else:
            valores = self.minimax(newEstado, 0, movs[0], jugadorMax, self.profundidadBusqueda, alpha, beta, 1)
            mov= valores[1]
            estadosEvaluados = valores[2]
        if(self.estadisticas):
            print("\nTiempo de ejecución: ", time.time()-t0)
            print("Número de estados evaluados: ", estadosEvaluados)
        return mov

class SOISMCTS:
    k = 1/math.sqrt(2) #Coeficiente de exploracion

    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, determinization, numeroJugadores, tiempoEjecucion, estadisticas=True):
        self.aplicar_movimiento = staticmethod(aplicar_movimiento)
        self.obtener_movimientos = staticmethod(obtener_movimientos)
        self.es_estado_final = staticmethod(es_estado_final)
        self.gana_jugador = staticmethod(gana_jugador)
        self.determinization = staticmethod(determinization)
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.tiempoEjecucion = tiempoEjecucion
        self.estadisticas = estadisticas

    class nodo:
        def __init__(self,padre,accion=None):
            self.a = accion #Acción la cual hace que se cree el nodo
            self.c = [] #Hijos del nodo
            self.n = 0 #Número de visitas
            self.nP = 1 #Número de veces las cuales estuvo disponibles
            self.r = [] #Vector de recompensa total
            self.padre = padre #Padre del nodo

        def actions_of_determinization_without_children(self,movs): #u(v,d)
            acciones = movs[:] #Copia la lista de movimientos disponibles con la determinización
            for child in self.c:       #Recorre los hijos del nodo
                if(child.a in acciones):#Si ya tiene un hijo con la acción la elimina de la lista de acciones
                    acciones.remove(child.a) 
            return acciones                #Devuelve la lista de acciones de la determinización sin hijos
    
    @staticmethod
    def nodos_creados(v):
        if(len(v.c)==0):
            return 1
        else:
            suma = 1
            for hijo in v.c:
                suma = suma + SOISMCTS.nodos_creados(hijo)
            return suma
            
    def ejecuta(self,s0):
        movs=self.obtener_movimientos(s0)
        if(len(movs)==1):
            return movs[0]
        elif(len(movs)==0):
            return None
        else:
            v0=self.nodo(None)
            jugadores = self.jugadores
            v0.r=[0]*len(jugadores)
            t0 = time.time()
            while( time.time() - t0 < self.tiempoEjecucion):
                d0=self.determinization(s0) #Elige una determinización aleatoria de s0
                movs = self.obtener_movimientos(d0) #Obtiene los movimientos disponibles con la determinización
                (v,d,movs,actionsWithoutChildren)=self.select(v0,d0,movs)    #Selecciona un nodo y determinización
                if(len(actionsWithoutChildren)!=0): #Si aún hay acciones en la determinización para los cuales el nodo aún no tiene hijos
                    (v,d)=self.expand(v,d,actionsWithoutChildren)    #Expande el nodo y determinización
                    movs = self.obtener_movimientos(d) #Obtiene los movimientos disponibles con la nueva determinización
                r=self.simulate(d,movs)           #Simula el juego hasta el final
                self.backpropagate(r,v,jugadores)      #Actualiza los valores de los nodos
            mejor_accion = max(v0.c, key=lambda c: c.n).a  #Elige lla acción del nodo que más veces ha sido visitado
            if(self.estadisticas):
                numeroNodosCreados = self.nodos_creados(v0)
                print("\nTiempo de ejecución: ", self.tiempoEjecucion)
                print("Número de nodos creados: ",numeroNodosCreados)
                print("Número de nodos visitados: ",v0.n)
            return mejor_accion   #Devuelve la acción que maximiza la recompensa

    #Función para coger el mejor nodo
    @staticmethod
    def best_child(v,movs,jugador,k):
        hijosCompatibles = [c for c in v.c if c.a in movs]
        heuristicas = []
        for children in hijosCompatibles:
            heuristica = ((children.r[jugador])/children.n) + (k * math.sqrt(math.log(children.nP)/children.n))
            heuristicas.append(heuristica)
            #Actualizamos el número de visitas disponibles
            children.nP += 1

        mejorHijo=hijosCompatibles[heuristicas.index(max(heuristicas))]
        return mejorHijo
            
    def select(self,v,d,movs):
        accionesSinHijos = v.actions_of_determinization_without_children(movs) #Obtiene las acciones de la determinización sin hijos
        while(self.es_estado_final(d)==False and len(accionesSinHijos)==0): #Mientras no sea un estado final y siga habiendo acciones de la determinazión sin hijos en el nodo
            jugador = d.jugadorActual-1                 #El jugador el cuál le toca jugar en la determinización
            c=self.best_child(v,movs,jugador,SOISMCTS.k) #Coge el mejor nodo de los nodos compatibles con la determinización
            v=c                                         #El nodo actual es el mejor nodo
            d=deepcopy(d)                               #Copia la determinización
            d=self.aplicar_movimiento(d,c.a)            #La determinización es la determinización del mejor nodo
            movs = self.obtener_movimientos(d)          #Obtiene los movimientos disponibles con la determinización
            accionesSinHijos = v.actions_of_determinization_without_children(movs) #Obtiene las acciones de la determinización sin hijos
        return v,d,movs,accionesSinHijos                                 #Devuelve el nodo y la determinización

    def expand(self,v,d,actionsWithoutChildren):
        d=deepcopy(d)               #Copia la determinización                                    
        a=random.choice(actionsWithoutChildren)  #Elige una acción aleatoria de las acciones de la determinización sin hijos
        w=self.nodo(v,a)             #Crea un nodo con la acción y el nodo actual como padre que es compatible con la determinización
        v.c.append(w)       #Añade el nodo a la lista de hijos del nodo actual
        w.r = [0]*len(w.padre.r) #Crea una lista de 0s del tamaño de la lista de recompensas del nodo padre
        v=w                     #El nodo actual es el nodo creado
        d=self.aplicar_movimiento(d,a)      #La determinización es la determinización del nodo creado
        return v,d              #Devuelve el nodo y la determinización

    def simulate(self,d,movs):
        jugadores = self.jugadores #Obtiene los jugadores del juego
        while(self.es_estado_final(d)==False): #Mientras no sea un estado final
            a=random.choice(movs) #Elige una acción aleatoria de las acciones disponibles
            d=self.aplicar_movimiento(d,a)       #Aplica la acción a la determinización
            movs=self.obtener_movimientos(d) #Obtiene las acciones disponibles con la determinización

        #Crea una lista de 0s del tamaño de la lista de jugadores
        res = [0] * len(jugadores)
        #Cambia los valores de la lista de 0s a la recompensa que obtiene cada jugador
        for jugador in jugadores:                           
            if(self.gana_jugador(d,jugador)):
                indice=jugadores.index(jugador)
                res[indice]=1

        #Si no hay ningún ganador, todos los jugadores empatan
        if (1 not in res):
            res = [0.5] * len(jugadores)
        return res

    @staticmethod
    def backpropagate(r,v1,jugadores):
        while(v1!=None):
            v1.n+=1      #Incrementa el número de veces que se ha visitado el nodo
            #Incrementa la recompensa del nodo para cada jugador
            for jugador in jugadores:
                indiceJugador=jugadores.index(jugador)
                v1.r[indiceJugador]+=r[indiceJugador]
            v1=v1.padre #El nodo actual es el nodo padre del nodo actual

class MOISMCTS:
    k=1/math.sqrt(2)

    def __init__(self, aplicar_movimiento, obtener_movimientos, es_estado_final, gana_jugador, determinization, accion_visible, numeroJugadores, tiempoEjecucion, estadisticas=True):
        self.aplicar_movimiento = staticmethod(aplicar_movimiento)
        self.obtener_movimientos = staticmethod(obtener_movimientos)
        self.es_estado_final = staticmethod(es_estado_final)
        self.gana_jugador = staticmethod(gana_jugador)
        self.determinization = staticmethod(determinization)
        self.accion_visible = staticmethod(accion_visible)
        self.jugadores = [i+1 for i in range(numeroJugadores)]
        self.tiempoEjecucion = tiempoEjecucion
        self.estadisticas = estadisticas
    
    class nodo:
        def __init__(self,padre,jugador,accion=None):
            self.jugador = jugador #Jugador al que pertenece el nodo
            self.a = accion #Acción la cual hace que se cree el nodo
            self.c = [] #Hijos del nodo
            self.n = 0 #Número de visitas
            self.nP = 1 #Número de visitas disponibles
            self.r = [] #Vector de recompensa total
            self.padre = padre #Padre del nodo

        def actions_of_determinization_without_children(self,movs): #u(v,d)
            acciones = movs[:] #Copia la lista de movimientos disponibles con la determinización
            for child in self.c:       #Recorre los hijos del nodo
                if(child.a in acciones):#Si ya tiene un hijo con la acción la elimina de la lista de acciones
                    acciones.remove(child.a) 
            return acciones                #Devuelve la lista de acciones de la determinización sin hijos
    
    @staticmethod
    def nodos_creados(v):
        if(len(v.c)==0):
            return 1
        else:
            suma = 1
            for hijo in v.c:
                suma = suma + MOISMCTS.nodos_creados(hijo)
            return suma
        
    def find_or_create_child(self,n,a,jugadorAccion):
        #Si el jugador no es el que tiene el turno
        if(jugadorAccion!=n.jugador):
            #Mira si la acción es visible para los jugadores que no tienen el turno
            if(self.accion_visible(a)):
                #Si es visible busca si ya tiene un hijo con la acción
                for child in n.c:
                    if(child.a==a):
                        return child
                #Si no tiene un hijo con la acción lo crea ya que este siempre puede ver por completo esta acción
                v1 = MOISMCTS.nodo(n,n.jugador,a)
                n.c.append(v1)
                v1.r = [0]*len(v1.padre.r) #Crea una lista de 0s del tamaño de la lista de recompensas del nodo padre
                return v1
            #Si no es visible recupera o crea un nodo con la acción "?"
            else:
                for child in n.c:
                    if(child.a=="?"):
                        return child
                v1 = MOISMCTS.nodo(n,n.jugador,"?")
                n.c.append(v1)
                v1.r = [0]*len(v1.padre.r)
                return v1
        else:
            #Si el nodo es del jugador que tiene el turno busca si ya tiene un hijo con la acción
            for child in n.c:
                if(child.a==a):
                    return child
            #Si no tiene un hijo con la acción lo crea ya que este siempre puede ver por completo esta acción
            v1 = MOISMCTS.nodo(n,n.jugador,a)
            n.c.append(v1)
            v1.r = [0]*len(v1.padre.r) #Crea una lista de 0s del tamaño de la lista de recompensas del nodo padre
            return v1

    def ejecuta(self,s0):
        movs=self.obtener_movimientos(s0)
        if(len(movs)==1):
            return movs[0]
        elif(len(movs)==0):
            return None
        else:
            jugadores = self.jugadores
            nodos0 = []
            for jugador in jugadores:
                v0=self.nodo(None,jugador)
                v0.r=[0]*len(jugadores)
                nodos0.append(v0)
            t0 = time.time()
            while( time.time() - t0 < self.tiempoEjecucion):
                d0=self.determinization(s0) #Elige una determinización aleatoria de s0
                movs = self.obtener_movimientos(d0) #Obtiene los movimientos disponibles con la determinización
                (nodos,d,movs,actionsWithoutChildren)=self.select(nodos0,d0,movs) #Selecciona un nodo y determinización
                if(len(actionsWithoutChildren)!=0): #Si aún hay acciones en la determinización para los cuales el nodo aún no tiene hijos
                    (nodos,d)=self.expand(nodos,d,actionsWithoutChildren)    #Expande el nodo y determinización
                    movs = self.obtener_movimientos(d) #Obtiene los movimientos disponibles con la determinización                
                r=self.simulate(d,movs)           #Simula el juego hasta el final
                for jugador in jugadores:
                    v=nodos[jugador-1]
                    self.backpropagate(r,v,jugadores)      #Actualiza los valores de los nodos
            nodoJugador = nodos0[s0.jugadorActual-1] #Elige el nodo del jugador que tiene el turno
            mejor_accion = max(nodoJugador.c, key=lambda c: c.n).a #Elige la mejor acción
            if(self.estadisticas):
                print("\nTiempo de ejecución: ", self.tiempoEjecucion)
                for nodo in nodos0:
                    print("\nNodo del jugador: ",nodo.jugador)
                    print("Número de nodos creados: ",self.nodos_creados(nodo))
                    print("Número de nodos visitados: ",nodo.n)
            return mejor_accion   #Devuelve la acción que maximiza la recompensa
    
    #Función para coger el mejor nodo
    @staticmethod
    def best_child(v,movs,jugador,k):
        hijosCompatibles = [c for c in v.c if c.a in movs]
        heuristicas = []
        for children in hijosCompatibles:
            heuristica = ((children.r[jugador])/children.n) + (k * math.sqrt(math.log(children.nP)/children.n))
            heuristicas.append(heuristica)
            #Actualizamos el número de visitas disponibles
            children.nP += 1

        mejorHijo=hijosCompatibles[heuristicas.index(max(heuristicas))]
        return mejorHijo
        
    def select(self,nodos,d,movs):
        n=nodos[d.jugadorActual-1] #El nodo actual es el nodo del jugador que tiene el turno
        accionesSinHijos = n.actions_of_determinization_without_children(movs) #Obtiene las acciones de la determinización sin hijos
        newNodos = nodos
        while(self.es_estado_final(d)==False and len(accionesSinHijos)==0): #Mientras no sea un estado final y no haya acciones de la determinazión sin hijos en el nodo
            jugador = d.jugadorActual-1                  #El jugador el cuál le toca jugar en la determinización
            c=self.best_child(n,movs,jugador,MOISMCTS.k) #Coge el mejor nodo de los nodos compatibles con la determinización
            d=deepcopy(d)                                #Copia la determinización
            d=self.aplicar_movimiento(d,c.a)             #La determinización es la determinización del mejor nodo
            movs = self.obtener_movimientos(d)           #Obtiene los movimientos disponibles con la determinización
            newNodos = []                                #Lista de nodos hijos
            for nodo in nodos:
                newNodo = self.find_or_create_child(nodo,c.a,jugador+1)      #Crea o encuentra el nodo hijo en todos los nodos
                newNodos.append(newNodo)
                if(newNodo.jugador==d.jugadorActual):
                    n=newNodo
            nodos = newNodos
            accionesSinHijos = n.actions_of_determinization_without_children(movs) #Obtiene las acciones de la determinización sin hijos
        return newNodos,d,movs,accionesSinHijos         #Devuelve el nodo y la determinización

    def expand(self,nodos,d,actionsWithoutChildren):
        d=deepcopy(d)                           #Copia la determinización  
        a=random.choice(actionsWithoutChildren) #Elige una acción aleatoria de las acciones de la determinización sin hijos
        jugador = d.jugadorActual
        newNodos = []                           #Los nuevos nodos serán los nodos hijos del nodo actual
        for nodo in nodos:
            newNodo = self.find_or_create_child(nodo,a,jugador)    #Crea o encuentra el nodo hijo en todos los nodos
            newNodos.append(newNodo)            #Añade el nodo hijo a la lista de nuevos nodos
        d=self.aplicar_movimiento(d,a)          #La determinización es la determinización del nodo creado
        return newNodos,d                       #Devuelve el nodo y la determinización

    def simulate(self,d,movs):
        jugadores = self.jugadores              #Obtiene los jugadores del juego
        while(self.es_estado_final(d)==False):  #Mientras no sea un estado final
            a=random.choice(movs)               #Elige una acción aleatoria de las acciones disponibles
            d=self.aplicar_movimiento(d,a)      #Aplica la acción a la determinización
            movs=self.obtener_movimientos(d)    #Obtiene las acciones disponibles con la determinización

        #Crea una lista de 0s del tamaño de la lista de jugadores
        res = [0] * len(jugadores)
        #Cambia los valores de la lista de 0s a la recompensa que obtiene cada jugador
        for jugador in jugadores:                           
            if(self.gana_jugador(d,jugador)):
                indice=jugadores.index(jugador)
                res[indice]=1

        #Si no hay ningún ganador, todos los jugadores empatan
        if (1 not in res):
            res = [0.5] * len(jugadores)
        return res

    @staticmethod
    def backpropagate(r,v1,jugadores):
        while(v1!=None):
            v1.n+=1      #Incrementa el número de veces que se ha visitado el nodo
            #Incrementa la recompensa del nodo para cada jugador
            for jugador in jugadores:
                indiceJugador=jugadores.index(jugador)
                v1.r[indiceJugador]+=r[indiceJugador]
            v1=v1.padre #El nodo actual es el nodo padre del nodo actual