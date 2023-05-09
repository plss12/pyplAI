#Stratego 8x10: 30 fichas por jugador
#-1 -> Agua
# 0 -> Casilla vacía
# 1 -> Espía (x1)
# 2 -> Explorador (x5)
# 3 -> Minador (x4)
# 4 -> Sargento (x2)
# 5 -> Teniente (x2)
# 6 -> Capitán (x3)
# 7 -> Comandante (x3)
# 8 -> Coronel (x2)
# 9 -> General (x1)
# 10 -> Mariscal (x1)
# 11 -> Bandera (x1)
# 12 -> Bomba (x5)

import random
from copy import deepcopy
import time
from colorama import Fore, init
import pyplAI
from pathlib import Path

init(autoreset=True)

class Stratego:
    jugadores = [1,2]

    def __init__(self,turnos,posicionFichas1=None,posicionFichas2=None):
        self.tablero=[]
        self.jugadorActual=1
        self.turnos=turnos
        self.estado_inicial(posicionFichas1,posicionFichas2)
    
    def estado_inicial(self,posicionFichas1,posicionFichas2):
        if(posicionFichas1):
            posicionFichasConvrt=deepcopy(posicionFichas1[::-1])
            for fila in posicionFichasConvrt:
                fila.reverse()
            filasJugador1 = Stratego.colocacion(posicionFichasConvrt,1)
        else:
            filasJugador1 = Stratego.colocacion_aleatoria(1)
        if(posicionFichas2):
            filasJugador2 = Stratego.colocacion(posicionFichas2,2)
        else:
            filasJugador2 = Stratego.colocacion_aleatoria(2)
        filasCentrales = Stratego.filas_centrales()
        tablero = (filasJugador1[0],
                filasJugador1[1],
                filasJugador1[2],
                filasCentrales[0],
                filasCentrales[1],
                filasJugador2[0],
                filasJugador2[1],
                filasJugador2[2])
        self.tablero=tablero
        return self

    def filas_centrales():
        filas=[[],[]]
        for i in range(3,5):
            for j in range(10):
                if(j!=2 and j!=3 and j!=6 and j!=7):
                    casillaVacia = Ficha(0,-1,i,j)
                    casillaVacia.visible=True
                    filas[i-3].append(casillaVacia)
                else:
                    fichaAgua = Ficha(-1,-1,i,j)
                    fichaAgua.visible=True
                    filas[i-3].append(fichaAgua)
        return filas

    @staticmethod
    def creacion_fichas(jugador):
        res = []
        espia = Ficha(1,jugador,0,0)
        res.append(espia)
        for _ in range(5):
            explorador = Ficha(2,jugador,0,0)
            res.append(explorador)
        for _ in range(4):
            minador = Ficha(3,jugador,0,0)
            res.append(minador)
        for _ in range(2):
            sargento = Ficha(4,jugador,0,0)
            res.append(sargento)
        for _ in range(2):
            teniente = Ficha(5,jugador,0,0)
            res.append(teniente)
        for _ in range(3):
            capitan = Ficha(6,jugador,0,0)
            res.append(capitan)
        for _ in range(3):
            comandante = Ficha(7,jugador,0,0)
            res.append(comandante)
        for _ in range(2):
            coronel = Ficha(8,jugador,0,0)
            res.append(coronel)
        for _ in range(1):
            general = Ficha(9,jugador,0,0)
            res.append(general)
        for _ in range(1):
            mariscal = Ficha(10,jugador,0,0)
            res.append(mariscal)
        for _ in range(1):
            bandera = Ficha(11,jugador,0,0)
            res.append(bandera)
        for _ in range(5):
            bomba = Ficha(12,jugador,0,0)
            res.append(bomba)
        return res

    @staticmethod
    def colocacion(posicionFichas,jugador):
        res = [],[],[]
        for i in range(3):
            for j in range(10):
                valor = posicionFichas[i][j]
                if(jugador==2):
                    ficha = Ficha(valor,jugador,i+5,j)
                else:
                    ficha = Ficha(valor,jugador,i,j)
                res[i].append(ficha)
        return res

    @staticmethod
    def colocacion_aleatoria(jugador):
        fichasJugador = Stratego.creacion_fichas(jugador)
        random.shuffle(fichasJugador)
        res = [],[],[]
        for i in range(3):
            for j in range(10):
                ficha = random.choice(fichasJugador)
                fichasJugador.remove(ficha)
                if(jugador==1):
                    ficha.cambiar_posicion(i,j)
                else:
                    ficha.cambiar_posicion(i+5,j)
                res[i].append(ficha)
        return res

    def gana_jugador(self, jugador):
        numMovs = len(self.obtiene_movimientos())
        tablero = self.tablero
        jugadorTurno = self.jugadorActual
        jugadorAnterior = 3-jugadorTurno
        if(numMovs==0):
            if(jugador==jugadorAnterior):
                return True
            elif(jugador!=jugadorAnterior):
                return False
        else:
            jugadorRival = 3-jugador
            for fila in tablero:
                for ficha in fila:
                    if(ficha.valor==11 and ficha.jugador==jugadorRival):
                        return False
            return True

    def es_estado_final(self):
        if(self.turnos<=0):
            return True
        else:
            jugador1=self.gana_jugador(1)
            jugador2=self.gana_jugador(2)
            return jugador1 or jugador2
    
    @staticmethod
    def obtiene_movimientos_ficha(tablero,ficha):
        fila = ficha.fila
        columna = ficha.columna
        jugador = ficha.jugador
        jugadorRival = 3-jugador
        movimientos = []
        if(fila+1<len(tablero)):
            if(tablero[fila+1][columna].valor==0):
                movimientos.append((fila,columna,fila+1,columna))
            elif(tablero[fila+1][columna].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila+1,columna]))
        if(fila-1>=0):
            if(tablero[fila-1][columna].valor==0):
                movimientos.append((fila,columna,fila-1,columna))
            elif(tablero[fila-1][columna].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila-1,columna]))
        if(columna+1<len(tablero[0])):
            if(tablero[fila][columna+1].valor==0):
                movimientos.append((fila,columna,fila,columna+1))
            elif(tablero[fila][columna+1].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila,columna+1]))
        if(columna-1>=0):
            if(tablero[fila][columna-1].valor==0):
                movimientos.append((fila,columna,fila,columna-1))
            elif(tablero[fila][columna-1].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila,columna-1]))
        return movimientos

    #El explorador puede moverse en línea recta (horizontal o vertical) por tantas casillas como libres tenga esta línea
    #además, puede atacar en el mismo turno en el que se mueve, por lo que si al final de la línea hay una ficha enemiga,
    #el explorador puede atacarla
    @staticmethod
    def obtiene_movimientos_explorador(tablero,ficha):
        fila=ficha.fila
        columna=ficha.columna
        jugador=ficha.jugador
        jugadorRival=3-jugador
        movimientos=[]
        fila1=fila
        while(fila1+1<len(tablero)):
            if(tablero[fila1+1][columna].valor==0):
                movimientos.append((fila,columna,fila1+1,columna))
                fila1+=1
            elif(tablero[fila1+1][columna].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila1+1,columna]))
                break
            else:
                break
        fila1=fila
        while(fila1-1>=0):
            if(tablero[fila1-1][columna].valor==0):
                movimientos.append((fila,columna,fila1-1,columna))
                fila1-=1
            elif(tablero[fila1-1][columna].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila1-1,columna]))
                break
            else:
                break
        columna1=columna
        while(columna1+1<len(tablero[0])):
            if(tablero[fila][columna1+1].valor==0):
                movimientos.append((fila,columna,fila,columna1+1))
                columna1+=1
            elif(tablero[fila][columna1+1].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila,columna1+1]))
                break
            else:
                break
        columna1=columna
        while(columna1-1>=0):
            if(tablero[fila][columna1-1].valor==0):
                movimientos.append((fila,columna,fila,columna1-1))
                columna1-=1
            elif(tablero[fila][columna1-1].jugador==jugadorRival):
                movimientos.append(([fila,columna],[fila,columna1-1]))
                break
            else:
                break
        return movimientos

    def obtiene_movimientos(self):
        jugador = self.jugadorActual
        tablero = self.tablero
        movimientos = []
        for fila in tablero:
            for ficha in fila:
                valor = ficha.valor
                if(ficha.jugador==jugador and valor!=11 and valor!=12):
                    #Si la ficha es un explorador, sus movimientos son diferentes
                    if(valor!=2):
                        movimientos.extend(Stratego.obtiene_movimientos_ficha(tablero,ficha))
                    else:
                        movimientos.extend(Stratego.obtiene_movimientos_explorador(tablero,ficha))
        return random.sample(movimientos, len(movimientos))

    @staticmethod
    def ataque(fichaAtacante, fichaDefensor):
        valorAtacante = abs(fichaAtacante.valor)
        valorDefensor = abs(fichaDefensor.valor)
        #Si el atacante y el defensor tienen el mismo poder mueren ambos
        if(valorAtacante==valorDefensor):
            return 0
        #Si el atacante es el Espía y el defensor es el Mariscal, el Espía gana aun teniendo menos poder
        elif(valorAtacante==1 and valorDefensor==10):
            return fichaAtacante
        #Si el defensor es la Bomba, siempre pierde el atacante excepto que sea un Minador
        elif(valorDefensor==12):
            if(valorAtacante==3):
                return fichaAtacante
            else:
                return fichaDefensor
        #Si el defensor es la Bandera, siempre gana el atacante
        elif(valorDefensor==11):
            return fichaAtacante
        #Si ninguna de estas excepciones se cumple, gana la ficha con mayor poder
        else:
            if(valorAtacante>valorDefensor):
                return fichaAtacante
            else:
                return fichaDefensor

    #Función que devuelve la diferencia de casillas entre dos fichas
    @staticmethod
    def diferencia_casillas(fila,columna,newFila,newColumna):
        if(fila==newFila):
            return abs(columna-newColumna)
        elif(columna==newColumna):
            return abs(fila-newFila)

    def aplica_movimiento(self, movimiento):
        tablero = self.tablero
        jugadorRival = 3-self.jugadorActual
        self.jugadorActual = jugadorRival
        self.turnos = self.turnos-1
        if(len(movimiento)==4):
            fila=movimiento[0]
            columna=movimiento[1]
            newFila=movimiento[2]
            newColumna=movimiento[3]
            ficha = tablero[fila][columna]
            #Si la ficha es un explorador se observa si el movimiento es de más de una casilla
            #si lo es, se pone como visible, ya que es la única ficha capaz de mover más de una casilla
            if(ficha.valor==2 and ficha.visible==False):
                if(Stratego.diferencia_casillas(fila,columna,newFila,newColumna)>1):
                    ficha.visible=True
            #También se comprueba si la ficha ha sido utilizada anteriormente, para cambiar su bool en caso
            #de que no hubiese sido utilizada
            if(ficha.utilizada==False):
                ficha.utilizada=True
            espacio = tablero[newFila][newColumna]
            espacio.cambiar_posicion(fila,columna)
            ficha.cambiar_posicion(newFila,newColumna)
            tablero[fila][columna]=espacio
            tablero[newFila][newColumna]=ficha
        else:
            iAtaque=movimiento[0][0]
            jAtaque=movimiento[0][1]
            iDefensa=movimiento[1][0]
            jDefensa=movimiento[1][1]
            fichaAtacante = tablero[iAtaque][jAtaque]
            fichaDefensiva = tablero[iDefensa][jDefensa]
            ganadorAtaque = Stratego.ataque(fichaAtacante,fichaDefensiva)
            #Si la ficha es un explorador se observa si el ataque se ha producido a distancia
            #si es así, y este explorador gana la batalla, se pone como visible ya que es la única ficha
            #capaz de atacar a distancia
            if(fichaAtacante.valor==2 and fichaAtacante.visible==False and ganadorAtaque==fichaAtacante):
                if(Stratego.diferencia_casillas(iAtaque,jAtaque,iDefensa,jDefensa)>1):
                    fichaAtacante.visible=True
            if(ganadorAtaque==fichaAtacante):
                espacio=Ficha(0,-1,iAtaque,jAtaque)
                tablero[iAtaque][jAtaque]=espacio
                tablero[iDefensa][jDefensa]=fichaAtacante
                fichaAtacante.cambiar_posicion(iDefensa,jDefensa)
                fichaAtacante.visible=True
                #También se comprueba si la ficha ha sido utilizada anteriormente, para cambiar su bool en caso
                if(fichaAtacante.utilizada==False):
                    fichaAtacante.utilizada=True
            elif(ganadorAtaque==fichaDefensiva):
                espacio=Ficha(0,-1,iAtaque,jAtaque)
                tablero[iAtaque][jAtaque]=espacio
                fichaDefensiva.visible=True
            elif(ganadorAtaque==0):
                espacio1=Ficha(0,-1,iAtaque,jAtaque)
                espacio2=Ficha(0,-1,iDefensa,jDefensa)
                tablero[iAtaque][jAtaque]=espacio1
                tablero[iDefensa][jDefensa]=espacio2
        return self
    
    def imprime_tablero(self,jugadoresVisibles):
        tablero=self.tablero
        i=len(tablero)-1
        for fila in tablero:
            print("  +--+--+--+--+--+--+--+--+--+--+")
            print(i,end=" ")
            i-=1
            for ficha in fila:
                visible=ficha.visible
                jugador=ficha.jugador
                ficha=ficha.valor
                print("|",end="")
                if(visible==True or jugador in jugadoresVisibles):
                #if(visible==True or jugador==1):
                    if(ficha==-1):
                        print(Fore.BLUE+"X",end=" ")
                    elif(ficha==0):
                        print(" ",end=" ")
                    elif(ficha==11):
                        if(jugador==1):
                            print(Fore.GREEN+"B",end=" ")
                        else:
                            print(Fore.RED+"B",end=" ")
                    elif(ficha<10):
                        if(jugador==1):
                            print(Fore.GREEN+str(ficha),end=" ")
                        else:
                            print(Fore.RED+str(ficha),end=" ")
                    else:
                        if(jugador==1):
                            print(Fore.GREEN+str(ficha),end="")
                        else:
                            print(Fore.RED+str(ficha),end="")
                else:
                    if(jugador==1):
                        print(Fore.GREEN+"?",end=" ")
                    else:
                        print(Fore.RED+"?",end=" ")
            print("|")
        print("  +--+--+--+--+--+--+--+--+--+--+")
        print("    0  1  2  3  4  5  6  7  8  9 ")

    def imprime_estado(self):
        jugador=self.jugadorActual
        numMovs=len(self.obtiene_movimientos())
        self.imprime_tablero([self.jugadorActual])
        print("Turnos restantes: ",self.turnos)
        print("Turno del Jugador ",jugador)
        print("Movimientos posibles: ",numMovs)
    
    def turno_prueba(self):
        self.imprime_tablero([self.jugadorActual])
        movs=self.obtiene_movimientos()
        mov = random.choice(movs)
        return self.aplica_movimiento(mov)
    
    def turno_jugador(self):
        movs=self.obtiene_movimientos()
        self.imprime_estado()
        self.imprime_movimientos(movs)
        print("Introduce el movimiento que quieres realizar: ")
        mov = int(input())
        while(mov<=0 or mov>len(movs)):
            print("Movimiento invalido, introduce un movimiento: ")
            mov=int(input())
        movimientoSeleccionado=movs[mov-1]
        if(len(movimientoSeleccionado)==2):
            ficha=self.tablero[movimientoSeleccionado[1][0]][movimientoSeleccionado[1][1]]
            if(ficha.valor!=11 or ficha.valor!=12):
                print("Has atacado a ",ficha.nombre," (",ficha.valor,")")
            else:
                print("Has atacado a una",ficha.nombre)
        return self.aplica_movimiento(movimientoSeleccionado)
    
    def turno_mcts(self,mcts):
        self.imprime_tablero([self.jugadorActual])
        mov=mcts.ejecuta(self)
        if(mov!=None):
            return self.aplica_movimiento(mov)
        else:
            return self

    def imprime_final(self):
        numero_movs=len(self.obtiene_movimientos())
        print("\n Tablero final:")
        self.imprime_tablero(Stratego.jugadores)
        if(self.gana_jugador(1)):
            if(numero_movs==0):
                print("Gana el jugador 1 por falta de movimientos del rival")
            else:
                print("Gana el jugador 1 por capturar la bandera")
            return 1
        elif(self.gana_jugador(2)):
            if(numero_movs==0):
                print("Gana el jugador 2 por falta de movimientos del rival")
            else:
                print("Gana el jugador 2 por capturar la bandera")
            return 2
        else:
            print("Empate")
            return 0

    def imprime_movimientos(self,movs):
        i=1
        tablero=self.tablero
        for mov in movs:
            if(len(mov)==4):
                ficha = tablero[mov[0]][mov[1]]
                fichaTradu=Ficha.traductor_ficha(ficha.valor)
                newI1=Ficha.cambio_coordenada(len(tablero),mov[0])
                newI2=Ficha.cambio_coordenada(len(tablero),mov[2])
                print(i,"º movimiento: Mover ",fichaTradu,"(",ficha.valor,") de [",mov[1],",",newI1,"] a [",mov[3],",",newI2,"]")
            elif(len(mov)==2):
                fichaAtaque=tablero[mov[0][0]][mov[0][1]]
                fichaAtaqueTradu=Ficha.traductor_ficha(fichaAtaque.valor)
                newI1=Ficha.cambio_coordenada(len(tablero),mov[0][0])
                newI2=Ficha.cambio_coordenada(len(tablero),mov[1][0])
                print(i,"º movimiento: Atacar con ",fichaAtaqueTradu,"(",fichaAtaque.valor,") en [",mov[0][1],",",newI1,"] a [",mov[1][1],",",newI2,"]")
            i+=1
    
    def determinization(self):
        jugador = self.jugadorActual
        fichasNoVisibles=[]
        #Obtenemos las fichas no visibles del jugador rival
        for fila in self.tablero:
            for ficha in fila:
                if(ficha.visible==False and ficha.jugador!=jugador):
                    fichasNoVisibles.append(ficha)
        #Ahora aleatoriamente hacemos una repartición de estas fichas por el tablero en las casillas en las que no sabemos que hay
        determinazion=deepcopy(self)
        copiaFichas=deepcopy(fichasNoVisibles)
        random.shuffle(copiaFichas)
        fichasRepartidas=[]
        #Primero determinamos las fichas que han sido utilizadas impidiendo que estas se determinen como bombas o bandera
        for fila in determinazion.tablero:
            for ficha in fila:
                if(ficha.visible==False and ficha.jugador!=jugador and ficha.utilizada==True):
                    fila = ficha.fila
                    columna = ficha.columna
                    fichaAleatoria=random.choice(copiaFichas)
                    while(fichaAleatoria.valor==11 or fichaAleatoria.valor==12):
                        fichaAleatoria=random.choice(copiaFichas)
                    fichaAleatoria.cambiar_posicion(fila,columna)
                    copiaFichas.remove(fichaAleatoria)
                    determinazion.tablero[fila][columna]=fichaAleatoria
                    fichasRepartidas.append(fichaAleatoria)
        #Ahora determinamos las fichas que no han sido utilizadas puediendo ser cualquier tipo de ficha
        for fila in determinazion.tablero:
            for ficha in fila:
                if(ficha not in fichasRepartidas):
                    if(ficha.visible==False and ficha.jugador!=jugador and ficha.utilizada==False):
                        fila = ficha.fila
                        columna = ficha.columna
                        fichaAleatoria=random.choice(copiaFichas)
                        fichaAleatoria.cambiar_posicion(fila,columna)
                        copiaFichas.remove(fichaAleatoria)
                        determinazion.tablero[fila][columna]=fichaAleatoria
        return determinazion


