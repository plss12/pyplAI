from copy import deepcopy
import random
from itertools import combinations
import pyplAI
from colorama import Fore, init

init(autoreset=True)

class Jugador:
    def __init__(self, jugador):
        self.id = jugador
        self.cartas = []
        self.escobas = 0
        self.capturadas = []
    
    def __eq__(self, id):
        return self.id==id

    def __str__(self):
        cadena=""
        for carta in self.cartas:
            cadena+=str(carta[0]) + " de " +carta[1]+", "
        return cadena.rstrip(", ")
    
    def addCarta(self, carta):
        self.cartas.append(carta)

    def addCartas(self, cartas):
        for carta in cartas:
            self.addCarta(carta)
    
    def addCartaCapturada(self, carta):
        self.capturadas.append(carta)

    def addCartasCapturadas(self, cartas):
        for carta in cartas:
            self.addCartaCapturada(carta)
    
    def eliminarCarta(self, carta):
        self.cartas.remove(carta)

    def eliminarCartas(self, cartas):
        for carta in cartas:
            self.eliminarCarta(carta)

class Mesa:
    def __init__(self):
        self.cartas=[]

    def __str__(self):
        cartasCadena = ""
        for carta in self.cartas:
            cartasCadena+=str(carta[0]) + " de " +carta[1]+", "
        cadena=cartasCadena.rstrip(", ")
        return cadena

    def addCarta(self, carta):
        self.cartas.append(carta)

    def addCartas(self, cartas):
        for carta in cartas:
            self.addCarta(carta)
    
    def eliminarCarta(self, carta):
        self.cartas.remove(carta)

    def eliminarCartas(self, cartas):
        for carta in cartas:
            self.eliminarCarta(carta)
    
class Baraja:
    
    palos=["oros", "copas", "espadas", "bastos"]
    numeros=["1", "2", "3", "4", "5", "6", "7", "Jota", "Caballo", "Rey"]
    valores=[1,2,3,4,5,6,7,8,9,10]

    def __init__(self):
        self.cartas = Baraja.crearBaraja()
    
    def __eq__(self, other):
        return self.cartas == other.cartas

    @staticmethod
    def crearBaraja():
        res=[]
        for palo in Baraja.palos:
            for numero in range(1,11):
                res.append([numero,palo])
        return res
    
    def barajar(self):
        random.shuffle(self.cartas)
    
    def repartir(self, jugador):
        for i in range(3):
            jugador.addCarta(self.cartas.pop())
        i+=1
    
    def repartirMesa(self, mesa):
        for i in range(4):
            mesa.addCarta(self.cartas.pop())
        i+=1

    def robar(self, jugador):
        jugador.addCarta(self.cartas.pop())

