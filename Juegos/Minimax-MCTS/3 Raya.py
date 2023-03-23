from copy import deepcopy
import random
import pyplAI
from colorama import Fore, init

init(autoreset=True)

class TicTacToe:
    jugadores = 2

    def __init__(self):
        self.tablero=([0,0,0],
                      [0,0,0],
                      [0,0,0])
        self.jugadorActual=1

    def obtiene_movimientos(self):
        movimientos=[]
        tablero=self.tablero
        for i in range(3):
            for j in range(3):
                if(tablero[i][j]==0):
                    movimientos.append((i,j))
        return random.sample(movimientos, len(movimientos))

    def aplica_movimiento(self,a):
        tablero = self.tablero
        jugador = self.jugadorActual
        tablero[a[0]][a[1]]=jugador
        self.jugadorActual=2 if jugador==1 else 1
        return self

    def gana_jugador(self,jugador):
        tablero=self.tablero
        #Comprobamos si hay un 3 en raya
        if(tablero[0][0]==tablero[1][1]==tablero[2][2] and tablero[0][0]==jugador):
            return True
        elif(tablero[0][2]==tablero[1][1]==tablero[2][0] and tablero[0][2]==jugador):
            return True
        else:
            for i in range(3):
                if(tablero[i][0]==tablero[i][1]==tablero[i][2] and tablero[i][0]==jugador):
                    return True
                elif(tablero[0][i]==tablero[1][i]==tablero[2][i] and tablero[0][i]==jugador):
                    return True
        return False

    def es_estado_final(self):
        num_movs = len(self.obtiene_movimientos())
        #Si no hay movimientos posibles la partida ha terminado, pudiendo ser empate o victoria
        if(num_movs==0):
            return True
        #Comprobamos si gana algun jugador
        if(self.gana_jugador(1) or self.gana_jugador(2)):
            return True
        return False
    
    def imprime_tablero(self):
        tablero = self.tablero
        for i in range(3):
            print("\n")
            for j in range(3):
                print(tablero[i][j],end=" ")
        print("\n")
    
    def imprime_final(self):
        self.imprime_tablero()
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

    def heuristica(self,jugador):
        tablero = self.tablero
        contadorPosibles3 = 0
        contadorPosibles3Enemigos = 0
        contadorPosibles2 = 0
        contadorPosibles2Enemigos = 0
        lineas = (([0,0],[0,1],[0,2]),([1,0],[1,1],[1,2]),([2,0],[2,1],[2,2]),([0,0],[1,0],[2,0]),([0,1],[1,1],[2,1]),([0,2],[1,2],[2,2]),([0,0],[1,1],[2,2]),([0,2],[1,1],[2,0]))
        combinacionesUno=([0,1,2],[1,2,0],[2,0,1])
        for linea in lineas:
            for combinacion in combinacionesUno:
                x1 = linea[combinacion[0]][0]
                y1 = linea[combinacion[0]][1]
                x2 = linea[combinacion[1]][0]
                y2 = linea[combinacion[1]][1]
                x3 = linea[combinacion[2]][0]
                y3 = linea[combinacion[2]][1]
                if tablero[x1][y1]==tablero[x2][y2] == jugador and tablero[x3][y3] == 0:
                    contadorPosibles3+=1
                elif tablero[x1][y1]==tablero[x2][y2] == 3-jugador and tablero[x3][y3] == 0:
                    contadorPosibles3Enemigos+=1
                if tablero[x1][y1]== jugador and tablero[x2][y2] == tablero[x3][y3] == 0:
                    contadorPosibles3+=1
                elif tablero[x1][y1]== 3-jugador and tablero[x2][y2] == tablero[x3][y3] == 0:
                    contadorPosibles3Enemigos+=1
        return 10*(contadorPosibles3 - contadorPosibles3Enemigos)+ contadorPosibles2 - contadorPosibles2Enemigos

    def turno_jugador(self):
        print(Fore.RED+"Turno Jugador "+str(self.jugadorActual))
        self.imprime_tablero()
        movimientos = self.obtiene_movimientos()
        imprime_movimientos(movimientos)
        print("Introduce el movimiento que quieres realizar: ")
        movimiento=int(input())
        while(movimiento<1 or movimiento>len(movimientos)):
            print("Movimiento invalido, introduce un movimiento: ")
            movimiento=int(input())
        return self.aplica_movimiento(movimientos[movimiento-1])
    
    def turno_mcts(self,mcts):
        print(Fore.BLUE+"Turno MCTS "+str(self.jugadorActual))
        self.imprime_tablero()
        mov = mcts.ejecuta(self)
        if(mov!=None):
            return self.aplica_movimiento(mov)
        else:
            return self
    
    def turno_minimax(self,minimax):
        print(Fore.GREEN+"Turno Minimax "+str(self.jugadorActual))
        self.imprime_tablero()
        mov = minimax.ejecuta(self)
        if(mov!=None):
            return self.aplica_movimiento(mov)
        else:
            return self
    
    def turno_aleatorio(self):
        print(Fore.RED+"Turno Aleatorio "+str(self.jugadorActual))
        self.imprime_tablero()
        movimientos = self.obtiene_movimientos()
        mov = random.choice(movimientos)
        return self.aplica_movimiento(mov)
    