class Ficha:
    @staticmethod
    def traductor_ficha(ficha):
        if(ficha==-1):
            return "Agua"
        elif(ficha==0):
            return "Espacio"
        elif(ficha==1):
            return "Espía"
        elif(ficha==2):
            return "Explorador"
        elif(ficha==3):
            return "Minador"
        elif(ficha==4):
            return "Sargento"
        elif(ficha==5):
            return "Teniente"
        elif(ficha==6):
            return "Capitán"
        elif(ficha==7):
            return "Comandante"
        elif(ficha==8):
            return "Coronel"
        elif(ficha==9):
            return "General"
        elif(ficha==10):
            return "Mariscal"
        elif(ficha==11):
            return "Bandera"
        elif(ficha==12):
            return "Bomba"

    def __init__(self,valor,jugador,fila,columna):
        self.valor=valor
        self.nombre=Ficha.traductor_ficha(valor)
        #Este bool se utilizará para saber que fichas conoce el rival y cuales no
        if(valor==0 or valor==-1):
            self.visible=True
        else:
            self.visible=False
        #Este bool servirá para saber que fichas han sido movidas o usado en ataque y cuales no
        #ya que esto descartaría estas fichas como posibles bombas o la bandera ya que estas
        #no pueden moverse ni atacar
        self.utilizada=False
        self.jugador=jugador
        self.fila=fila
        self.columna=columna
    
    def __str__(self):
        if(self.visible and self.valor!=0 and self.valor!=-1):
            coord="("+str(self.fila)+","+str(self.columna)+")"
            return self.nombre, "("+str(self.valor)+") en ", coord
        elif(self.valor==0):
            return " "
        elif(self.valor==-1):
            return "X"
     
    def cambiar_posicion(self,i,j):
        self.fila=i
        self.columna=j
    
    @staticmethod
    def cambio_coordenada(len,i):
        newI=len-1-i
        return newI

