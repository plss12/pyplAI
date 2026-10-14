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
    #Reglas de la Escoba de 15 (reglamento de los Juegos Bonaerenses): se reparten 3 cartas a cada jugador
    #y 4 a la mesa, y se vuelven a repartir 3 cuando todos se quedan sin cartas. Quien juega una carta que
    #suma 15 con cartas de la mesa está obligado a llevárselas, y si se lleva todas hace escoba. Al final
    #se cuentan escobas, cartas, oros, setenta y siete de oros; en caso de empate en cartas, oros o
    #setenta no puntúa nadie

    #Valor de cada carta en la setenta según su número (las figuras valen 10)
    valoresSetenta={7:21, 6:18, 1:16, 5:15, 4:14, 3:13, 2:12, 8:10, 9:10, 10:10}

    def __init__(self,numeroJugadores,visibilidad):
        self.baraja=self.crearBaraja()
        self.jugadores=self.crearJugadores(numeroJugadores)
        self.listaJugadores=[jugador.id for jugador in self.jugadores]
        self.mesa=self.crearMesa()
        self.jugadorActual=1
        #Reparte el último jugador, que es también el último en jugar en cada ronda
        self.ultimoJugadorCapturando=numeroJugadores
        self.visibilidad=visibilidad
        self.escobaDeMuestra()

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
        return jugadores

    def crearMesa(self):
        nuevaMesa=Mesa()
        Baraja.repartirMesa(self.baraja, nuevaMesa)
        return nuevaMesa

    #Si las cuatro cartas de la mesa suman 15, el que reparte se las lleva y se anota una escoba
    def escobaDeMuestra(self):
        if(sum(carta[0] for carta in self.mesa.cartas)==15):
            repartidor=self.jugadores[-1]
            repartidor.escobas+=1
            repartidor.addCartasCapturadas(self.mesa.cartas)
            self.mesa.cartas=[]

    def capturar(self, carta, listaCaptura):
        jugador=self.jugadores[self.jugadorActual-1]
        if(len(listaCaptura)==len(self.mesa.cartas)):
            jugador.escobas+=1
        jugador.eliminarCarta(carta)
        jugador.addCartaCapturada(carta)
        jugador.addCartasCapturadas(listaCaptura)
        self.mesa.eliminarCartas(listaCaptura)
        self.ultimoJugadorCapturando=self.jugadorActual

    def dejarCartaMesa(self, carta):
        self.jugadores[self.jugadorActual-1].eliminarCarta(carta[0])
        self.mesa.addCarta(carta[0])

    #Al terminar la mano, las cartas que quedan en la mesa son para el último jugador que se llevó cartas
    def capturarCartasSobrantesFinales(self):
        jugadorUltimaCaptura=self.jugadores[self.ultimoJugadorCapturando-1]
        jugadorUltimaCaptura.addCartasCapturadas(self.mesa.cartas)
        self.mesa.cartas=[]

    def aplicarMovimiento(self,movimiento):
        #Si el movimiento solo tiene la carta, no hay captura y se deja en la mesa
        if(len(movimiento)==1):
            self.dejarCartaMesa(movimiento)
        else:
            self.capturar(movimiento[0], movimiento[1])
        self.siguienteJugador()
        #Cuando todos se quedan sin cartas se reparten 3 más o, si no quedan, termina la mano
        if(all(len(jugador.cartas)==0 for jugador in self.jugadores)):
            if(len(self.baraja.cartas)>0):
                for jugador in self.jugadores:
                    self.baraja.repartir(jugador)
            else:
                self.capturarCartasSobrantesFinales()
        return self

    #Esta función se encarga de comprobar si hay alguna suma de 15 posible entre una de las cartas del jugador y la mesa
    @staticmethod
    def subsetSum(listaCartas, valor):
        x=15-valor
        res = []
        for i in range(1,len(listaCartas)+1):
            for subset in combinations(listaCartas, i):
                if sum(carta[0] for carta in subset) == x:
                    res.append(list(subset))
        return res

    #Devuelve un diccionario con las key correspondiendo al valor de la carta y con esta estan las cartas que
    # suman 15, asi solo hay que almacenar una vez por valor y no varias si se repitiesen cartas del mismo
    def comprobarMovimientos(self, jugador):
        listaMovimientos={}
        listaCartasMesa=self.mesa.cartas
        valores=set(carta[0] for carta in jugador.cartas)
        for valor in valores:
            listaMovimientos[valor]=Escoba.subsetSum(listaCartasMesa, valor)
        return listaMovimientos

    def siguienteJugador(self):
        if(self.jugadorActual==len(self.jugadores)):
            self.jugadorActual=1
        else:
            self.jugadorActual+=1

    def esEstadoFinal(self):
        return len(self.baraja.cartas)==0 and all(len(jugador.cartas)==0 for jugador in self.jugadores)

    #Índice del único jugador con el valor máximo, o None si hay empate
    @staticmethod
    def ganadorUnico(valores):
        maximo=max(valores)
        if(maximo>0 and valores.count(maximo)==1):
            return valores.index(maximo)
        return None

    #Setenta: suma de la mejor carta de cada palo; sin cartas de los cuatro palos no se puede ganar
    @staticmethod
    def puntosSetenta(capturadas):
        mejores={}
        for carta in capturadas:
            mejores[carta[1]]=max(mejores.get(carta[1],0), Escoba.valoresSetenta[carta[0]])
        if(len(mejores)<4):
            return 0
        return sum(mejores.values())

    def recuentoPuntos(self):
        puntos=[jugador.escobas for jugador in self.jugadores]
        if(self.visibilidad==True):
            print("\nRecuento de puntos: ")
            for i in range(len(self.jugadores)):
                print("El jugador ", str(i+1)," tiene ", str(puntos[i]), " escobas")
        cartas=[len(jugador.capturadas) for jugador in self.jugadores]
        oros=[sum(1 for carta in jugador.capturadas if carta[1]=="oros") for jugador in self.jugadores]
        setenta=[Escoba.puntosSetenta(jugador.capturadas) for jugador in self.jugadores]
        for nombre, valores in (("cartas",cartas),("oros",oros),("setenta",setenta)):
            ganador=Escoba.ganadorUnico(valores)
            if(ganador is not None):
                puntos[ganador]+=1
                if(self.visibilidad==True):
                    print("El jugador ", str(ganador+1)," gana el punto de ", nombre)
            elif(self.visibilidad==True):
                print("Empate en ", nombre, ": nadie se anota el punto")
        for i in range(len(self.jugadores)):
            if([7,"oros"] in self.jugadores[i].capturadas):
                puntos[i]+=1
                if(self.visibilidad==True):
                    print("El jugador ", str(i+1)," tiene el siete de oros (siete de velo)")
        return puntos

    #Gana el jugador con más puntos; si varios empatan en cabeza, la partida es un empate
    def ganaJugador(self, jugador):
        ganador=Escoba.ganadorUnico(self.recuentoPuntos())
        return ganador is not None and ganador+1==jugador

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

    #Traduce el diccionario de sumas de 15 a la lista de movimientos: cada carta que suma 15 con cartas
    #de la mesa debe llevárselas (una opción por cada combinación posible) y el resto se dejan en la mesa
    @staticmethod
    def traducirPosiblesMovimientos(cartas,diccMovimientos,visibilidad):
        res=[]
        for carta in cartas:
            capturas=diccMovimientos[carta[0]]
            if(len(capturas)>0):
                for captura in capturas:
                    res.append([carta, captura])
            else:
                res.append([carta])
        if(visibilidad==True):
            for x, movimiento in enumerate(res, start=1):
                carta=movimiento[0]
                if(len(movimiento)==1):
                    print(x,"º: Dejar "+str(carta[0]) + " de " +carta[1])
                else:
                    cartasCaptura=", ".join(str(c[0]) + " de " + c[1] for c in movimiento[1])
                    print(x,"º: Capturar con "+str(carta[0]) + " de " +carta[1]+" las cartas: "+cartasCaptura)
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
        movimiento=random.choice(traducido)
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