class Escoba:

    def __init__(self,numeroJugadores,visibilidad):
        self.baraja=self.crearBaraja()
        self.jugadores=self.crearJugadores(numeroJugadores)
        self.listaJugadores=[jugador.id for jugador in self.jugadores]
        self.mesa=self.crearMesa()
        self.jugadorActual=1
        self.ultimoJugadorCapturando=1
        self.visibilidad=visibilidad
        
    def __str__(self):
        cadena="\nMESA:\n"+str(self.mesa)+";"+"\n\nJUGADOR:\n"+str(self.jugadores[self.jugadorActual-1])+"\n"
        return cadena
    
    def crearBaraja(self):
        nuevaBaraja=Baraja()
        nuevaBaraja.barajar()
        return nuevaBaraja

    def crearJugadores(self, numeroJugadores):
        jugadores=[]
        for i in range(numeroJugadores):
            jug=Jugador(i+1)
            self.baraja.repartir(jug)
            jugadores.append(jug)
            i+=1
        return jugadores

    def crearMesa(self):
        nuevaMesa=Mesa()
        Baraja.repartirMesa(self.baraja, nuevaMesa)
        return nuevaMesa
    
    def capturar(self, carta, listaCaptura):
        jugador=self.jugadores[self.jugadorActual-1]
        numeroCartasMesa=len(self.mesa.cartas)
        numeroCartasCapturadas=len(listaCaptura)
        jugador.eliminarCarta(carta)
        jugador.addCartaCapturada(carta)
        if(numeroCartasMesa==numeroCartasCapturadas):
            jugador.escobas+=1
        jugador.addCartasCapturadas(listaCaptura)
        self.mesa.eliminarCartas(listaCaptura)

    def dejarCartaMesa(self, carta):
        self.jugadores[self.jugadorActual-1].eliminarCarta(carta[0])
        self.mesa.addCarta(carta[0])

    def capturarCartasSobrantesFinales(self):
        jugadorUltimaCaptura=self.jugadores[self.ultimoJugadorCapturando-1]
        jugadorUltimaCaptura.addCartasCapturadas(self.mesa.cartas)
        self.mesa.eliminarCartas(self.mesa.cartas)

    def aplicarMovimiento(self,movimiento):
        #Si el movimiento es una carta, esto es, no hay capturas, se deja en la mesa
        if(len(movimiento)==1):
            self.dejarCartaMesa(movimiento)
            if(len(self.baraja.cartas)>0):
                self.baraja.robar(self.jugadores[self.jugadorActual-1])
        #Si el movimiento es una lista, esto es, hay capturas, se capturan
        else:
            self.capturar(movimiento[0], movimiento[1])
            self.ultimoJugadorCapturando=self.jugadorActual
            if(len(self.baraja.cartas)>0):
                self.baraja.robar(self.jugadores[self.jugadorActual-1])
        self.siguienteJugador()
        return self

    #Esta función se encarga de comprobar si hay alguna suma de 15 posible entre una de las cartas del jugador y la mesa
    @staticmethod
    def subsetSum(listaCartas, valor):
        x=15-valor
        n=len(listaCartas)
        res = []
        # Iterating through all possible
        # subsets of arr from lengths 0 to n:
        for i in range(n+1):
            for subset in combinations(listaCartas, i):
                # printing the subset if its sum is x:
                valorSubset=[]
                for carta in subset:
                    valorSubset.append(carta[0])
                if sum(valorSubset) == x:
                    res.append(list(subset))
        return res

    #Devuelve un diccionario con las key correspondiendo al valor de la carta y con esta estan las cartas que
    # suman 15, asi solo hay que almacenar una vez por valor y no varias si se repitiesen cartas del mismo 
    def comprobarMovimientos(self, jugador):
        listaMovimientos={}
        listaCartasMesa=self.mesa.cartas
        valores=[]
        for carta in jugador.cartas:
            valores.append(carta[0])
        valores=list(set(valores))
        for valor in valores:
            listaSumas=Escoba.subsetSum(listaCartasMesa, valor)
            listaMovimientos[valor]=listaSumas
        return listaMovimientos
        
    def siguienteJugador(self):
        if(self.jugadorActual==len(self.jugadores)):
            self.jugadorActual=1
        else:
            self.jugadorActual+=1
    
    def esEstadoFinal(self):
        numJugadores=len(self.jugadores)
        numJugadoresSinCartas=0
        for jugador in self.jugadores:
            if len(jugador.cartas)==0:
                numJugadoresSinCartas+=1
        if numJugadoresSinCartas==numJugadores:
            self.capturarCartasSobrantesFinales()
            return True
        else:
            return False

    def recuentoPuntos(self):
        puntos=[]
        listnumSietes=[]
        listnumOros=[]
        listnumCartas=[]
        i=0
        if(self.visibilidad==True):
            print("\nRecuento de puntos: ")
        for jugador in self.jugadores:
            puntosJugador=jugador.escobas
            if(self.visibilidad==True):
                print("El jugador ", str(i+1)," tiene ", str(jugador.escobas), " escobas lo que equivale a ", str(jugador.escobas), " puntos")
            capturasJugador=jugador.capturadas
            listnumCartas.append(len(capturasJugador))
            numSietes=0
            numOros=0
            for carta in capturasJugador:
                if(carta[0]=="7"):
                    numSietes+=1
                if(carta[1]=="oros"):
                    numOros+=1
                if(carta[1]=="oros" and carta[0]==7):
                    puntosJugador+=1
                    if(self.visibilidad==True):
                        print("El jugador ", str(i+1)," tiene una siete de oros (guindis) lo que equivale a 1 punto")
            listnumSietes.append(numSietes)
            listnumOros.append(numOros)
            if(numSietes==4):
                puntosJugador+=2
                if(self.visibilidad==True): 
                    print("El jugador ", str(i+1)," tiene los cuatro sietes lo que equivale a 2 puntos")
            if(numOros==10):
                puntosJugador+=2
                if(self.visibilidad==True):
                    print("El jugador ", str(i+1)," tiene todos los oros lo que equivale a 2 puntos")
            puntos.append(puntosJugador)
            i+=1
        for i in range(len(puntos)):
            if(listnumCartas[i]==max(listnumCartas)):
                puntos[i]+=1
                if(self.visibilidad==True):
                    print("El jugador ", str(i+1)," tiene el mayor numero de cartas capturadas lo que equivale a 1 punto")
            if(listnumSietes[i]==max(listnumSietes)):
                puntos[i]+=1
                if(self.visibilidad==True):
                    print("El jugador ", str(i+1)," tiene el mayor numero de sietes capturados lo que equivale a 1 punto")
            if(listnumOros[i]==max(listnumOros)):
                puntos[i]+=1
                if(self.visibilidad==True):
                    print("El jugador ", str(i+1)," tiene el mayor numero de oros capturados lo que equivale a 1 punto")
        return puntos
    
    def ganaJugador(self, jugador):
        puntos=self.recuentoPuntos()
        maximo=max(puntos)
        ganadores=[]
        for i in range(len(puntos)):
            if(puntos[i]==maximo):
                ganadores.append(i+1)
        if(jugador in ganadores):
            return True
        else:
            return False

    def finalPartida(self):
        puntos=self.recuentoPuntos()
        maximo=max(puntos)
        if(puntos.count(maximo)>1):
            if(self.visibilidad==True):
                print(Fore.RED+"\nHay empate entre los jugadores: ")
            ganadores = []
            for i in range(len(puntos)):
                if(puntos[i]==maximo):
                    if(self.visibilidad==True):
                        print(Fore.RED+"Jugador "+str(i+1))
                    ganadores.append(i+1)
            return ganadores
        else:
            ganador=puntos.index(maximo)
            if(self.visibilidad==True):
                print(Fore.RED+"\nEl ganador es el jugador "+str(ganador+1)+" con "+str(maximo)+" puntos")
            return [ganador+1]
        

    #Es el encargado de traducir el diccionario con los valores y las cartas que suman 15 a una lista, con todas las
    #cartas con sus posibles capturas aunque estas se repitan en valor, o solo las cartas si no hay ningun movimiento 
    @staticmethod
    def traducirPosiblesMovimientos(cartas,diccMovimientos,visibilidad):
        res=[]
        #Recorremos las cartas del jugador y comprobamos si hay alguna tiene alguna captura
        for carta in cartas:
            capturas=diccMovimientos[carta[0]]
            if(len(capturas)>0):
                for capturas in capturas:
                    res.append([carta, capturas])
        #Si no hay ninguna carta con captura, se deja una carta en la mesa
        sum=0
        if (len(res)==0):
            if(visibilidad==True):
                print("No hay capturas posibles, debes dejar alguna de tus cartas en la mesa")
            x=1
            for carta in cartas:
                res.append([carta])
                if(visibilidad==True):
                    print(x,"º: Dejar "+str(carta[0]) + " de " +carta[1])
                x+=1
            sum=len(res)
        #Si hay alguna carta con captura, se muestran todas las posibles
        else:
            x=1
            for i in res:
                cartasCaptura=""
                for carta in i[1]:
                    cartasCaptura+=str(carta[0]) + " de " +carta[1]+", "
                if(visibilidad==True):
                    print(x,"º: Puedes capturar con "+str(i[0][0]) + " de " +i[0][1]+" las cartas: "+cartasCaptura.rstrip(", "))
                x+=1
            sum+=len(res)
        if(visibilidad==True):
            print("Posibles mov ",sum)
        return res

    def obtieneMovimientos(self): #Obtiene los movimientos disponibles traducidos
        movsSinTraducir = self.comprobarMovimientos(self.jugadores[self.jugadorActual-1])
        movsTraducidos = self.traducirPosiblesMovimientos(self.jugadores[self.jugadorActual-1].cartas, movsSinTraducir, self.visibilidad)
        return movsTraducidos
    
    #Función que a partir del estado de la partida y un jugador de la partida, devuelve una determinización aleatoria 
    #posible de la partida a través de obtener la información disponible del estado de la partida para el jugador
    def determinization(self): 
        cartas_no_visibles=[]
        cartas_no_visibles.extend(self.baraja.cartas)
        for jugador in self.jugadores:
            if(jugador!=self.jugadorActual):
                cartas_no_visibles.extend(jugador.cartas)
        random.shuffle(cartas_no_visibles)
        determinizacion=deepcopy(self)
        for jugador in determinizacion.jugadores:
            if(jugador!=determinizacion.jugadores[determinizacion.jugadorActual-1]):
                numer_cartas=len(jugador.cartas)
                cartas=[]
                for i in range(numer_cartas):
                    carta=random.choice(cartas_no_visibles)
                    cartas.append(carta)
                    cartas_no_visibles.remove(carta)
                    i+=1
                jugador.cartas=cartas
        determinizacion.baraja.cartas=cartas_no_visibles
        return determinizacion
    
    def imprimeEstado(self):
        partida = str(self)
        mesa = partida.split(";")[0]
        jugador = partida.split(";")[1]
        print(Fore.GREEN + mesa)
        print(Fore.BLUE + jugador)
            

    def ronda(self):
        print(Fore.RED+"\nTurno del jugador "+ str(self.jugadorActual))
        self.imprimeEstado()
        listaMov=self.comprobarMovimientos(self.jugadores[self.jugadorActual-1])
        traducido=self.traducirPosiblesMovimientos(self.jugadores[self.jugadorActual-1].cartas,listaMov,self.visibilidad)
        indiceMov=int(input("Elige un movimiento de la lista anterior: "))
        while(indiceMov>len(traducido) or indiceMov<1):
            print("Ese movimiento no es valido")
            indiceMov=int(input("Elige un movimiento de la lista anterior: "))
        movimiento=traducido[indiceMov-1]
        self.aplicarMovimiento(movimiento)
    
    def rondaPrueba(self):
        print(Fore.RED+"Turno del jugador aleatorio "+str(self.jugadorActual))
        self.imprimeEstado()
        listaMov=self.comprobarMovimientos(self.jugadores[self.jugadorActual-1])
        traducido=self.traducirPosiblesMovimientos(self.jugadores[self.jugadorActual-1].cartas,listaMov,self.visibilidad)
        indiceMov=1
        movimiento=traducido[indiceMov-1]
        self.aplicarMovimiento(movimiento)

    def rondaMCTS(self,mcts):
        print(Fore.RED+"Turno del jugador SOISMCTS "+str(self.jugadorActual))
        self.imprimeEstado()
        self.visibilidad=False
        mov = mcts.ejecuta(self)
        if(len(mov)==1):
            print("El jugador deja la carta ",mov[0][0]," de ",mov[0][1])
        else:
            print("El jugador captura con la carta ",mov[0][0]," de ",mov[0][1]," las cartas: ")
            for carta in mov[1]:
                print("   -",carta[0]," de ",carta[1])
        self.visibilidad=True
        self.aplicarMovimiento(mov)


