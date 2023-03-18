import random
from copy import deepcopy
from colorama import Fore, init
import pyplAI

init(autoreset=True)

class Holjjak:
    listaJugadores = [1, 2]
    jugadores = 2
    numeroCanicas1 = 10
    numeroCanicas2 = 10
    def __init__(self):
        self.jugadorActual=1
        self.canicasJugadores=[Holjjak.numeroCanicas1,Holjjak.numeroCanicas2]
        #Habra dos turnos, el 0 en el que el jugador elige el numero de canicas a coger y el 1 en el que el jugador dice si el 
        #numero de canicas que ha cogido es par o impar
        self.turno=0
        self.canicasApostadas=0

    def __str__(self):
        jugador1=Fore.RED+"Jugador 1: "+str(self.canicasJugadores[0])+" canicas\n"
        jugador2=Fore.BLUE+"Jugador 2: "+str(self.canicasJugadores[1])+" canicas"
        return jugador1+jugador2
    
    def obtiene_movimientos(self):
        if self.turno==1:
            movs=["Par","Impar"]
            return movs
        else:
            movs=[]
            for i in range(1,self.canicasJugadores[self.jugadorActual-1]+1):
                movs.append(i)
            return movs
    
    def aplica_movimiento(self,mov):
        jugadorRival=3-self.jugadorActual
        #Si el mov es un string, estamos en turno de adivinar
        if(type(mov)==str):
            self.turno=0
            #Si aciertas el numero de canicas que coges, obtienes las canicas del rival, si no, das las tuyas al rival
            if(mov=="Par"):
                if(self.canicasApostadas%2==0):
                    self.canicasJugadores[self.jugadorActual-1]+=self.canicasApostadas
                    self.canicasJugadores[jugadorRival-1]-=self.canicasApostadas
                else:
                    canicasPerdidas=self.canicasApostadas
                    canicasJugador=self.canicasJugadores[self.jugadorActual-1]
                    #Se comprueba si la apuesta es mayor que el numero de canicas que tiene
                    #si es asi, se le dan el numero de canicas que triene el jugador aunque sean menos
                    if(canicasPerdidas>canicasJugador):
                        canicasPerdidas=canicasJugador
                    self.canicasJugadores[self.jugadorActual-1]-=canicasPerdidas
                    self.canicasJugadores[jugadorRival-1]+=canicasPerdidas
            else:
                if(self.canicasApostadas%2==0):
                    canicasPerdidas=self.canicasApostadas
                    canicasJugador=self.canicasJugadores[self.jugadorActual-1]
                    #Se comprueba si la apuesta es mayor que el numero de canicas que tiene
                    #si es asi, se le dan el numero de canicas que triene el jugador aunque sean menos
                    if(canicasPerdidas>canicasJugador):
                        canicasPerdidas=canicasJugador
                    self.canicasJugadores[self.jugadorActual-1]-=canicasPerdidas
                    self.canicasJugadores[jugadorRival-1]+=canicasPerdidas
                else:
                    self.canicasJugadores[self.jugadorActual-1]+=self.canicasApostadas
                    self.canicasJugadores[jugadorRival-1]-=self.canicasApostadas
        #Si el mov es un int, estamos en turno de coger canicas
        else:
            self.turno=1
            self.canicasApostadas=mov
            self.jugadorActual=3-self.jugadorActual
        return self
    
    def gana_jugador(self,jugador):
        jugadorRival=3-jugador
        if(self.canicasJugadores[jugadorRival-1]<=0):
            return True
        else:
            return False
    
    def es_estado_final(self):
        if(self.gana_jugador(1) or self.gana_jugador(2)):
            return True
        else:
            return False

    def determinization(self):
            determinization = deepcopy(self)
            if(determinization.turno==0):
                return determinization
            else:
                jugador = determinization.jugadorActual
                canicasRival = determinization.canicasJugadores[3-jugador-1]
                canicasApostadas = random.randint(1,canicasRival)
                determinization.canicasApostadas = canicasApostadas
                return determinization
    
    @staticmethod
    def accion_visible(accion):
        if(type(accion)==str):
            return True
        else:
            return False
    
    def imprime_estado(self):
        if(self.turno==0):
            print("\n")
            print(self,"\n")
            print("Turno de coger canicas")
        else:
            print("\n")
            print(self,"\n")
            print("Turno de adivinar")

    def imprime_final(self):
        print("\nFinal de la partida")
        print(self,"\n")
        jugadores = Holjjak.listaJugadores
        for jugador in jugadores:
            if self.gana_jugador(jugador):
                if(jugador==1):
                    print(Fore.RED+"Gana el jugador 1 con "+str(self.canicasJugadores[jugador-1])+" canicas")
                    return 1
                else:
                    print(Fore.BLUE+"Gana el jugador 2 con "+str(self.canicasJugadores[jugador-1])+" canicas")
                    return 2

    def turno_jugador(self):
        self.imprime_estado()
        movs = self.obtiene_movimientos()
        imprime_movs(movs)
        mov = int(input())
        while(mov<=0 or mov>=len(movs)+1):
            print("Movimiento invalido")
            mov = int(input())
        mov=movs[mov-1]
        if(type(mov)==str):
            print("\n")
            print("El rival tenía escondidas",self.canicasApostadas,"canicas")
            print("\n")
        print("===========================================\n")
        return self.aplica_movimiento(mov)
            
    def turno_mcts(self,mcts,ismcts):
        self.imprime_estado()
        if(self.turno==0):
            mov = mcts.ejecuta(self)
        else:
            mov = ismcts.ejecuta(self)
        if(mov!=None):                
            print("===========================================\n")
            return self.aplica_movimiento(mov)
        else:
            return self
        
    def turno_aleatorio(self):
        self.imprime_estado()
        movs = self.obtiene_movimientos()
        mov = random.choice(movs)
        print("===========================================\n")
        return self.aplica_movimiento(mov)
    
