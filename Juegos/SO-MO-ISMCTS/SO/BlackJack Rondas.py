from copy import deepcopy
import random
import pyplAI
from colorama import Fore, init

init(autoreset=True)

class Jugador:
    def __init__(self,creditos, mano):
        self.creditosIniciales=creditos
        self.creditosAnteriores = creditos
        self.creditos=creditos
        self.mano=mano

    def __str__(self):
        cadena="Creditos: "+str(self.creditos)+"\nMano: "
        for carta in self.mano:
            cadena += str(carta[1]) + " de " + carta[2] + ", "
        cadena=cadena.rstrip(", ")
        cadena += "\nPuntuacion: "+str(BlackJack.puntuacion(self.mano))
        return cadena

class Croupier:
    def __init__(self,mano):
        self.cartaOculta=None
        self.mano=mano

    def __str__(self):
        cadena = "Mano: "
        for carta in self.mano:
            if carta != self.cartaOculta:
                cadena += str(carta[1]) + " de " + carta[2] + ", "
        cadena=cadena.rstrip(", ")
        if self.cartaOculta == None:
            cadena += "\nPuntuacion: "+str(BlackJack.puntuacion(self.mano))
        else:
            manoOculta = self.mano[1:]
            cadena += "\nPuntuacion: "+str(BlackJack.puntuacion(manoOculta))
        return cadena

    def ocultarCarta(self):
        self.cartaOculta=self.mano[0]

    def mostrarCarta(self):
        self.cartaOculta=None