def jugadorContraSOISMCTS():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))

    numeroJugadores = int(input("¿Contra cúantos jugadores quieres jugar? (1-3) \n"))
    while(numeroJugadores<1 or numeroJugadores>3):
        numeroJugadores = int(input("Introduce un número de jugadores entre 1 y 3: \n"))
    
    posicionJugador = int(input("¿En qué posición quieres jugar? (1-Número Jugadores) \n"))
    while(posicionJugador<1 or posicionJugador>numeroJugadores+1):
        posicionJugador = int(input("Introduce una posición entre 1 y el número de jugadores: \n"))
    
    mcts = pyplAI.SOISMCTS(Escoba.aplicarMovimiento,Escoba.obtieneMovimientos,Escoba.esEstadoFinal,Escoba.ganaJugador,Escoba.determinization,numeroJugadores+1,tiempoEjecucion, True)
    estado=Escoba(numeroJugadores+1,True)
    while(estado.esEstadoFinal()==False):
        jugador = estado.jugadorActual
        if(jugador==posicionJugador):
            estado.ronda()
        else:
            estado.rondaMCTS(mcts)
    estado.finalPartida()

def jugadorContraJugador():
    numeroJugadores = int(input("¿Cúantos jugadores vais a jugar? (2-4) \n"))
    while(numeroJugadores<2 or numeroJugadores>4):
        numeroJugadores = int(input("Introduce un número de jugadores entre 2 y 4: \n"))

    estado=Escoba(numeroJugadores,True)
    
    while(estado.esEstadoFinal()==False):
        jugador = estado.jugadorActual
        print(Fore.RED+"\nTurno del jugador "+str(jugador))
        estado.ronda()
    estado.finalPartida()