def imprime_movimientos(movimientos):
    for i in range(len(movimientos)):
        print("Movimiento "+str(i+1)+": \n  Fila -",movimientos[i][0]+1," \n  Columna -",movimientos[i][1]+1,"\n")

def imprime_estadisticas(tiemposMiniMax, tiempoMCTS):
    tiempoMiniMax=sum(tiemposMiniMax)/len(tiemposMiniMax)
    print("Tiempo de ejecución medio Minimax: ", tiempoMiniMax)
    print("Tiempo de ejecución MCTS: ", tiempoMCTS)

def determinization(s):
    determinization = deepcopy(s)
    return determinization

def jugadorContraAlgoritmo():
    algoritmo = int(input("¿Contra qué algoritmo quieres jugar? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo<1 or algoritmo>2):
        algoritmo = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo==1):
        depth = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth<=0):
            depth = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo = pyplAI.Minimax(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador,TicTacToe.heuristica, TicTacToe.jugadores, depth, True)
    else:
        tiempoEjecucion = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion<=0):
            tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo = pyplAI.MCTS(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador, TicTacToe.jugadores, tiempoEjecucion, True)
    
    posicionJugador = int(input("¿En qué posición quieres jugar? (1-2) \n"))
    while(posicionJugador<1 or posicionJugador>2):
        posicionJugador = int(input("Introduce 1 si quieres jugar primero o 2 si quieres jugar segundo: \n"))
    
    s = TicTacToe()
    while(s.es_estado_final()==False):
        jugador = s.jugadorActual
        if(jugador==posicionJugador):
            s = s.turno_jugador()
        else:
            if(algoritmo.__class__.__name__=="MCTS"):
                s = s.turno_mcts(algoritmo)
            else:
                s=s.turno_minimax(algoritmo)    
    s.imprime_final()    

def jugadorContraJugador():
    s = TicTacToe()
    while(s.es_estado_final()==False):
        s = s.turno_jugador()
    s.imprime_final()