def posicionFichasJugador():
    res = [],[],[]
    valoresFichas=[1,2,2,2,2,2,3,3,3,3,4,4,5,5,6,6,6,7,7,7,8,8,9,10,11,12,12,12,12,12]
    print("Introduzca las posiciones de las fichas que desea colocar empezando por arriba de izquierda a derecha")
    for i in range(3):
        for j in range(10):
            print("Para la fila",i+1,"en la casilla",j+1," introduce el valor de la ficha que desea colocar: ")
            print("Fichas disponibles: ",valoresFichas,"")
            valor = int(input())
            while(valor not in valoresFichas):
                print("No le quedan más fichas de ese tipo, introduzca otro valor: ")
                print("Fichas disponibles: ",valoresFichas,"")
                valor = int(input())
            valoresFichas.remove(valor)
            res[i].append(valor)
    return res

def posicionFichasAlgoritmoGenetico():
    genes = cargar_genes()
    mejorGen = random.choice(list(genes.keys()))
    mejorGen = genes[mejorGen]
    return mejorGen

class Cromosoma:
    def __init__(self,genes=None):
        if(genes==None):
            self.genes=[]
            self.generaCromosomaInicialAleatorio()
        else:
            self.genes = genes
        self.fitness = 1
        self.es_estado_final = Stratego.es_estado_final
        self.aplicar_movimiento = Stratego.aplica_movimiento
        self.obtener_movimientos = Stratego.obtiene_movimientos
        self.gana_jugador = Stratego.gana_jugador
    
    def generaCromosomaInicialAleatorio(self):
        valoresFichas=[1,2,2,2,2,2,3,3,3,3,4,4,5,5,6,6,6,7,7,7,8,8,9,10,11,12,12,12,12,12]
        for i in range(30):
            self.genes.append(random.choice(valoresFichas))
            valoresFichas.remove(self.genes[i])
        
    def simulate(self,d,movs):
        jugadores = Stratego.jugadores
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
        
    def evalua(self):
        res=0
        primerFila=self.genes[:10]
        segundaFila=self.genes[10:20]
        terceraFila=self.genes[20:30]
        posicionFichasGen=[primerFila,segundaFila,terceraFila]
        for _ in range(15):
            partida = Stratego(100,posicionFichasGen,None)
            movs=partida.obtiene_movimientos()
            recompensa=self.simulate(partida,movs)
            res+=recompensa[0]
        for _ in range(15):
            partida = Stratego(100,None,posicionFichasGen)
            movs=partida.obtiene_movimientos()
            recompensa=self.simulate(partida,movs)
            res+=recompensa[1]
        self.fitness = res
    
    #Mutacion por intercambio de genes
    def muta(self,probabilidadMutacion):
        if(random.random()<=probabilidadMutacion):
            punto1 = random.randint(0,len(self.genes)-1)
            punto2 = random.randint(0,len(self.genes)-1)
            self.genes[punto1],self.genes[punto2] = self.genes[punto2],self.genes[punto1]
    
    def fichaFalta(ficha,listaFichas):
        valoresFichas=[1,2,2,2,2,2,3,3,3,3,4,4,5,5,6,6,6,7,7,7,8,8,9,10,11,12,12,12,12,12]
        numeroFichas=valoresFichas.count(ficha)
        numeroFichasEnLista=listaFichas.count(ficha)
        if(numeroFichasEnLista<numeroFichas):
            return True
        else:
            return False

    #Cruce basado en orden con una pequeña modificacion para cumplir con las fichas
    def cruza(self,otroCromosoma):
        punto1 = random.randint(0,len(self.genes)-1)
        punto2 = random.randint(0,len(self.genes)-1)
        if(punto1>punto2):
            punto1,punto2=punto2,punto1
        l1 = [None]*len(self.genes)
        l2 = [None]*len(self.genes)
        for i in range(punto1,punto2+1):
            l1[i]=self.genes[i]
            l2[i]=otroCromosoma.genes[i]
        indices = [x for x in range(punto2+1,len(self.genes))]+[x for x in range (0,punto2+1)]
        c1=(punto2+1)%len(self.genes)
        c2=(punto2+1)%len(self.genes)
        for i in indices:
            if(Cromosoma.fichaFalta(otroCromosoma.genes[i],l1)):
                l1[c1]=otroCromosoma.genes[i]
                c1=(c1+1)%len(self.genes)
            if(Cromosoma.fichaFalta(self.genes[i],l2)):
                l2[c2]=self.genes[i]
                c2=(c2+1)%len(self.genes)
        cromosoma1 = Cromosoma(l1)
        cromosoma2 = Cromosoma(l2)
        return cromosoma1,cromosoma2

