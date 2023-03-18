import random
import pyplAI
from colorama import Fore, init

init(autoreset=True)

#Super Tic Tac Toe, tablero de 3x3 en el que cada casilla incluye un tablero de 3x3
#El jugador 1 juega con el 1 y el jugador 2 con el 2
#Para ganar una casilla del tablero principal se debe ganar la partida dentro de el
#Para ganar la partida se debe hacer 3 en raya en el tablero principal
#Los movimientos tendrán la siguiente forma: (i,j,k,l) donde i,j es la casilla del tablero principal y k,l es la casilla del tablero secundario

#Creamos un tablero en el cual actuara como el tablero principal, y se completará si se gana una partida dentro de el

class UltimateTTT():
    jugadores = [1,2]
    jugadores = 2

    @staticmethod
    def tablero_inicial():
        tablero1=([0,0,0],
                [0,0,0],
                [0,0,0])
        tablero2=([0,0,0],
                [0,0,0],
                [0,0,0])
        tablero3=([0,0,0],
                [0,0,0],
                [0,0,0])
        tablero4=([0,0,0],
                [0,0,0],
                [0,0,0])    
        tablero5=([0,0,0],
                [0,0,0],
                [0,0,0])
        tablero6=([0,0,0],
                [0,0,0],
                [0,0,0])
        tablero7=([0,0,0],
                [0,0,0],
                [0,0,0])    
        tablero8=([0,0,0],
                [0,0,0],
                [0,0,0])
        tablero9=([0,0,0],
                [0,0,0],
                [0,0,0])
        tablero=([tablero1,tablero2,tablero3],
                [tablero4,tablero5,tablero6],
                [tablero7,tablero8,tablero9])
        return tablero

    def __init__(self):
        self.tableroPrincipal=([0,0,0],
                               [0,0,0],
                               [0,0,0])
        self.tablero = UltimateTTT.tablero_inicial()
        self.tableroJugada = (-1,-1)
        self.jugadorActual = 1

    @staticmethod
    def obtiene_movimientos_tablero(tablero):
        movimientos=[]
        for i in range(3):
            for j in range(3):
                if(tablero[i][j]==0):
                    movimientos.append((i,j))
        return movimientos

    def obtiene_movimientos(self):
        movimientos=[]
        tablero=self.tablero
        tablero_principal=self.tableroPrincipal
        tablero_jugada=self.tableroJugada
        if(tablero_jugada==(-1,-1)):
            for i in range(3):
                for j in range(3):
                    if(tablero_principal[i][j]==0):
                        movimientosTablero=self.obtiene_movimientos_tablero(tablero[i][j])
                        for mov in movimientosTablero:
                            movimientos.append((i,j,mov[0],mov[1]))    
        else:
            tablero_secundario=tablero[tablero_jugada[0]][tablero_jugada[1]]
            if(tablero_principal[tablero_jugada[0]][tablero_jugada[1]]==0):
                movimientosTablero=self.obtiene_movimientos_tablero(tablero_secundario)
                for mov in movimientosTablero:
                    movimientos.append((tablero_jugada[0],tablero_jugada[1],mov[0],mov[1]))
            else:
                for i in range(3):
                    for j in range(3):
                        if(tablero_principal[i][j]==0):
                            movimientosTablero=self.obtiene_movimientos_tablero(tablero[i][j])
                            for mov in movimientosTablero:
                                movimientos.append((i,j,mov[0],mov[1]))      
        return random.sample(movimientos, len(movimientos))
        
    def aplica_movimiento(self,a):
        tablero = self.tablero
        jugador = self.jugadorActual
        tablero_secundario=tablero[a[0]][a[1]]
        tablero_secundario[a[2]][a[3]]=jugador
        if(self.gana_jugador_tablero(tablero_secundario,jugador)):
            self.actualiza_tablero_principal((a[0],a[1]),jugador)
        self.jugadorActual = 3-jugador
        self.tableroJugada = (a[2],a[3])
        return self

    def imprime_tablero(self):
        tablero=self.tablero
        for i in range(3):
            if(i==0):
                print("+-------+-+-------+-+-------+")
            for j in range(3):
                linea=""
                for k in range(3):
                    linea=linea+"| "+str(tablero[i][k][j]).replace("[","").replace("]","").replace(",","")+" | "
                print(linea)
            print("+-------+-+-------+-+-------+")    

    def gana_jugador(self,jugador):
        return self.gana_jugador_tablero(self.tableroPrincipal,jugador)

    @staticmethod
    def gana_jugador_tablero(tablero,jugador):
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

    def actualiza_tablero_principal(self,coordenadas, jugador):
        tablero_principal=self.tableroPrincipal
        tablero_principal[coordenadas[0]][coordenadas[1]]=jugador

    def es_estado_final(self):
        num_movs = len(self.obtiene_movimientos())
        tablero_principal = self.tableroPrincipal
        #Si no hay movimientos posibles la partida ha terminado, pudiendo ser empate o victoria
        if(num_movs==0):
            return True
        #Comprobamos si gana algun jugador
        if(self.gana_jugador_tablero(tablero_principal,1) or self.gana_jugador_tablero(tablero_principal,2)):
            return True
        return False

    @staticmethod
    def evalua_tablero(tablero, jugador):
        contadorPosibles3 = 0
        contadorPosibles3Enemigos = 0
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
        return (contadorPosibles3 - contadorPosibles3Enemigos)

    def heuristica(self,jugador):
        tableros = self.tablero
        tableroPrincipal=self.tableroPrincipal
        tableroListaFichas=[casilla for fila in tableroPrincipal for casilla in fila]
        #Tableros pequeños ganados suman 5 puntos
        res = 5*(tableroListaFichas.count(jugador)-tableroListaFichas.count(3-jugador))
        #El tablero del medio suma 10 puntos si está ganado
        if(tableroListaFichas[4]==jugador):
            res+=10
        elif(tableroListaFichas[4]==3-jugador):
            res-=10
        #Ganar un tablero de las esquinas suma 3 puntos
        esquinas=[0,2,6,8]
        for esquina in esquinas:
            if(tableroListaFichas[esquina]==jugador):
                res+=3
            elif(tableroListaFichas[esquina]==3-jugador):
                res-=3
        #Ganar la casilla del medio de cualquier tablero suma 3 punto
        for linea in tableros:
            for tablero in linea:
                if(tablero[1][1]==jugador):
                    res+=3
                elif(tablero[1][1]==3-jugador):
                    res-=3
        #Ganar cualquier casilla en el tablero central suma 3 punto
        for casilla in tableros[1][1]:
            if(casilla==jugador):
                res+=3
            elif(casilla==3-jugador):
                res-=3
        #Se evalua el tablero principal
        res+=4*self.evalua_tablero(tableroPrincipal,jugador)
        #Se evalua cada uno de los tableros pequeños
        for linea in tableros:
            for tablero in linea:
                res+=2*self.evalua_tablero(tablero,jugador)
        return res

    def imprime_final(self):
        self.imprime_tablero()
        tablero_final = self.tableroPrincipal
        for i in range(3):
            print(tablero_final[i])
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
        print(Fore.RED+"Turno Jugador "+str(self.jugadorActual))
        self.imprime_tablero()
        movimientos = self.obtiene_movimientos()
        imprime_movimientos(movimientos)
        print("Introduce el movimiento que quieres realizar: ")
        movimiento=int(input())
        while(movimiento<=0 or movimiento>len(movimientos)):
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