def imprime_movs(movs):
    if(type(movs[0])==str):
        print("Adivina si el numero de canicas que ha apostado el rival es par o impar")
        print(1,"-",movs[0])
        print(2,"-",movs[1])
    else:
        print("Elige el numero de canicas que quieres apostar (1-"+str(movs[-1])+")")

def jugadorContraISMCTS():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del ISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))

    algoritmo= int(input("¿Quieres jugar contra el algoritmo de SO(1) o contra el algoritmo de MO(2)?: \n"))
    while(algoritmo<1 or algoritmo>2):
        algoritmo = int(input("Introduce 1 para utilizar MOISMCTS o 2 para utilizar SOISMCTS: \n"))

    if(algoritmo==1):
        ismcts = pyplAI.SOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.jugadores,tiempoEjecucion, True)
    else:
        ismcts = pyplAI.MOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.accion_visible,Holjjak.jugadores,tiempoEjecucion, True)
    mcts = pyplAI.MCTS(Holjjak.aplica_movimiento, Holjjak.obtiene_movimientos, Holjjak.es_estado_final, Holjjak.gana_jugador,Holjjak.jugadores, tiempoEjecucion, True)

    posicionJugador = int(input("¿Desea jugar primero o segundo? (1-2)\n"))
    while(posicionJugador<1 or posicionJugador>2):
        posicionJugador = int(input("Introduce 1 para ser primero o 2 para ser segundo: \n"))

    estado=Holjjak()
    while(estado.es_estado_final()==False):
        jugador = estado.jugadorActual
        if(jugador==posicionJugador):
            print(Fore.RED+"\nTurno del jugador "+str(jugador))
            estado.turno_jugador()
        else:
            print(Fore.BLUE+"\nTurno del SOISMCTS "+str(jugador))
            estado.turno_mcts(mcts,ismcts)
    estado.imprime_final()

def jugadorContraJugador():
    estado=Holjjak()
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
        ismcts1=pyplAI.SOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.jugadores,tiempoEjecucion, True)
        ismcts2=pyplAI.SOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.jugadores,tiempoEjecucion)
    elif(modo==2):
        ismcts1=pyplAI.SOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.jugadores,tiempoEjecucion, True)
        ismcts2=pyplAI.MOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.accion_visible,Holjjak.jugadores,tiempoEjecucion, True)
    elif(modo==3):
        ismcts1=pyplAI.MOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.accion_visible,Holjjak.jugadores,tiempoEjecucion, True)
        ismcts2=pyplAI.SOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.jugadores,tiempoEjecucion, True)
    else:
        ismcts1=pyplAI.MOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.accion_visible,Holjjak.jugadores,tiempoEjecucion, True)
        ismcts2=pyplAI.MOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.accion_visible,Holjjak.jugadores,tiempoEjecucion, True)
    mcts = pyplAI.MCTS(Holjjak.aplica_movimiento, Holjjak.obtiene_movimientos, Holjjak.es_estado_final, Holjjak.gana_jugador,Holjjak.jugadores, tiempoEjecucion, True)

    resultados=[]
    i=0
    for i in range(numeroPartidas):
        estado=Holjjak()
        while(estado.es_estado_final()==False):
            jugador = estado.jugadorActual
            if(jugador==1):
                if(modo==1 or modo==2):
                    print(Fore.RED+"\nTurno del SOISMCTS "+str(jugador))
                else:
                    print(Fore.RED+"\nTurno del MOISMCTS "+str(jugador))
                estado.turno_mcts(mcts,ismcts1)
            else:
                if(modo==1 or modo==3):
                    print(Fore.BLUE+"\nTurno del SOISMCTS "+str(jugador))
                else:
                    print(Fore.BLUE+"\nTurno del MOISMCTS "+str(jugador))
                estado.turno_mcts(mcts,ismcts2)
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
        ismcts=pyplAI.SOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.jugadores,tiempoEjecucion, True)
    else:
        ismcts=pyplAI.MOISMCTS(Holjjak.aplica_movimiento,Holjjak.obtiene_movimientos,Holjjak.es_estado_final,Holjjak.gana_jugador,Holjjak.determinization,Holjjak.accion_visible,Holjjak.jugadores,tiempoEjecucion, True)
    mcts = pyplAI.MCTS(Holjjak.aplica_movimiento, Holjjak.obtiene_movimientos, Holjjak.es_estado_final, Holjjak.gana_jugador,Holjjak.jugadores, tiempoEjecucion, True)

    resultados=[]
    i=0
    for i in range(numeroPartidas):
        estado=Holjjak()
        while(estado.es_estado_final()==False):
            jugador = estado.jugadorActual
            if(jugador==1):
                if(modo==1):
                    print(Fore.RED+"\nTurno del SOISMCTS "+str(jugador))
                else:
                    print(Fore.RED+"\nTurno del MOISMCTS "+str(jugador))
                estado.turno_mcts(mcts,ismcts)
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
    print("\nBienvenido al juego Holjjak\n")
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