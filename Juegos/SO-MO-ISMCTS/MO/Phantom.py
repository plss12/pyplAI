from copy import deepcopy
import random
import pyplAI
from colorama import Fore, init

init(autoreset=True)

class Phantom:
    listaJugadores = [1,2]
    jugadores = 2

    def __init__(self):
        self.tablero=([0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0])
        self.jugadorActual=1
        self.jugadorAnterior=0
        self.posicionesVisiblesJugadores = [[],[]] #Posiciones visibles por cada jugador del jugador contrario
        self.fichasJugadores = [0,0]
    
    def obtiene_movimientos(self):
        movimientos=[]
        tablero=self.tablero
        casillasVisibles = self.posicionesVisiblesJugadores[self.jugadorActual-1]
        for i in range(4):
            for j in range(4):
                if((i,j) not in casillasVisibles and tablero[i][j]!=self.jugadorActual):
                    movimientos.append((i,j))
        return random.sample(movimientos,len(movimientos))
    
    def aplica_movimiento(self,a):
        tablero = self.tablero
        jugador = self.jugadorActual
        jugadorRival = 3-jugador
        if(tablero[a[0]][a[1]]==0):
            tablero[a[0]][a[1]]=jugador
            self.jugadorActual = jugadorRival
            self.jugadorAnterior = jugador
            self.fichasJugadores[jugador-1] += 1
        elif(tablero[a[0]][a[1]]==jugadorRival):
            self.jugadorAnterior = jugador
            self.posicionesVisiblesJugadores[jugador-1].append(a)
        return self
    
    def imprime_tablero(self, jugadores):
        tablero = self.tablero
        for i in range(4):
            print("\n")
            for j in range(4):
                if(len(jugadores)==1):
                    jugador = jugadores[0]
                    if((i,j) in self.posicionesVisiblesJugadores[jugador-1] or tablero[i][j]==jugador):
                        print(tablero[i][j],end=" ")
                    else:
                        print("0",end=" ")
                else:
                    print(tablero[i][j],end=" ")
        print("\n")
    
    def imprime_movimientos(self, movimientos):
        for i in range(len(movimientos)):
            print(i+1,": ",movimientos[i])

    def imprime_estado(self):
        self.imprime_tablero([self.jugadorActual])
        if(self.jugadorActual==self.jugadorAnterior):
            print("La posición que seleccionó estaba ocupada por el rival, elija otra posición\n")
        print("\n")

    def gana_jugador(self,jugador):
        tablero=self.tablero
        #Comprobamos si hay un 4 en raya
        if(tablero[0][0]==tablero[1][1]==tablero[2][2]==tablero[3][3]==jugador):
            return True
        elif(tablero[0][3]==tablero[1][2]==tablero[2][1]==tablero[3][0]==jugador):
            return True
        else:
            for i in range(4):
                if(tablero[i][0]==tablero[i][1]==tablero[i][2]==tablero[i][3] and tablero[i][0]==jugador):
                    return True
                elif(tablero[0][i]==tablero[1][i]==tablero[2][i]==tablero[3][i] and tablero[0][i]==jugador):
                    return True
        return False
    
    def es_estado_final(self):
        num_movs=len(self.obtiene_movimientos())
        #Si no hay movimientos posibles la partida ha terminado, pudiendo ser empate o victoria
        if(num_movs==0):
            return True
        #Comprobamos si gana algun jugador
        if(self.gana_jugador(1) or self.gana_jugador(2)):
            return True
        return False

    def imprime_final(self):
        self.imprime_tablero(Phantom.listaJugadores)
        #Al aplicar movimiento se cambia el jugador, el ganador es el jugador anterior
        if(self.gana_jugador(1)):
            print("Gana el jugador 1")
            return 1
        elif(self.gana_jugador(2)):
            print("Gana el jugador 2")
            return 2
        else:
            print("Empate")
            return 0

    def turno_jugador(self):
        self.imprime_estado()
        movimientos=self.obtiene_movimientos()
        self.imprime_movimientos(movimientos)
        print("Introduce el movimiento que quieres realizar: ")
        movimiento=int(input())
        while(movimiento<=0 or movimiento>len(movimientos)):
            print("Movimiento invalido, introduce un movimiento: ")
            movimiento=int(input())
        return self.aplica_movimiento(movimientos[movimiento-1])
    
    def turno_mcts(self,mcts):
        self.imprime_estado()
        mov = mcts.ejecuta(self)
        if(mov!=None):
            return self.aplica_movimiento(mov)
        else:
            return self
    
    def turno_aleatorio(self):
        self.imprime_estado()
        movimientos=self.obtiene_movimientos()
        return self.aplica_movimiento(random.choice(movimientos))
    
    def determinization(self):
        determinization = deepcopy(self)
        tablero = determinization.tablero
        jugador = determinization.jugadorActual
        jugadorRival = 3-jugador
        fichasRivalVisiblesPorJugador=determinization.posicionesVisiblesJugadores[jugador-1]
        #Obtenemos el número de fichas que el jugador no sabe donde estan situadas
        numeroFichasRival=determinization.fichasJugadores[jugadorRival-1]
        numeroFichaJugador=determinization.fichasJugadores[jugador-1]
        numeroEspacios=16-numeroFichasRival-numeroFichaJugador
        numeroFichasRivalVisibles=len(fichasRivalVisiblesPorJugador)
        #Obtenemos una lista con todas las fichas que el jugador no sabe donde estan situadas
        fichas=[]
        espacios=[0]*numeroEspacios
        fichasRival=[jugadorRival]*(numeroFichasRival-numeroFichasRivalVisibles)
        fichas.extend(espacios)
        fichas.extend(fichasRival)
        random.sample(fichas,len(fichas))
        #Recorremos el tablero y colocamos aleatoriamente las fichas que no sabemos donde estan situadas
        #en las posiciones que no sabemos que contienen
        for i in range(4):
            for j in range(4):
                if(tablero[i][j]==0 or (tablero[i][j]==jugadorRival and (i,j) not in fichasRivalVisiblesPorJugador)):
                    tablero[i][j]=random.choice(fichas)
                    fichas.remove(tablero[i][j])
        return determinization
    
    @staticmethod
    def accion_visible(accion):
        return False