class Poblacion:
    def __init__(self,cromosomas=None):
        if(cromosomas==None):
            self.poblacion=[]
        else:
            self.poblacion=cromosomas
    
    def generaPoblacionEvaluada(self,numeroCromosomas):
        for _ in range(numeroCromosomas):
            cromo=Cromosoma()
            cromo.evalua()
            self.poblacion.append(cromo)

    def prepararPoblacion(self):
        self.poblacion.sort(key=lambda x: x.fitness,reverse=True)
        suma = 0
        for cromosoma in self.poblacion:
            suma+=cromosoma.fitness
            cromosoma.sumaParcial=suma
        self.sumaTotal=suma
    
    #Selección por ruleta
    def selecciona(self):
        num = random.random()*self.sumaTotal
        for cromosoma in self.poblacion:
            if(num<cromosoma.sumaParcial):
                return cromosoma
        return None
    
    def seleccionaVarios(self,numero):
        res = []
        for _ in range(numero):
            res.append(self.selecciona())
        return res

class AlgoritmoGenetico:
    def __init__(self,proporcionCruce,probabilidadMutacion,numeroPoblacion,numeroGeneraciones):
        self.proporcionCruce = proporcionCruce
        self.probabilidadMutacion = probabilidadMutacion
        self.numeroGeneraciones = numeroGeneraciones
        self.numeroPoblacion = numeroPoblacion
        self.mejorPoblacion = None
    
    def ejecuta(self):
        if(self.mejorPoblacion==None):
            poblacion = Poblacion()
            poblacion.generaPoblacionEvaluada(self.numeroPoblacion)
        else:
            poblacion = self.mejorPoblacion
        cromosomasPorCruzar = int(self.proporcionCruce*self.numeroPoblacion)
        if(cromosomasPorCruzar==0):
            cromosomasPorCruzar=2
        if(cromosomasPorCruzar%2!=0):
            cromosomasPorCruzar+=1
        cromosomasSinCruzar = self.numeroPoblacion-cromosomasPorCruzar
        for _ in range(self.numeroGeneraciones):
            poblacion.prepararPoblacion()
            p1=poblacion.seleccionaVarios(cromosomasPorCruzar)
            p2=poblacion.seleccionaVarios(cromosomasSinCruzar)
            random.shuffle(p1)
            for i in range(0,len(p1),2):
                hijos = p1[i].cruza(p1[i+1])
                p1[i]=hijos[0]
                p1[i+1]=hijos[1]
            p4=p1+p2
            for cromosoma in p4:
                cromosoma.muta(self.probabilidadMutacion)
                cromosoma.evalua()
            poblacion=Poblacion(p4)
            print("Generación: ",_+1)
            listaFitness = list(map(lambda x: x.fitness,poblacion.poblacion))
            listaFitness.sort(reverse=True)
            print("Mejor fitness: ",listaFitness[:5])
        return poblacion

    def obtieneMejor(self,poblacion):
        mejor = max(poblacion.poblacion,key=lambda x: x.fitness)
        fila1=mejor.genes[:10]
        fila2=mejor.genes[10:20]
        fila3=mejor.genes[20:30]
        print("Fila 1: ",fila1)
        print("Fila 2: ",fila2)
        print("Fila 3: ",fila3)
        self.mejorPoblacion = poblacion
        return mejor

