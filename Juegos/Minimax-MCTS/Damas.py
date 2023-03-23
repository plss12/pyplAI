from copy import deepcopy
import random
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
        self.tablero = ([0,1,0,1,0,1,0,1],
                        [1,0,1,0,1,0,1,0],
                        [0,1,0,1,0,1,0,1],
                        [0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0],
                        [2,0,2,0,2,0,2,0],
                        [0,2,0,2,0,2,0,2],
                        [2,0,2,0,2,0,2,0])
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

    #Funcion que comprueba si una ficha puede capturar algún rival y devuelve estos movimientos
    def comprobar_captura(self,i,j,lista,iInicial,jInicial,listaCapturas=[]):
        tablero=self.tablero
        jugador=self.jugadorActual
        if(jugador==1):
            peonRival=2
            reyRival=4
        else:
            peonRival=1
            reyRival=3
        der = j+1
        izq = j-1
        newI=cambio_coordenada(len(tablero),i)
        if(jugador==1):
            arr=i+1
        else:
            arr=i-1
        if(der<=6 and (arr<=6 and arr>=1) and (tablero[arr][der]==peonRival or tablero[arr][der]==reyRival)):
            if(jugador==1):
                arr2=arr+1
            else:
                arr2=arr-1
            if(tablero[arr2][der+1]==0):
                newArr=cambio_coordenada(len(tablero),arr)
                newListaCapturasDer=listaCapturas[:]
                newListaCapturasDer.append((der,newArr))
                self.comprobar_captura(arr2,der+1,lista,iInicial,jInicial,newListaCapturasDer)
        if(izq>=1 and (arr<=6 and arr>=1) and (tablero[arr][izq]==peonRival or tablero[arr][izq]==reyRival)):
            if(jugador==1):
                arr2=arr+1
            else:
                arr2=arr-1
            if(tablero[arr2][izq-1]==0):
                newArr=cambio_coordenada(len(tablero),arr)
                newListaCapturasIzq=listaCapturas[:]
                newListaCapturasIzq.append((izq,newArr))
                self.comprobar_captura(arr2,izq-1,lista,iInicial,jInicial,newListaCapturasIzq)
        if(len(listaCapturas)>0):
            lista.append((len(listaCapturas),(jInicial,iInicial,j,newI),listaCapturas))
        return lista

    #Funcion que comprueba si una dama puede capturar y devuelve estos movimientos
    def comprobar_captura_dama(self,i,j,lista,iInicial,jInicial,listaCapturas=[]):
        tablero=self.tablero
        jugador=self.jugadorActual
        if(jugador==1):
            peonRival=2
            reyRival=4
        else:
            peonRival=1
            reyRival=3
        der = j+1
        izq = j-1
        newI=cambio_coordenada(len(tablero),i)
        arr=i+1
        abj=i-1
        while(der<=6 and arr<=6):
            if(tablero[arr][der]==peonRival or tablero[arr][der]==reyRival):
                if(tablero[arr+1][der+1]==0):
                    newArr=cambio_coordenada(len(tablero),arr)
                    newListaCapturasDer=listaCapturas[:]
                    newListaCapturasDer.append((der,newArr))
                    newEstado=deepcopy(self)
                    newEstado.tablero[arr][der]=0
                    newEstado.tablero[i][j]=0
                    newEstado.tablero[arr+1][der+1]=jugador
                    arr2=arr+1
                    der2=der+1
                    while(der2<=7 and arr2<=7):
                        if(tablero[arr2][der2]==0):
                            newEstado.comprobar_captura_dama(arr2,der2,lista,iInicial,jInicial,newListaCapturasDer)
                            der2=der2+1
                            arr2=arr2+1
                        else:
                            break
                    break
                else:
                    break
            elif(tablero[arr][der]==0):
                arr+=1
                der+=1
            else:
                break
        der=j+1
        abj=i-1
        while(der<=6 and abj>=1):
            if(tablero[abj][der]==peonRival or tablero[abj][der]==reyRival):
                if(tablero[abj-1][der+1]==0):
                    newArr=cambio_coordenada(len(tablero),abj)
                    newListaCapturasDer=listaCapturas[:]
                    newListaCapturasDer.append((der,newArr))
                    newEstado=deepcopy(self)
                    newEstado.tablero[abj][der]=0
                    newEstado.tablero[i][j]=0
                    newEstado.tablero[abj-1][der+1]=jugador
                    der2=der+1
                    abj2=abj-1
                    while(der2<=7 and abj2>=0):
                        if(tablero[abj2][der2]==0):
                            newEstado.comprobar_captura_dama(abj2,der2,lista,iInicial,jInicial,newListaCapturasDer)
                            der2=der2+1
                            abj2=abj2-1
                        else:
                            break
                    break
                else:
                    break
            elif(tablero[abj][der]==0):
                der=der+1
                abj=abj-1
            else:
                break
        izq=j-1
        arr=i+1
        while(izq>=1 and arr<=6):
            if(tablero[arr][izq]==peonRival or tablero[arr][izq]==reyRival):
                if(tablero[arr+1][izq-1]==0):
                    newArr=cambio_coordenada(len(tablero),arr)
                    newListaCapturasIzq=listaCapturas[:]
                    newListaCapturasIzq.append((izq,newArr))
                    newEstado=deepcopy(self)
                    newEstado.tablero[arr][izq]=0
                    newEstado.tablero[i][j]=0
                    newEstado.tablero[arr+1][izq-1]=jugador
                    arr2=arr+1
                    izq2=izq-1
                    while(izq2>=0 and arr2<=7):
                        if(tablero[arr2][izq2]==0):
                            newEstado.comprobar_captura_dama(arr2,izq2,lista,iInicial,jInicial,newListaCapturasIzq)
                            izq2=izq2-1
                            arr2=arr2+1
                        else:
                            break
                    break
                else:
                    break
            elif(tablero[arr][izq]==0):
                izq=izq-1
                arr=arr+1
            else:
                break
        izq=j-1
        abj=i-1
        while(izq>=1 and abj>=1):
            if(tablero[abj][izq]==peonRival or tablero[abj][izq]==reyRival):
                if(tablero[abj-1][izq-1]==0):
                    newArr=cambio_coordenada(len(tablero),abj)
                    newListaCapturasIzq=listaCapturas[:]
                    newListaCapturasIzq.append((izq,newArr))
                    newEstado=deepcopy(self)
                    newEstado.tablero[abj][izq]=0
                    newEstado.tablero[i][j]=0
                    newEstado.tablero[abj-1][izq-1]=jugador
                    izq2=izq-1
                    abj2=abj-1
                    while(izq2>=0 and abj2>=0):
                        if(tablero[abj2][izq2]==0):
                            newEstado.comprobar_captura_dama(abj2,izq2,lista,iInicial,jInicial,newListaCapturasIzq)
                            izq2=izq2-1
                            abj2=abj2-1
                        else:
                            break
                    break
                else:
                    break
            elif(tablero[abj][izq]==0):
                izq=izq-1
                abj=abj-1
            else:
                break
        if(len(listaCapturas)>0):
            lista.append((len(listaCapturas),(jInicial,iInicial,j,newI),listaCapturas))
        return lista

    #Funcion que devuelve una lista con los movimientos que mas capturas tiene
    @staticmethod
    def limpiar_lista_capturas(lista):
        lista.sort(key=lambda l:l[0], reverse=True)
        movimientosMasCapturas=[[mov[1],mov[2]] for mov in lista if mov[0]==lista[0][0]]
        return movimientosMasCapturas

    def obtiene_movimientos(self):
        tablero = self.tablero
        jugador = self.jugadorActual
        jugadorRey = jugador+2
        movimientos = []
        numer_filas = len(tablero)
        movimiento=(0,0,0,0)
        captura=False
        numCapturasMax=0
        for i in range(numer_filas):
            if(jugador or jugadorRey in tablero[i]):
                for j in range(len(tablero[i])):
                    if(tablero[i][j]==jugador):
                        #Comprobamos si puede comer, si es asi esta obligado a hacer el movimiento con mas capturas
                        movimientosCaptura=self.comprobar_captura(i,j,[],cambio_coordenada(numer_filas,i),j)
                        if(movimientosCaptura):
                            movimientosCaptura=self.limpiar_lista_capturas(movimientosCaptura)
                            numCapturas=len(movimientosCaptura[0][1])
                            #Si hay captura se olvidan los anteriores movimientos
                            if(captura==False):
                                movimientos=[]
                                captura=True
                            #Si la captura es mayor que las anteriores se olvidan los anteriores movimientos
                            if(numCapturas>numCapturasMax):
                                movimientos=[]
                                movimientos=movimientosCaptura
                                numCapturasMax=numCapturas
                            #Si la captura es igual que las anteriores se añaden los nuevos movimientos
                            elif(numCapturas==numCapturasMax):
                                movimientos.extend(movimientosCaptura)
                                numCapturasMax=numCapturas
                        #Si no puede comer y no hay capturas anteriores se añaden los movimientos normales
                        elif(captura==False): 
                            newI=cambio_coordenada(numer_filas,i)
                            izq=j-1
                            der=j+1
                            if(jugador==1):
                                arr=i+1
                            else:
                                arr=i-1
                            newArr=cambio_coordenada(numer_filas,arr)
                            if(izq>=0 and (arr<=7 and arr>=0)):
                                if(tablero[arr][izq]==0):
                                    movimiento=(j,newI,izq,newArr)
                                    movimientos.append(movimiento)                  
                            if(der<=7 and (arr<=7 and arr>=0)):
                                if(tablero[arr][der]==0):
                                    movimiento=(j,newI,der,newArr)
                                    movimientos.append(movimiento)
                    elif(tablero[i][j]==jugadorRey):
                        movimientosCapturaDama=self.comprobar_captura_dama(i,j,[],cambio_coordenada(numer_filas,i),j)
                        if(movimientosCapturaDama):
                            movimientosCapturaDama=self.limpiar_lista_capturas(movimientosCapturaDama)
                            numCapturas=len(movimientosCapturaDama[0][1])
                            #Si hay captura se olvidan los anteriores movimientos
                            if(captura==False):
                                movimientos=[]
                                captura=True
                            #Si la captura es mayor que las anteriores se olvidan los anteriores movimientos
                            if(numCapturas>numCapturasMax):
                                movimientos=[]
                                movimientos=movimientosCapturaDama
                                numCapturasMax=numCapturas
                            #Si la captura es igual que las anteriores se añaden los nuevos movimientos
                            elif(numCapturas==numCapturasMax):
                                movimientos.extend(movimientosCapturaDama)
                                numCapturasMax=numCapturas
                        #Si no puede comer y no hay capturas anteriores se añaden los movimientos normales
                        elif(captura==False):   
                            izq=j-1
                            arr=i-1
                            newI=cambio_coordenada(numer_filas,i)
                            newArr=cambio_coordenada(numer_filas,arr)
                            while(izq>=0 and arr>=0):
                                newArr=cambio_coordenada(numer_filas,arr)
                                if(tablero[arr][izq]==0):
                                    movimiento=(j,newI,izq,newArr)
                                    movimientos.append(movimiento)
                                    izq=izq-1
                                    arr=arr-1
                                else:
                                    break
                            der=j+1 
                            arr=i-1
                            newI=cambio_coordenada(numer_filas,i)
                            newArr=cambio_coordenada(numer_filas,arr)
                            while(der<=7 and arr>=0):
                                newArr=cambio_coordenada(numer_filas,arr)
                                if(tablero[arr][der]==0):
                                    movimiento=(j,newI,der,newArr)
                                    movimientos.append(movimiento)
                                    der=der+1
                                    arr=arr-1
                                else:
                                    break
                            izq=j-1
                            abj=i+1
                            newI=cambio_coordenada(numer_filas,i)
                            newAbj=cambio_coordenada(numer_filas,abj)   
                            while(izq>=0 and abj<=7):
                                newAbj=cambio_coordenada(numer_filas,abj)
                                if(tablero[abj][izq]==0):
                                    movimiento=(j,newI,izq,newAbj)
                                    movimientos.append(movimiento)
                                    izq=izq-1
                                    abj=abj+1
                                else:
                                    break
                            der=j+1 
                            abj=i+1
                            newI=cambio_coordenada(numer_filas,i)
                            newAbj=cambio_coordenada(numer_filas,abj)   
                            while(der<=7 and abj<=7):
                                newAbj=cambio_coordenada(numer_filas,abj)
                                if(tablero[abj][der]==0):
                                    movimiento=(j,newI,der,newAbj)
                                    movimientos.append(movimiento)
                                    der=der+1
                                    abj=abj+1
                                else:
                                    break
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

    def imprime_final(self):
        print("\nFin del juego\n")
        numeroMovimientos = self.obtiene_movimientos()
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
        algoritmo = pyplAI.MinMax(Damas.aplica_movimiento,Damas.obtiene_movimientos,Damas.es_estado_final,Damas.gana_jugador,Damas.heuristica, Damas.jugadores, depth, True)
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