def jugadorContraISMCTS():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del ISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))

    algoritmo= int(input("¿Quieres jugar contra el algoritmo de SO(1) o contra el algoritmo de MO(2)?: \n"))
    while(algoritmo<1 or algoritmo>2):
        algoritmo = int(input("Introduce 1 para utilizar MOISMCTS o 2 para utilizar SOISMCTS: \n"))

    if(algoritmo==1):
        mcts = pyplAI.SOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.jugadores,tiempoEjecucion, True)
    else:
        mcts = pyplAI.MOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.accion_visible,Phantom.jugadores,tiempoEjecucion, True)
    
    posicionJugador = int(input("¿Desea jugar primero o segundo? (1-2)\n"))
    while(posicionJugador<1 or posicionJugador>2):
        posicionJugador = int(input("Introduce 1 para ser primero o 2 para ser segundo: \n"))

    estado=Phantom()
    while(estado.es_estado_final()==False):
        jugador = estado.jugadorActual
        if(jugador==posicionJugador):
            print(Fore.RED+"\nTurno del jugador "+str(jugador))
            estado.turno_jugador()
        else:
            print(Fore.BLUE+"\nTurno del SOISMCTS "+str(jugador))
            estado.turno_mcts(mcts)
    estado.imprime_final()

def jugadorContraJugador():
    estado=Phantom()
    while(estado.es_estado_final()==False):
        jugador = estado.jugadorActual
        if(jugador==1):
            print(Fore.RED+"\nTurno del jugador "+str(jugador))
        else:
            print(Fore.BLUE+"\nTurno del jugador "+str(jugador))
        estado.turno_jugador()
    estado.imprime_final()