def guardar_poblacion(poblacion):
    f = open("Stratego.txt","a")
    #Obtener los mejores 20 cromosomas
    poblacion.poblacion.sort(key=lambda x: x.fitness,reverse=True)
    mejoresCromo=poblacion.poblacion=poblacion.poblacion[:20]
    for cromosoma in mejoresCromo:
        genStr = str(cromosoma.genes)
        genLimpio = genStr[1:-1]
        gen = genLimpio+" ; "+str(cromosoma.fitness)+"\n"
        f.write(gen)
    f.close()

def cargar_genes():
    script_location = Path(__file__).absolute().parent
    file_location = script_location / "Stratego.txt"
    f = open(file_location,"r")
    genes = f.readlines()
    dicc = {}
    for gen in genes:
        gen = gen.split(" ; ")
        gen[1] = float(gen[1].replace("\n",""))
        filas = gen_a_filas(gen[0])
        dicc[gen[1]]=filas
    f.close()
    return dicc

def gen_a_filas(gen):
    gen = gen.split(",")
    res = []
    fila1=[]
    fila2=[]
    fila3=[]
    for i in range(0,10):
        fila1.append(int(gen[i]))
    for i in range(10,20):
        fila2.append(int(gen[i]))
    for i in range(20,30):
        fila3.append(int(gen[i]))
    res.append(fila1)
    res.append(fila2)
    res.append(fila3)
    return res

