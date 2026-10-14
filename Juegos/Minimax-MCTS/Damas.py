from copy import deepcopy
import random
import time
import pyplAI
from colorama import Fore, init

init(autoreset=True)

#Creamos una funcion la cual convierte la coordenada i en las coordenadas que usamos visualmente, ya que la i del indice empieza en 0 pero seria la ultima coordenada del tablero
def cambio_coordenada(len,i):
    newI=len-1-i
    return newI

class Damas:
    jugadores = 2

    def __init__(self,turnos):
        #Se juega en las casillas que incluyen la esquina inferior derecha de cada jugador
        self.tablero = ([1,0,1,0,1,0,1,0],
                        [0,1,0,1,0,1,0,1],
                        [1,0,1,0,1,0,1,0],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [0,2,0,2,0,2,0,2],
                        [2,0,2,0,2,0,2,0],
                        [0,2,0,2,0,2,0,2])
        self.jugadorActual = 2
        self.turnos = turnos

    def heuristica(self,jugador):
        tablero = self.tablero
        contadorFichas=0
        contadorDamas=0
        contadorFichasEnemigas=0
        contadorDamasEnemigas=0
        for i in range(len(tablero)):
            for j in range(len(tablero)):
                if(tablero[i][j]==jugador):
                    contadorFichas+=1
                elif(tablero[i][j]==jugador+2):
                    contadorDamas+=1
                elif(tablero[i][j]==3-jugador):
                    contadorFichasEnemigas+=1
                elif(tablero[i][j]==3-jugador+2):
                    contadorDamasEnemigas+=1
        return 4*(contadorDamas-contadorDamasEnemigas)+(contadorFichas-contadorFichasEnemigas)

    DIAGONALES = ((1,1),(1,-1),(-1,1),(-1,-1))

    @staticmethod
    def dentro(i,j):
        return 0<=i<8 and 0<=j<8

    def es_rival(self,i,j,jugador):
        return self.tablero[i][j] in (3-jugador, 3-jugador+2)

    #La casilla de salida de la ficha que mueve cuenta como vacía durante su jugada
    def esta_vacia(self,i,j,origen):
        return self.tablero[i][j]==0 or (i,j)==origen

    #Secuencias de captura de un peón desde (i,j). Las piezas capturadas siguen en el tablero hasta
    #el final de la jugada, por lo que no se pueden saltar dos veces. El peón solo captura hacia delante
    def capturas_peon(self,i,j,jugador,capturadas,origen):
        res = []
        di = 1 if jugador==1 else -1
        for dj in (1,-1):
            ri, rj = i+di, j+dj
            li, lj = i+2*di, j+2*dj
            if(Damas.dentro(li,lj) and self.es_rival(ri,rj,jugador) and (ri,rj) not in capturadas and self.esta_vacia(li,lj,origen)):
                nuevas = capturadas+[(ri,rj)]
                siguientes = self.capturas_peon(li,lj,jugador,nuevas,origen)
                res.extend(siguientes if siguientes else [(nuevas,(li,lj))])
        return res

    #Secuencias de captura de una dama desde (i,j): captura a distancia y puede caer en cualquier casilla
    #libre detrás de la pieza capturada
    def capturas_dama(self,i,j,jugador,capturadas,origen):
        res = []
        for di, dj in Damas.DIAGONALES:
            ri, rj = i+di, j+dj
            while(Damas.dentro(ri,rj) and self.esta_vacia(ri,rj,origen)):
                ri, rj = ri+di, rj+dj
            if(not Damas.dentro(ri,rj) or not self.es_rival(ri,rj,jugador) or (ri,rj) in capturadas):
                continue
            li, lj = ri+di, rj+dj
            while(Damas.dentro(li,lj) and self.esta_vacia(li,lj,origen)):
                nuevas = capturadas+[(ri,rj)]
                siguientes = self.capturas_dama(li,lj,jugador,nuevas,origen)
                res.extend(siguientes if siguientes else [(nuevas,(li,lj))])
                li, lj = li+di, lj+dj
        return res

    #Movimientos sin captura: el peón avanza una casilla en diagonal y la dama, las que quiera
    def movimientos_simples(self,i,j,jugador,dama):
        res = []
        adelante = 1 if jugador==1 else -1
        direcciones = Damas.DIAGONALES if dama else ((adelante,1),(adelante,-1))
        for di, dj in direcciones:
            ni, nj = i+di, j+dj
            while(Damas.dentro(ni,nj) and self.tablero[ni][nj]==0):
                res.append((j,cambio_coordenada(8,i),nj,cambio_coordenada(8,ni)))
                if not dama:
                    break
                ni, nj = ni+di, nj+dj
        return res

    #Devuelve los movimientos legales. Capturar es obligatorio y se debe elegir la secuencia que capture
    #más piezas (ley de la cantidad) y, a igualdad, la que capture más damas (ley de la calidad).
    #Los movimientos simples son (columna, fila, nueva columna, nueva fila) y las capturas
    #[(columna, fila, nueva columna, nueva fila), [(columna, fila) de cada pieza capturada]],
    #con las filas numeradas de abajo (0) a arriba (7)
    def obtiene_movimientos(self):
        tablero = self.tablero
        jugador = self.jugadorActual
        capturas = []
        simples = []
        for i in range(8):
            for j in range(8):
                ficha = tablero[i][j]
                if(ficha!=jugador and ficha!=jugador+2):
                    continue
                dama = ficha==jugador+2
                if(dama):
                    secuencias = self.capturas_dama(i,j,jugador,[],(i,j))
                else:
                    secuencias = self.capturas_peon(i,j,jugador,[],(i,j))
                for capturadas, (fi, fj) in secuencias:
                    numDamas = sum(1 for (ci,cj) in capturadas if tablero[ci][cj]>2)
                    movimiento = [(j,cambio_coordenada(8,i),fj,cambio_coordenada(8,fi)), [(cj,cambio_coordenada(8,ci)) for (ci,cj) in capturadas]]
                    capturas.append((len(capturadas), numDamas, movimiento))
                if(not capturas):
                    simples.extend(self.movimientos_simples(i,j,jugador,dama))
        if(capturas):
            mejor = max((c[0],c[1]) for c in capturas)
            movimientos = []
            vistos = set()
            for numero, numDamas, movimiento in capturas:
                #Dos caminos que capturan las mismas piezas y acaban en la misma casilla son la misma jugada
                clave = (movimiento[0], frozenset(movimiento[1]))
                if((numero,numDamas)==mejor and clave not in vistos):
                    vistos.add(clave)
                    movimientos.append(movimiento)
        else:
            movimientos = simples
        return random.sample(movimientos, len(movimientos))

    def aplica_movimiento(self,movimiento):
        tablero =self.tablero
        jugador = self.jugadorActual
        self.jugadorActual = 3 - self.jugadorActual
        self.turnos = self.turnos - 1
        if(len(movimiento)==4):
            i=movimiento[1]
            iTrad=cambio_coordenada(len(tablero),i)
            j=movimiento[0]
            newI=movimiento[3]
            newITrad=cambio_coordenada(len(tablero),newI)
            newJ=movimiento[2]
            ficha=tablero[iTrad][j]
            #Si la ficha llega al final del tablero se convierte en dama
            if(newI==7 or newI==0):
                if(ficha==1 or ficha==2):
                    ficha=ficha+2
            tablero[iTrad][j]=0
            tablero[newITrad][newJ]=ficha
            return self
        else:
            posicionesMovimiento=movimiento[0]
            capturas=movimiento[1]
            i=posicionesMovimiento[1]
            iTrad=cambio_coordenada(len(tablero),i)
            j=posicionesMovimiento[0]
            newI=posicionesMovimiento[3]
            newITrad=cambio_coordenada(len(tablero),newI)
            newJ=posicionesMovimiento[2]
            ficha=tablero[iTrad][j]
            #Si la ficha llega al final del tablero se convierte en dama
            if(newI==7 or newI==0):
                if(ficha==1 or ficha==2):
                    ficha=ficha+2
            tablero[iTrad][j]=0
            tablero[newITrad][newJ]=ficha
            for captura in capturas:
                i=captura[1]
                iTrad=cambio_coordenada(len(tablero),i)
                j=captura[0]
                tablero[iTrad][j]=0
            return self

    #Comprueba si el jugador tiene alguna ficha en el tablero
    def jugador_tiene_fichas(self,jugador):
        tablero = self.tablero
        res = False
        dama=jugador+2
        for fila in tablero:
            if(jugador in fila or dama in fila):
                res = True
                break
        return res

    def gana_jugador(self,jugador):
        numeroMovimientos = len(self.obtiene_movimientos())
        if(jugador==2):
            return self.ganan_blancas(numeroMovimientos)
        else:
            return self.ganan_negras(numeroMovimientos)

    def ganan_negras(self,numeroMovimientos):
        jugador = self.jugadorActual
        resultado = False
        if(numeroMovimientos==0 and jugador==2):
            resultado = True
        elif(self.jugador_tiene_fichas(2)==False):
            resultado = True
        return resultado

    def ganan_blancas(self,numeroMovimientos):
        jugador = self.jugadorActual
        resultado = False
        if(numeroMovimientos==0 and jugador==1):
            resultado = True
        elif(self.jugador_tiene_fichas(1)==False):
            resultado = True
        return resultado

    def es_estado_final(self):
        numeroMovimientos = len(self.obtiene_movimientos())
        numeroTurnos=self.turnos
        if(numeroTurnos==0):
            return True
        else:
            blancas=self.ganan_blancas(numeroMovimientos)
            negras=self.ganan_negras(numeroMovimientos)
            return blancas or negras

    def imprime_tablero(self):
        tablero = self.tablero
        numFilas = len(tablero)
        for i in range(numFilas):
            print("\n",cambio_coordenada(numFilas,i),end="   ")
            for j in range(len(tablero[i])):
                if(tablero[i][j]==1):
                    print("n",end=" ")
                elif(tablero[i][j]==2):
                    print("b",end=" ")
                elif(tablero[i][j]==3):
                    print("N",end=" ")
                elif(tablero[i][j]==4):
                    print("B",end=" ")
                else:
                    print("-",end=" ")
        print("\n")
        for i in range(numFilas):
            if (i==0):
                print("     ",end="")
            print(i,end=" ")
        print("\n")

    def imprime_estado(self):
        turnos = self.turnos
        jugador = self.jugadorActual
        self.imprime_tablero()
        print("\nTurnos restantes: ",turnos)
        if(jugador==1):
            print("\nTurno de las negras")
        else:
            print("\nTurno de las blancas")

    #Devuelve el jugador ganador o 0 si hay empate
    def ganador(self):
        if(self.gana_jugador(2)):
            return 2
        elif(self.gana_jugador(1)):
            return 1
        return 0

    def imprime_final(self):
        print("\nFin del juego\n")
        numeroMovimientos = len(self.obtiene_movimientos())
        #Recorremos el tablero e imprimimos en consola el valor de cada casilla siendo 
        self.imprime_tablero()
        #Se comprueba si el estado es final y se imprime el resultado
        if(self.ganan_blancas(numeroMovimientos)):
                print("\nGanan blancas\n")
                return 2
        elif(self.ganan_negras(numeroMovimientos)):
                print("\nGanan negras\n")
                return 1
        else:
            print("\nEmpate\n")
            return 0
    
    def turno_jugador(self):
        print(Fore.RED+"\nTurno Jugador "+str(self.jugadorActual))
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
        print(Fore.BLUE+"\nTurno MCTS "+str(self.jugadorActual))
        self.imprime_tablero()
        mov = mcts.ejecuta(self)
        if(mov!=None):
            return self.aplica_movimiento(mov)
        else:
            return self
    
    def turno_minimax(self,minimax):
        print(Fore.GREEN+"\nTurno Minimax "+str(self.jugadorActual))
        self.imprime_tablero()
        mov = minimax.ejecuta(self)
        if(mov!=None):
            return self.aplica_movimiento(mov)
        else:
            return self
    
    def turno_aleatorio(self):
        print(Fore.RED+"\nTurno Aleatorio "+str(self.jugadorActual))
        self.imprime_tablero()
        movimientos = self.obtiene_movimientos()
        mov = random.choice(movimientos)
        return self.aplica_movimiento(mov)