def ISMCTSContraISMCTS():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del ISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    
    numeroPartidas = int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))

    modo = int(input("¿Desea simular SO vs S0 (1), SO vs MO (2), MO vs SO (3) o MO vs MO (4)?: \n"))
    while(modo<1 or modo>4):
        modo = int(input("Introduce 1 para simular SO vs SO, 2 para simular SO vs MO, 3 para simular MO vs SO o 4 para simular MO vs MO: \n"))

    if(modo==1):
        mcts1=pyplAI.SOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.jugadores,tiempoEjecucion, True)
        mcts2=pyplAI.SOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.jugadores,tiempoEjecucion, True)
    elif(modo==2):
        mcts1=pyplAI.SOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.jugadores,tiempoEjecucion, True)
        mcts2=pyplAI.MOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.accion_visible,Phantom.jugadores,tiempoEjecucion, True)
    elif(modo==3):
        mcts1=pyplAI.MOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.accion_visible,Phantom.jugadores,tiempoEjecucion, True)
        mcts2=pyplAI.SOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.jugadores,tiempoEjecucion, True)
    else:
        mcts1=pyplAI.MOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.accion_visible,Phantom.jugadores,tiempoEjecucion, True)
        mcts2=pyplAI.MOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.accion_visible,Phantom.jugadores,tiempoEjecucion, True)

    resultados=[]
    i=0
    for i in range(numeroPartidas):
        estado=Phantom()
        while(estado.es_estado_final()==False):
            jugador = estado.jugadorActual
            if(jugador==1):
                if(modo==1 or modo==2):
                    print(Fore.RED+"\nTurno del SOISMCTS "+str(jugador))
                else:
                    print(Fore.RED+"\nTurno del MOISMCTS "+str(jugador))
                estado.turno_mcts(mcts1)
            else:
                if(modo==1 or modo==3):
                    print(Fore.BLUE+"\nTurno del SOISMCTS "+str(jugador))
                else:
                    print(Fore.BLUE+"\nTurno del MOISMCTS "+str(jugador))
                estado.turno_mcts(mcts2)
        res=estado.imprime_final()
        resultados.append(res)
        i+=1
    print("\nResultados de las partidas: \n")
    if(modo==1 or modo==2):
        print("Ganadas por SOISMCTS: "+str(resultados.count(1)))
    else:
        print("Ganadas por MOISMCTS: "+str(resultados.count(1)))
    if(modo==1 or modo==3):
        print("Ganadas por SOISMCTS: "+str(resultados.count(2)))
    else:
        print("Ganadas por MOISMCTS: "+str(resultados.count(2)))
    print("Empates: "+str(resultados.count(0)))

def ISMCTSContraAleatorio():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del ISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    
    numeroPartidas = int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))

    modo = int(input("¿Desea simular SO vs aleatorio (1), MO vs aleatorio (2)?: \n"))
    while(modo<1 or modo>2):
        modo = int(input("Introduce 1 para simular SO vs aleatorio o 2 para simular MO vs aleatorio: \n"))
    
    if(modo==1):
        mcts=pyplAI.SOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.jugadores,tiempoEjecucion, True)
    else:
        mcts=pyplAI.MOISMCTS(Phantom.aplica_movimiento,Phantom.obtiene_movimientos,Phantom.es_estado_final,Phantom.gana_jugador,Phantom.determinization,Phantom.jugadores,tiempoEjecucion, True)
    
    resultados=[]
    i=0
    for i in range(numeroPartidas):
        estado=Phantom()
        while(estado.es_estado_final()==False):
            jugador = estado.jugadorActual
            if(jugador==1):
                if(modo==1):
                    print(Fore.RED+"\nTurno del SOISMCTS "+str(jugador))
                else:
                    print(Fore.RED+"\nTurno del MOISMCTS "+str(jugador))
                estado.turno_mcts(mcts)
            else:
                print(Fore.BLUE+"\nTurno del jugador aleatorio "+str(jugador))
                estado.turno_aleatorio()
        res=estado.imprime_final()
        resultados.append(res)
        i+=1
    print("\nResultados de las partidas: \n")
    if(modo==1):
        print("Ganadas por SOISMCTS: "+str(resultados.count(1)))
    else:
        print("Ganadas por MOISMCTS: "+str(resultados.count(1)))
    print("Ganadas por jugador aleatorio: "+str(resultados.count(2)))
    print("Empates: "+str(resultados.count(0)))

def main():
    print("\nBienvenido al juego Phantom\n")
    print("Estos son los modos que contiene este juego:\n")
    print("1. Jugar una partida contra algún algoritmo de MCTS")
    print("2. Jugar una partida contra otro jugador")
    print("3. Simular partidas entre dos algoritmos de MCTS")
    print("4. Simular partidas algoritmos de MCTS contra jugadas aleatorias")
    opcion=int(input("\nElige un modo: \n"))
    while(opcion<1 or opcion>4):
        opcion=int(input("Opción no válida, elige una opción válida: \n"))
    if(opcion==1):
        jugadorContraISMCTS()
    elif(opcion==2):
        jugadorContraJugador()
    elif(opcion==3):
        ISMCTSContraISMCTS()
    elif(opcion==4):
        ISMCTSContraAleatorio()

if __name__ == "__main__":
    main()