def algoritmoGenetico():
    numGeneraciones = int(input("Introduce el número de generaciones: "))
    while(numGeneraciones<1):
        numGeneraciones = int(input("Introduce un número de generaciones mayor que 1: "))
    numPoblacion = int(input("Introduce el número de individuos por generación: "))
    while(numPoblacion<1):
        numPoblacion = int(input("Introduce un número de individuos mayor que 1: "))

    probabilidadMutacion = 0.2
    proporcionCruce = 0.6
    t0 = time.time()
    algoritmo=AlgoritmoGenetico(proporcionCruce, probabilidadMutacion, numPoblacion, numGeneraciones)
    mejorPoblación=algoritmo.ejecuta()
    t1 = time.time()
    print("Tiempo de ejecución: ",t1-t0)
    guardar_poblacion(mejorPoblación)


def jugadorContraSOISMCTS():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    numeroJugadores = 2
    mcts = pyplAI.SOISMCTS(Stratego.aplica_movimiento,Stratego.obtiene_movimientos,Stratego.es_estado_final,Stratego.gana_jugador,Stratego.determinization,numeroJugadores,tiempoEjecucion, True)
    
    turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))
    while(turnos<=0):
        print("El número de turnos debe ser mayor que 0\n")
        turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))
    
    turnoJugador = int(input("¿Quién empieza la partida? (1: Jugador, 2: SOISMCTS): \n"))
    while(turnoJugador!=1 and turnoJugador!=2):
        turnoJugador = int(input("Elige una opción válida (1: Jugador, 2: SOISMCTS): \n"))

    print("¿Desea elegir la posición de las fichas o jugar con posiciones determinadas por el algoritmo genético?")
    print("1. Posiciones elegidas por el usuario")
    print("2. Posiciones determinadas por el algoritmo genético")
    posicion = int(input("Introduce una opción: \n"))
    while(posicion!=1 and posicion!=2):
        posicion = int(input("Introduce una opción válida: \n"))
    if(posicion==1):
        print("Introduce la posición de las fichas: \n")
        fichasJugador=posicionFichasJugador()
    else:
        fichasJugador=posicionFichasAlgoritmoGenetico()

    fichasSOISMCTS=posicionFichasAlgoritmoGenetico()

    if(turnoJugador==1):
        estado = Stratego(turnos,fichasJugador,fichasSOISMCTS)
    else:
        estado = Stratego(turnos,fichasSOISMCTS,fichasJugador)
    
    while(estado.es_estado_final()==False):
        jugador = estado.jugadorActual
        if(jugador==turnoJugador):
            print("\nTurno del jugador")
            estado = estado.turno_jugador()
        else:
            print("\nTurno del SOISMCTS")
            estado=estado.turno_mcts(mcts)
    estado.imprime_final()