def imprime_movimientos(movimientos):
    i=0
    for movimiento in movimientos:
        if(len(movimiento)==4):
            print(i+1,"º movimiento:",movimiento)
        elif(len(movimiento)==2):
            print(i+1,"º movimiento:",movimiento[0],"con captura de ",movimiento[1])
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
        algoritmo = pyplAI.Minimax(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador,Damas.heuristica, Damas.jugadores, depth, True)
    else:
        tiempoEjecucion = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion<=0):
            tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo = pyplAI.MCTS(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador, Damas.jugadores, tiempoEjecucion, True)
    
    turnos = int(input("Introduce el número de turnos: \n"))
    while(turnos<=0):
        turnos = int(input("Introduce un número de turnos mayor que 0: \n"))

    posicionJugador = int(input("¿Qué ficha quieres usar? (1. Negras o 2. Blancas) \n"))
    while(posicionJugador<1 or posicionJugador>2):
        posicionJugador = int(input("Introduce 1 si quieres jugar negras o 2 si quieres jugar blancas: \n"))
    
    s = Damas(turnos)
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
    turnos = int(input("Introduce el número de turnos: \n"))
    while(turnos<=0):
        turnos = int(input("Introduce un número de turnos mayor que 0: \n"))

    s = Damas(turnos)
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
        algoritmo1 = pyplAI.Minimax(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador,Damas.heuristica, Damas.jugadores, depth1, True)
    else:
        tiempoEjecucion1 = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion1<=0):
            tiempoEjecucion1 = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo1 = pyplAI.MCTS(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador, Damas.jugadores, tiempoEjecucion1, True)
    
    algoritmo2 = int(input("¿Qué algoritmo quieres usar como segundo jugador? \n 1. Minimax \n 2. MCTS \n"))
    while(algoritmo2<1 or algoritmo2>2):
        algoritmo2 = int(input("Introduce un algoritmo válido: \n"))
    
    if(algoritmo2==1):
        depth2 = int(input("Introduce la profundidad del Minimax: \n"))
        while(depth2<=0):
            depth2 = int(input("Introduce una profundidad mayor que 0: \n"))
        algoritmo2 = pyplAI.Minimax(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador,Damas.heuristica, Damas.jugadores, depth2, True)
    else:
        tiempoEjecucion2 = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion2<=0):
            tiempoEjecucion2 = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo2 = pyplAI.MCTS(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador, Damas.jugadores, tiempoEjecucion2, True)
    
    turnos = int(input("Introduce el número de turnos: \n"))
    while(turnos<=0):
        turnos = int(input("Introduce un número de turnos mayor que 0: \n"))

    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        s = Damas(turnos)
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
        resultados.append(s.ganador())
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
        algoritmo = pyplAI.Minimax(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador,Damas.heuristica, Damas.jugadores, depth, True)
        tiempos = []
    else:
        tiempoEjecucion = float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
        while(tiempoEjecucion<=0):
            tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
        algoritmo = pyplAI.MCTS(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador, Damas.jugadores, tiempoEjecucion, True)
    
    turnos = int(input("Introduce el número de turnos: \n"))
    while(turnos<=0):
        turnos = int(input("Introduce un número de turnos mayor que 0: \n"))

    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        s = Damas(turnos)
        while(s.es_estado_final()==False):
            jugador = s.jugadorActual
            if(jugador==1):
                if(algoritmo.__class__.__name__=="MCTS"):
                    s = s.turno_mcts(algoritmo)
                else:
                    t0 = time.time()
                    s=s.turno_minimax(algoritmo)
                    t1 = time.time()
                    tiempos.append(t1-t0)
            else:
                s = s.turno_aleatorio()
        res=s.imprime_final()
        resultados.append(res)
        i+=1
    if(algoritmo.__class__.__name__=="MCTS"):
        print("\nPartidas Ganadas por el MCTS: ",resultados.count(1))
    else:
        print("\nPartidas Ganadas por el Minimax: ",resultados.count(1))
        print("Tiempo medio de ejecución del Minimax: ",sum(tiempos)/len(tiempos))
    print("Partidas Ganadas por el jugador aleatorio: ",resultados.count(2))
    print("Empates: ",resultados.count(0))
    
def main():
    print("\nBienvenido al juego de las Damas\n")
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