def imprime_movimientos(movs):
    print("Movimientos posibles: ")
    i=1
    for mov in movs:
        print(i,"º Movimiento:")
        print("     Tablero: (", mov[0],",",mov[1],")")
        print("     Casilla: (", mov[2],",",mov[3],")")

        i+=1

def imprime_estadisticas(tiemposMiniMax, tiempoMCTS):
    tiempoMiniMax=sum(tiemposMiniMax)/len(tiemposMiniMax)
    print("Tiempo de ejecución medio Minimax: ", tiempoMiniMax)
    print("Tiempo de ejecución MCTS: ", tiempoMCTS)

def jugadorContraAlgoritmo():
    algoritmo = int(input("¿Contra qué algoritmo quieres jugar? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo<1 or algoritmo>2):
        algoritmo = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo==1):
        depth = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth<=0):
            depth = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo = pyplAI.MinMax(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador,UltimateTTT.heuristica, UltimateTTT.jugadores, depth)
    else:
        tiempoEjecucion = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion<=0):
            tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo = pyplAI.MCTS(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador, UltimateTTT.jugadores, tiempoEjecucion)
    
    posicionJugador = int(input("¿En qué posición quieres jugar? (1-2) \n"))
    while(posicionJugador<1 or posicionJugador>2):
        posicionJugador = int(input("Introduce 1 si quieres jugar primero o 2 si quieres jugar segundo: \n"))
    
    s = UltimateTTT()
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
    s = UltimateTTT()
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
        algoritmo1 = pyplAI.MinMax(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador,UltimateTTT.heuristica, UltimateTTT.jugadores, depth1)
    else:
        tiempoEjecucion1 = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion1<=0):
            tiempoEjecucion1 = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo1 = pyplAI.MCTS(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador, UltimateTTT.jugadores, tiempoEjecucion1)
    
    algoritmo2 = int(input("¿Qué algoritmo quieres usar como segundo jugador? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo2<1 or algoritmo2>2):
        algoritmo2 = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo2==1):
        depth2 = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth2<=0):
            depth2 = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo2 = pyplAI.MinMax(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador,UltimateTTT.heuristica, UltimateTTT.jugadores, depth2)
    else:
        tiempoEjecucion2 = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion2<=0):
            tiempoEjecucion2 = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo2 = pyplAI.MCTS(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador, UltimateTTT.jugadores, tiempoEjecucion2)
    
    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        s = UltimateTTT()
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
        resultados.append(s.gana_jugador(1))
        i+=1
    if(algoritmo1.__class__.__name__=="MCTS"):
        print("\nPartidas Ganadas por el MCTS 1: ",resultados.count(1))
    else:
        print("\nPartidas Ganadas por el Minimax 1: ",resultados.count(1))
    if(algoritmo2.__class__.__name__=="MCTS"):
        print("Partidas Ganadas por el MCTS 2: ",resultados.count(2))
    else:
        print("Partidas Ganadas por el Minimax 2: ",resultados.count(2))
    print("Empates: ",resultados.count(0))

def algoritmoContraAleatorio():
    algoritmo = int(input("¿Qué algoritmo quieres usar? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo<1 or algoritmo>2):
        algoritmo = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo==1):
        depth = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth<=0):
            depth = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo = pyplAI.MinMax(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador,UltimateTTT.heuristica, UltimateTTT.jugadores, depth)
    else:
        tiempoEjecucion = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion<=0):
            tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo = pyplAI.MCTS(UltimateTTT.aplica_movimiento,UltimateTTT.obtiene_movimientos,UltimateTTT.es_estado_final,UltimateTTT.gana_jugador, UltimateTTT.jugadores, tiempoEjecucion)
    
    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        s = UltimateTTT()
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
    print("\nBienvenido al juego Ultimate TicTacToe\n")
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