def jugadorContraJugador():
    turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))
    while(turnos<=0):
        print("El número de turnos debe ser mayor que 0")
        turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))
    
    print("¿Desea elegir la posición de las fichas o jugar con posiciones determinadas por el algoritmo genético?")
    print("1. Posiciones elegidas por el usuario")
    print("2. Posiciones determinadas por el algoritmo genético")
    posicion = int(input("Introduce una opción: \n"))
    while(posicion!=1 and posicion!=2):
        posicion = int(input("Introduce una opción válida: \n"))
    if(posicion==1):
        print("Introduce la posición de las fichas del jugador 1: \n")
        fichasJugador1=posicionFichasJugador()
        print("Introduce la posición de las fichas del jugador 2: \n")
        fichasJugador2=posicionFichasJugador()
    else:
        fichasJugador1=posicionFichasAlgoritmoGenetico()
        fichasJugador2=posicionFichasAlgoritmoGenetico()
    estado = Stratego(turnos,fichasJugador1,fichasJugador2)
    
    while(estado.es_estado_final()==False):
        jugador = estado.jugadorActual
        if(jugador==1):
            print("\nTurno del jugador 1")
        else:
            print("\nTurno del jugador 2")
        estado = estado.turno_jugador()
    estado.imprime_final()

def SOISMCTSContraSOISMCTS():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    numeroJugadores = 2
    mcts = pyplAI.SOISMCTS(Stratego.aplica_movimiento,Stratego.obtiene_movimientos,Stratego.es_estado_final,Stratego.gana_jugador,Stratego.determinization,numeroJugadores,tiempoEjecucion, True)
    
    turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))
    while(turnos<=0):
        print("El número de turnos debe ser mayor que 0")
        turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))

    fichasSOISMCTS1=posicionFichasAlgoritmoGenetico()
    fichasSOISMCTS2=posicionFichasAlgoritmoGenetico()

    estado = Stratego(turnos,fichasSOISMCTS1,fichasSOISMCTS2)
   
    while(estado.es_estado_final()==False):
        jugador = estado.jugadorActual
        if(jugador==1):
            print("\nTurno del SOISMCTS 1")
        else:
            print("\nTurno del SOISMCTS 2")
        estado=estado.turno_mcts(mcts)
    estado.imprime_final()