def SOISMCTSContraSOISMCTS():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    numeroJugadores = 2
    mcts = pyplAI.SOISMCTS(Escoba.aplicarMovimiento,Escoba.obtieneMovimientos,Escoba.esEstadoFinal,Escoba.ganaJugador,Escoba.determinization,numeroJugadores,tiempoEjecucion, True)
    
    estado=Escoba(numeroJugadores,True)
    
    while(estado.esEstadoFinal()==False):
        estado.rondaMCTS(mcts)
    estado.finalPartida()

def SOISMCTSContraAleatorio():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    numeroJugadores = 2
    mcts = pyplAI.SOISMCTS(Escoba.aplicarMovimiento,Escoba.obtieneMovimientos,Escoba.esEstadoFinal,Escoba.ganaJugador,Escoba.determinization,numeroJugadores,tiempoEjecucion, True)
    
    estado=Escoba(numeroJugadores,True)
    
    while(estado.esEstadoFinal()==False):
        jugador=estado.jugadorActual
        if(jugador==1):
            estado.rondaMCTS(mcts)
        else:
            estado.rondaPrueba()
    estado.finalPartida()

def main():
    print("\nBienvenido al juego de la Escoba\n")
    print("Estos son los modos que contiene este juego:\n")
    print("1. Jugar una partida contra SOISMCTS")
    print("2. Jugar una partida contra otros jugadores")
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
        
if __name__ == "__main__":
    main()