def SOISMCTSContraAleatorios():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución de los SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))

    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))

    numeroJugadores = 4
    mcts = pyplAI.SOISMCTS(Escoba.aplicarMovimiento,Escoba.obtieneMovimientos,Escoba.esEstadoFinal,Escoba.ganaJugador,Escoba.determinization,numeroJugadores,tiempoEjecucion, True)
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        estado=Escoba(numeroJugadores,True)
        
        while(estado.esEstadoFinal()==False):
            jugador = estado.jugadorActual
            if(jugador==1 or jugador==3):
                estado.rondaMCTS(mcts)
            else:
                estado.rondaPrueba()
        res = estado.finalPartida()
        ganadoresAle= res.count(2)+res.count(4)
        ganadoresMCTS= res.count(1)+res.count(3)
        if(ganadoresAle>ganadoresMCTS):
            resultados.append(2)
        elif(ganadoresAle<ganadoresMCTS):
            resultados.append(1)
        else:
            resultados.append(0)
        i+=1
    print("\nPartidas Ganadas por los SO-ISMCTS: ", resultados.count(1))
    print("Partidas Ganadas por los jugadores aleatorio: ", resultados.count(2))
    print("Partidas empatadas: ",resultados.count(0))

def SOISMCTSContraAleatorio():
    tiempoEjecucion = float(input("Introduce el tiempo de ejecución del SOISMCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion = float(input("Introduce un tiempo de ejecución mayor que 0: \n"))

    numeroPartidas=int(input("Introduce el número de partidas que quieres simular: \n"))
    while(numeroPartidas<=0):
        numeroPartidas = int(input("Introduce un número de partidas mayor que 0: \n"))

    numeroJugadores = 2
    mcts = pyplAI.SOISMCTS(Escoba.aplicarMovimiento,Escoba.obtieneMovimientos,Escoba.esEstadoFinal,Escoba.ganaJugador,Escoba.determinization,numeroJugadores,tiempoEjecucion, True)
    
    resultados = []
    i=0
    while(i<numeroPartidas):
        estado=Escoba(numeroJugadores,True)
        
        while(estado.esEstadoFinal()==False):
            jugador=estado.jugadorActual
            if(jugador==1):
                estado.rondaMCTS(mcts)
            else:
                estado.rondaPrueba()
        res = estado.finalPartida()
        if(len(res)==2):
            resultados.append(0)
        else:
            resultados.append(res[0])
        i+=1
    print("\nPartidas Ganadas por el SO-ISMCTS: ",resultados.count(1))
    print("Partidas Ganadas por el jugador aleatorio: ",resultados.count(2))
    print("Partidas empatadas: ",resultados.count(0))

def main():
    print("\nBienvenido al juego de la Escoba\n")
    print("Estos son los modos que contiene este juego:\n")
    print("1. Jugar una partida contra SOISMCTS")
    print("2. Jugar una partida contra otros jugadores")
    print("3. Simular partidas con 2 SOISMCTS y 2 aleatorios")
    print("4. Simular partidas SOISMCTS contra jugadas aleatorias")
    opcion=int(input("\nElige un modo: \n"))
    while(opcion<1 or opcion>4):
        opcion=int(input("Opción no válida, elige una opción válida: \n"))
    if(opcion==1):
        jugadorContraSOISMCTS()
    elif(opcion==2):
        jugadorContraJugador()
    elif(opcion==3):
        SOISMCTSContraAleatorios()
    elif(opcion==4):
        SOISMCTSContraAleatorio()
        
if __name__ == "__main__":
    main()