def algoritmoContraAlgoritmo():
    algoritmo1 = int(input("¿Qué algoritmo quieres usar como primer jugador? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo1<1 or algoritmo1>2):
        algoritmo1 = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo1==1):
        depth1 = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth1<=0):
            depth1 = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo1 = pyplAI.Minimax(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador,TicTacToe.heuristica, TicTacToe.jugadores, depth1, True)
    else:
        tiempoEjecucion1 = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion1<=0):
            tiempoEjecucion1 = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo1 = pyplAI.MCTS(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador, TicTacToe.jugadores, tiempoEjecucion1, True)
    
    algoritmo2 = int(input("¿Qué algoritmo quieres usar como segundo jugador? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo2<1 or algoritmo2>2):
        algoritmo2 = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo2==1):
        depth2 = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth2<=0):
            depth2 = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo2 = pyplAI.Minimax(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador,TicTacToe.heuristica, TicTacToe.jugadores, depth2, True)
    else:
        tiempoEjecucion2 = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion2<=0):
            tiempoEjecucion2 = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo2 = pyplAI.MCTS(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador, TicTacToe.jugadores, tiempoEjecucion2, True)
    
    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        s = TicTacToe()
        while(s.es_estado_final()==False):
            if(s.jugadorActual==1):
                if(algoritmo1.__class__.__name__=="MCTS"):
                    s = s.turno_mcts(algoritmo1)
                else:
                    s=s.turno_minimax(algoritmo1)
            else:
                if(algoritmo2.__class__.__name__=="MCTS"):
                    s = s.turno_mcts(algoritmo2)
                else:
                    s=s.turno_minimax(algoritmo2)
        s.imprime_final()
        resultados.append(s.gana_jugador(1))
        i+=1
    if(algoritmo1.__class__.__name__=="MCTS"):
        print("\nPartidas Ganadas por el MCTS 1: ",resultados.count(1))
    else:
        print("\nPartidas Ganadas por el Minimax 1: ",resultados.count(1))
    if(algoritmo2.__class__.__name__=="MCTS"):
        print("Partidas Ganadas por el MCTS 2: ",resultados.count(2))
    else:
        print("Partidas Ganadas por el MiniMax 2: ",resultados.count(2))
    print("Empates: ",resultados.count(0))

def algoritmoContraAleatorio():
    algoritmo = int(input("¿Qué algoritmo quieres usar? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo<1 or algoritmo>2):
        algoritmo = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo==1):
        depth = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth<=0):
            depth = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo = pyplAI.Minimax(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador,TicTacToe.heuristica, TicTacToe.jugadores, depth, True)
    else:
        tiempoEjecucion = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion<=0):
            tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo = pyplAI.MCTS(TicTacToe.aplica_movimiento,TicTacToe.obtiene_movimientos,TicTacToe.es_estado_final,TicTacToe.gana_jugador, TicTacToe.jugadores, tiempoEjecucion, True)
    
    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        s = TicTacToe()
        while(s.es_estado_final()==False):
            jugador = s.jugadorActual
            if(jugador==1):
                if(algoritmo.__class__.__name__=="MCTS"):
                    s = s.turno_mcts(algoritmo)
                else:
                    s=s.turno_minimax(algoritmo)
            else:
                s = s.turno_aleatorio()
        res=s.imprime_final()
        resultados.append(res)
        i+=1
    if(algoritmo.__class__.__name__=="MCTS"):
        print("\nPartidas Ganadas por el MCTS: ",resultados.count(1))
    else:
        print("\nPartidas Ganadas por el Minimax: ",resultados.count(1))
    print("Partidas Ganadas por el jugador aleatorio: ",resultados.count(2))
    print("Empates: ",resultados.count(0))


def main():
    print("\nBienvenido al juego del 3 en raya\n")
    print("Estos son los modos que contiene este juego:\n")
    print("1. Jugar una partida contra algún algoritmo (Minimax O MCTS)")
    print("2. Jugar una partida contra otro jugador")
    print("3. Simular partida entre dos algoritmos (Minimax y MCTS)")
    print("4. Simular partidas entre algún algoritmo y jugadas aleatorias")
    opcion=int(input("\nElige un modo: \n"))
    while(opcion<1 or opcion>4):
        opcion=int(input("Opción no válida, elige una opción válida: \n"))
    if(opcion==1):
        jugadorContraAlgoritmo()
    elif(opcion==2):
        jugadorContraJugador()
    elif(opcion==3):
        algoritmoContraAlgoritmo()
    elif(opcion==4):
        algoritmoContraAleatorio()

if __name__ == "__main__":
    main()