def SOISMCTSContraAleatorio():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    numeroJugadores = 2
    mcts = pyplAI.SOISMCTS(Stratego.aplica_movimiento,Stratego.obtiene_movimientos,Stratego.es_estado_final,Stratego.gana_jugador,Stratego.determinization,numeroJugadores,tiempoEjecucion, True)
    
    turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))
    while(turnos<=0):
        print("El número de turnos debe ser mayor que 0")
        turnos = int(input("Introduce el número de turnos (Se recomiendan unos 200): \n"))
    
    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))
    
    resultados = []
    i=0
    while(i<numeroPartidas):    
        fichasSOISMCTS=posicionFichasAlgoritmoGenetico()
        estado = Stratego(turnos,fichasSOISMCTS)
        
        while(estado.es_estado_final()==False):
            jugador = estado.jugadorActual
            if(jugador==1):
                print("\nTurno del jugador aleatorio")
                estado = estado.turno_prueba()
            else:
                print("\nTurno del SOISMCTS")
                estado=estado.turno_mcts(mcts)
        res = estado.imprime_final()
        resultados.append(res)
        i+=1
    print("\nPartidas Ganadas por los SO-ISMCTS: ", resultados.count(1))
    print("Partidas Ganadas por los jugadores aleatorio: ", resultados.count(2))
    print("Partidas empatadas: ",resultados.count(0))

def partida():
    print("\nEstas son las diferentes tipos de partidas:\n")
    print("1. Jugar una partida contra SOISMCTS")
    print("2. Jugar una partida contra otro jugador")
    print("3. Simular partida SOISMCTS contra SOISMCTS")
    print("4. Simular partidas SOISMCTS contra jugadas aleatorias")
    opcion=int(input("\nElige un modo: \n"))
    while(opcion<1 or opcion>4):
        opcion=int(input("Opción no válida, elige una opción válida: \n"))
    if(opcion==1):
        jugadorContraSOISMCTS()
    elif(opcion==2):
        jugadorContraJugador()
    elif(opcion==3):
        SOISMCTSContraSOISMCTS()
    elif(opcion==4):
        SOISMCTSContraAleatorio()

def main():
    print("\nBienvenido al juego de Stratego\n")
    print("Estos son los modos que contiene este juego:\n")
    print("1. Jugar o simular partidas")
    print("2. Algoritmo genético para encontrar la mejor configuración de piezas")
    opcion=int(input("\nElige una opción: \n"))
    while(opcion<1 or opcion>2):
        opcion=int(input("Opción no válida, elige una opción válida: \n"))
    if(opcion==1):
        partida()
    elif(opcion==2):
        algoritmoGenetico()

if __name__ == "__main__":
    main()