class Baraja:
    palos=["oros", "copas", "espadas", "bastos"]
    numeros=["As", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jota", "Reina", "Rey"]

    def __init__(self):
        self.cartas = []
        self.cartasVistas = 0
        self.numMazos = 0

    def crearBaraja(self, numeroMazos):
        res=[]
        for i in range(numeroMazos):
            for palo in Baraja.palos:
                valor=1
                for numero in Baraja.numeros:
                    res.append([valor, numero, palo])
                    valor+=1
        i+=1
        self.cartas = res
        self.numMazos = numeroMazos   
    
    def barajar(self):
        random.shuffle(self.cartas)
    
    def repartir(self, jugador):
        for i in range(2):
            carta = random.choice(self.cartas)
            jugador.mano.append(carta)
            self.cartas.remove(carta)
            self.cartasVistas+=1
        i+=1

    def robar(self, jugador):
        carta = random.choice(self.cartas)
        jugador.mano.append(carta)
        self.cartas.remove(carta)
        self.cartasVistas+=1

class BlackJack:
    jugadores = [1,2]
    numMazos = 4

    def crearBaraja(mazos):
        bar=Baraja()
        bar.crearBaraja(mazos)
        bar.barajar()
        return bar

    def crearPlayer(creditos):
        jug=Jugador(creditos,[])
        return jug

    def crearCroupier():
        crou=Croupier([])
        return crou

    def __init__(self,creditos, visibilidad=False):
        self.jugador=BlackJack.crearPlayer(creditos)
        self.croupier=BlackJack.crearCroupier()
        self.baraja=BlackJack.crearBaraja(BlackJack.numMazos)
        self.primerReparto=True
        self.apuesta=0
        self.jugadorActual=1
        self.visibilidad=visibilidad
        self.iniciarRonda=True
        
    def __str__(self):
        cadenaCroupier="\nCROUPIER:\n"+str(self.croupier)
        cadenaJugador = "\n\nJUGADOR:\n"+str(self.jugador)+"\n"+"Apuesta: "+str(self.apuesta)
        return cadenaCroupier+ " ; "+cadenaJugador
    
    def imprimePartida(self):
        partida = str(self)
        jugador = partida.split(" ; ")[1]
        croupier = partida.split(" ; ")[0]
        print(Fore.GREEN + croupier)
        print(Fore.BLUE + jugador)

    def repartir(self):
        self.baraja.repartir(self.jugador)
        self.baraja.repartir(self.croupier)
        self.croupier.ocultarCarta()
    
    def robaJugador(self):
        self.baraja.robar(self.jugador)

    def robaCroupier(self):
        self.baraja.robar(self.croupier)
    
    def nuevaRonda(self):
        self.apuesta=0
        self.jugador.creditosAnteriores = self.jugador.creditos
        if(self.es_estado_final()==False):
            self.jugador.mano=[]
            self.croupier.mano=[]
            self.primerReparto=True
            self.apostar(2)
            self.repartir()
            if(self.visibilidad==True):
                self.imprimePartida()
            self.comprobarBlackjack()

    def apostar(self, creditos):            
        self.apuesta=creditos
        self.jugador.creditos-=creditos
    
    def rendirse(self):
        self.jugador.creditos+=self.apuesta/2
    
    def doblarApuesta(self):
        if(self.jugador.creditos>=self.apuesta):
            self.apuesta*=2
            self.jugador.creditos-=self.apuesta/2

    #Se comprueba si el jugador ha obtenido BlackJack en la primera pareja de cartas y se ve si el croupier tambien
    def comprobarBlackjack(self):
        if(self.puntuacion(self.jugador.mano)==21 and self.puntuacion(self.croupier.mano)==21):
            self.jugador.creditos+=self.apuesta
            self.croupier.mostrarCarta()
            self.iniciarRonda=True
            if(self.visibilidad==True):
                print(Fore.RED+"\nBlackJack de ambos! Empate")
                print("============================================================")

        elif(self.puntuacion(self.jugador.mano)==21):
            self.jugador.creditos+=self.apuesta*2.5
            self.croupier.mostrarCarta()
            self.iniciarRonda=True
            if(self.visibilidad==True):
                print(Fore.RED+"\nBlackJack! Ganaste")
                print("============================================================")

    #Se comprueban las puntuaciones de los jugadores y con estas se decide el final de la ronda
    def finalRonda(self):
        puntuacionJugador=self.puntuacion(self.jugador.mano)
        puntuacionCroupier=self.puntuacion(self.croupier.mano)
        #Si alguno consiguio BlackJack con la primera pareja gana si no es empate, solo se comprueba
        #si la mesa lo consiguió en la primera pareja, ya que al jugador ya se le comprobó al repartir
        if(puntuacionJugador==21 and puntuacionCroupier==21):
            if(len(self.croupier.mano)==2):
                if(self.visibilidad==True):
                    print(Fore.RED+"\nPerdiste, la mesa obtuvo BlackJack con tan solo dos cartas")
                    print("============================================================")
            else:
                self.jugador.creditos+=self.apuesta
                if(self.visibilidad==True):
                    print(Fore.RED+"\nEmpate, ambos obtuvieron BlackJack")
                    print("============================================================")
        elif(puntuacionJugador>puntuacionCroupier):
            self.jugador.creditos+=self.apuesta*2
            if(self.visibilidad==True):
                print(Fore.RED+"\nGanaste, superaste a la mesa")
                print("============================================================")
        elif(puntuacionJugador<puntuacionCroupier):
            if(self.visibilidad==True):
                print(Fore.RED+"\nPerdiste, la mesa le superó")
                print("============================================================")
        else:
            self.jugador.creditos+=self.apuesta
            if(self.visibilidad==True):
                print(Fore.RED+"\nEmpate con la mesa")
                print("============================================================")

    def es_estado_final_ronda(self):
        return self.posibles_acciones()==["nuevaRonda"]

    def es_estado_final(self):
        return (self.baraja.cartasVistas>=self.baraja.numMazos*52*0.75 and self.apuesta==0) or (self.jugador.creditos<2 and self.apuesta==0)

    def posibles_acciones(self):
        if(self.iniciarRonda==True):
            return ["nuevaRonda"]
        else:
            if(self.primerReparto):
                if(self.jugador.creditos<self.apuesta):
                    if(self.visibilidad==True):
                        print("\nAcciones:\n1. Robar carta\n2. Pasar\n3. Rendirse")
                    roba = [1,self.jugador.mano]
                    pasa = [2,self.jugador.mano]
                    rendirse = [3,self.jugador.mano]
                    return [roba,pasa,rendirse]
                else:
                    if(self.visibilidad==True):
                        print("\nAcciones:\n1. Robar carta\n2. Pasar\n3. Rendirse\n4. Doblar apuesta")
                    roba = [1,self.jugador.mano]
                    pasa = [2,self.jugador.mano]
                    rendirse = [3,self.jugador.mano]
                    doblar = [4,self.jugador.mano]
                    return [roba,pasa,rendirse,doblar]
            else:
                if(self.visibilidad==True):
                    print("\nAcciones:\n1. Robar carta\n2. Pasar")
                roba = [1,self.jugador.mano]
                pasa = [2,self.jugador.mano]
                return [roba,pasa]
        
    def juega_croupier(self):
        self.croupier.mostrarCarta()
        while(self.puntuacion(self.croupier.mano)<17):
                self.robaCroupier()
                if(self.puntuacion(self.croupier.mano)>21):
                    if(self.visibilidad==True):
                        self.imprimePartida()
                        print(Fore.RED+"\nGanaste, la mesa superó los 21 puntos")
                        print("============================================================")
                    self.jugador.creditos+=self.apuesta*2
        if(self.puntuacion(self.croupier.mano)<=21):
            if(self.visibilidad==True):
                self.imprimePartida()
            self.finalRonda()
    
    def aplica_accion(self,accion):
        accion = accion[0]
        if(accion==1):
            self.robaJugador()
            self.primerReparto=False
            if(self.visibilidad==True):
                self.imprimePartida()
            if(self.puntuacion(self.jugador.mano)>21):
                self.iniciarRonda=True
                if(self.visibilidad==True):
                    print(Fore.RED+"\nPerdiste, superaste los 21 puntos")
                    print("============================================================")
        if(accion==2):
            self.iniciarRonda=True
            self.juega_croupier()
        if(accion==3):
            self.iniciarRonda=True
            self.rendirse()
            if(self.visibilidad==True):
                print(Fore.RED+"\nTe rendiste, recibes la mitad de tu apuesta")
                print("============================================================")
        if(accion==4):
            self.iniciarRonda=True
            self.doblarApuesta()
            self.robaJugador()
            if(self.puntuacion(self.jugador.mano)>21):
                if(self.visibilidad==True):
                    self.imprimePartida()
                    print(Fore.RED+"\nPerdiste, superaste los 21 puntos")
                    print("============================================================")
            else:
                self.juega_croupier()
        return self

    @staticmethod
    def puntuacion(mano):
        puntuacion=0
        numAses=0
        for carta in mano:
            if(carta[0]==1):
                puntuacion+=1
                numAses+=1
            elif(carta[0]>10):
                puntuacion+=10
            else:
                puntuacion+=carta[0]
        if(puntuacion<=11 and numAses>0):
            puntuacion+=10
        return puntuacion

    def finalPartida(self):
        creditosIniciales=self.jugador.creditosIniciales
        creditosFinales=self.jugador.creditos
        if(creditosIniciales>creditosFinales):
            print("\nPerdiste un total de "+str(creditosIniciales-creditosFinales)+" créditos")
        elif(creditosIniciales<creditosFinales):
            print("\nGanaste un total de "+str(creditosFinales-creditosIniciales)+" créditos")
        else:
            print("\nTienes los mismos créditos que al principio de la partida")

    def gana_jugador(self,jugador): #Comprueba si el jugador gana
        creditosIniciales=self.jugador.creditosIniciales
        creditosFinales=self.jugador.creditos
        if(jugador==1):
            if(creditosIniciales<=creditosFinales):
                return True
            else:
                return False
        else:
            if(creditosIniciales>=creditosFinales):
                return True
            else:
                return False
        
    def gana_jugador_ronda(self, jugador):
        creditosInicialesRonda=self.jugador.creditosAnteriores
        creditosFinalesRonda=self.jugador.creditos
        if(jugador==1):
            if(creditosFinalesRonda>=creditosInicialesRonda):
                return True
            else:
                return False
        else:
            if(creditosFinalesRonda<=creditosInicialesRonda):
                return True
            else:
                return False

    def determinization(self):
        cartas_no_visibles=[]
        cartas_no_visibles.extend(self.baraja.cartas)
        cartas_no_visibles.append(self.croupier.cartaOculta)
        random.shuffle(cartas_no_visibles)
        determinization=deepcopy(self)
        determinization.croupier.cartaOculta=random.choice(cartas_no_visibles)
        cartas_no_visibles.remove(determinization.croupier.cartaOculta)
        determinization.baraja.cartas=cartas_no_visibles
        return determinization

    def ronda(self):
        accionesLista = self.posibles_acciones()
        accion=int(input("\nElige una accion: "))
        acciones = [x[0] for x in accionesLista]
        while(accion not in acciones):
            accion=int(input("\nAcción no valida, elige una accion: "))
        accion = acciones.index(accion)
        self.aplica_accion(accionesLista[accion])
    
    def rondaPrueba(self):
        accionesLista = self.posibles_acciones()
        accion=random.choice(accionesLista)
        print("\nAcción: "+str(accion[0]))
        self.aplica_accion(accion)

    def rondaMCTS(self,mcts):
        self.visibilidad=False
        mov=mcts.ejecuta(self)
        if(mov[0]==1):
            print("\nAcción: Robar")
        elif(mov[0]==2):
            print("\nAcción: Pasar")
        elif(mov[0]==3):
            print("\nAcción: Retirarse")
        elif(mov[0]==4):
            print("\nAcción: Doblar apuesta")
        print("============================================================")
        self.visibilidad=True
        self.aplica_accion(mov)
    
    def comprobarNuevaRonda(self):
        self.visibilidad=False
        if(self.posibles_acciones()==["nuevaRonda"]):
            self.visibilidad=True
            self.iniciarRonda=False
            self.nuevaRonda()
            if(self.es_estado_final()==True):
                self.iniciarRonda=True
        self.visibilidad=True
    
def imprime_resultados(resultados):
    resultadoMedio = sum(resultados)/len(resultados)
    if(resultadoMedio>0):
        print("Ganancia Media: "+str(resultadoMedio))
    else:
        print("Perdida Media: "+str(resultadoMedio))

def partida_mcts():
    tiempoEjecucion=float(input("Introduce el tiempo de ejecución del MCTS en segundos: \n"))
    while(tiempoEjecucion<=0):
        tiempoEjecucion=float(input("Introduce un tiempo de ejecución mayor que 0: \n"))
    numeroJugadores=2
    mcts = pyplAI.SOISMCTS(BlackJack.aplica_accion,BlackJack.posibles_acciones,BlackJack.es_estado_final_ronda,BlackJack.gana_jugador_ronda,BlackJack.determinization,numeroJugadores,tiempoEjecucion, True)
    resultados = []
    numPartidas=int(input("Introduce el número de partidas que desea simular: "))
    while(numPartidas<=0):
        numPartidas=int(input("Introduce un número de partidas mayor que 0: "))
    for _ in range(numPartidas):
        partida=BlackJack(100,True)
        while(partida.es_estado_final()==False):
            partida.comprobarNuevaRonda()
            if(partida.iniciarRonda==False):
                partida.rondaMCTS(mcts)
        partida.finalPartida()
        resultados.append(partida.jugador.creditos-partida.jugador.creditosIniciales)
    imprime_resultados(resultados)

def partida_aleatoria():
    resultados = []
    numPartidas=int(input("Introduce el número de partidas que desea simular: \n"))
    while(numPartidas<=0):
        numPartidas=int(input("Introduce un número de partidas mayor que 0: \n"))
    for _ in range(numPartidas):
        partida=BlackJack(100,True)
        while(partida.es_estado_final()==False):
            partida.comprobarNuevaRonda()
            if(partida.iniciarRonda==False):
                partida.rondaPrueba()
        partida.finalPartida()
        resultados.append(partida.jugador.creditos-partida.jugador.creditosIniciales)
    imprime_resultados(resultados)

def partida_jugador():
    partida=BlackJack(100,True)
    while(partida.es_estado_final()==False):
        partida.comprobarNuevaRonda()
        if(partida.iniciarRonda==False):
            partida.ronda()
    partida.finalPartida()
    
def main():
    print("\nBienvenido al juego de BlackJack\n")
    print("Estos son los modos que contiene este juego:\n")
    print("1. Jugar contra el croupier")
    print("2. Simular partidas con SOISMCTS")
    print("3. Simular partidas aleatorias")
    opcion=int(input("\nElige una opción: \n"))
    while(opcion<1 or opcion>3):
        opcion=int(input("Opción no válida, elige una opción válida: \n"))
    if(opcion==1):
        print("\nComienza la partida\n")
        partida_jugador()
    elif(opcion==2):
        print("\nComienza la simulación\n")
        partida_mcts()
    elif(opcion==3):
        print("\nComienza la simulación aleatoria\n")
        partida_aleatoria()

if __name__ == "__main__":
    main()
