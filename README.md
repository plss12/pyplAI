# pyplAI

## Introducción
Esta biblioteca para Python es el resultado final de un Trabajo de Fin de Grado centrado en la implementación de algoritmos de *Monte Carlo Tree Search* (MCTS) y *minimax* para diferentes tipos de juegos de mesa, entre ellos, según clasifica la teoría de juegos, los juegos de información perfecta, como lo son *el ajedrez* o *las damas*, en los que en todo momento cualquier jugador puede ver toda la información del juego, como los posibles movimientos del rival, y juegos de información imperfecta, como lo son la mayoría de juegos de cartas como por ejemplo *el Uno* o *la brisca*, en el que los jugadores solo conocen información propia, como sus cartas, o información general del juego, como el estado de la mesa, pero desconocen la información del rival, como las cartas de los demás jugadores.

### Juegos de Información Perfecta

Para este tipo de juegos se han implementado los algoritmos de MCTS con UCT [[1]](#MCTS) y minimax con la técnica de poda de alfa-beta [[2]](#Minimax). Además, como ejemplos para ver el correcto uso de la biblioteca, se han creado diferentes juegos de mesa, entre ellos, *TicTacToe* (3 en raya), *Ultimate TicTacToe* [[3]](#UltimateTicTacToe) y *las damas*.

### Juegos de Información Imperfecta

Para este segundo tipo de juegos se han implementado dos algoritmos, el *Single Observer Information Set Monte Carlo Tree Search* [[4]](#ISMCTS) (SO-ISMCTS) y el *Multiple Observer Information Set Monte Carlo Tree Search* [[4]](#ISMCTS) (MO-ISMCTS). El primero de estos algoritmos genera un único árbol desde el punto de vista del jugador al que le toca jugar. Por otro lado, el segundo algoritmo crea un árbol para cada uno de los jugadores y agrupa las acciones que son indiferenciables desde el punto de vista de este jugador, es decir, si un jugador puede realizar varios movimientos que no aportarían información a los rivales, agrupa estos movimientos como si fuesen uno solo, creando un único nodo en el árbol de los jugadores rivales.

Un ejemplo serían los juegos en los que un jugador intercambia una de las cartas de su mano con cualquier carta de la baraja, cuando el jugador efectúa este intercambio los demás jugadores no reciben ningún tipo de información sobre el intercambio de cartas, por lo que su conocimiento sobre el estado del juego no cambia. 

Para estos algoritmos también se han desarrollado varios juegos como ejemplos de uso de la biblioteca, aunque ambos algoritmos se pueden usar en todos los juegos de información imperfecta, se ha diferenciado entre juegos para el SO-ISMCTS y el MO-ISMCTS. Para el primer algoritmo se ha creado *el juego de la escoba*, *el Stratego* y *el blackJack*, y para el segundo se ha desarrollado *el holjjak* (juego de adivinar las canicas del rival) y *el phantom* (variante del 4 en raya en el que no se ven los movimientos del rival).

## Manual de Uso
El primer paso necesario para poder usar esta biblioteca es descargarla. Se puede descargar la biblioteca desde la consola usando el comando \textit{pip install pyplAI}. Tras esto, ya se puede importar en el archivo de Python del juego al que queramos implementarla.

``` python
import pyplAI
```

### Clase sobre el Estado del Juego
Para poder usar esta biblioteca es imprescindible que haya una clase que guarde la información necesaria sobre el estado del juego. Aunque se puede dar a esta clase el nombre que se desee, en este manual se utilizará una clase llamada *Juego* a modo de ejemplo.

``` python
  class Juego:
          .
          .
          .
```

### Atributo Obligatorio *jugadorActual*
Debido a que los algoritmos necesitan saber cuál es el jugador al cual le toca jugar en cada uno de los turnos, es obligatorio añadir un atributo *jugadorActual* en la clase del juego. Además, es muy importante que este atributo tenga este mismo nombre.

``` python
  class Juego:
    def __init__(self):
        self.jugadorActual = 1
                .
                .
                .
```

Este atributo debe contener un valor numérico que representa el índice del jugador al que le toca jugar (empezando por 1). También, debe ir actualizándose conforme se avanza en el juego, por ejemplo, en el *3 en raya*, este atributo se debe iniciar con el valor 1, pero cuando el primer jugador realice su movimiento, se actualiza al valor 2, indicando que el segundo jugador es el que debe realizar su jugada.

Además del atributo para identificar el jugador actual del estado del juego, esta clase deberá implementar ciertos métodos para poder interactuar y obtener información sobre el estado del juego. Algunos métodos son comunes para todos los algoritmos, mientras que otros algoritmos requieren de métodos específicos. Cabe destacar que estos métodos pueden ser nombrados de forma distinta a como se mostrará a continuación, pero es totalmente necesario que reciban los parámetros de entrada y devuelvan la salida tal y como se especifica en este manual.

### Métodos Generales

Los siguientes 4 métodos serán obligatorios para todos los algoritmos que se implementan en esta biblioteca:

**•	obtiene_movimientos(self):** Devolverá una lista con todos los movimientos posibles del jugador actual del estado del juego, es recomendable devolver estos movimientos en un orden aleatorio.

``` python
  class Juego:
          .
          .
          .
        def obtiene_movimientos(self):
                    .
                    .
                    .
            return movimientos
```

**•	aplica_movimiento(self, movimiento):** Aplicará el movimiento dado al estado del juego y devolverá el estado resultante (*self*).

``` python
  class Juego:
          .
          .
          .
        def aplica_movimiento(self, movimiento):
                    .
                    .
                    .
            return self
```

**•	es_estado_final(self):** Comprueba el estado actual del juego, devolviendo *True* o *False* dependiendo de si es un estado final o no.

``` python
  class Juego:
          .
          .
          .
        def es_estado_final(self):
                    .
                    .
                    .
            return True
              o
            return False
```

**•	gana_jugador(self, jugador):** Comprueba si el jugador dado gana el juego en el estado actual de este, devolviendo *True* en caso de que sea ganador, o *False* en caso contrario. La variable *jugador* debe ser un número entero positivo, y se debe situar en el rango de 1, para el primer jugador del juego, hasta *n*, siendo *n* el número total de jugadores.

``` python
  class Juego:
          .
          .
          .
        def gana_jugador(self, jugador):
                    .
                    .
                    .
            return True
              o
            return False
```

### Métodos SO/MO-ISMCTS

Además de los 4 métodos anteriores, los algoritmos de *SO-ISMCTS* y *MO-ISMCTS* necesitan un método adicional para su uso, el cuál se explica a continuación:

**•	determinación(self):** Devuelve una determinación aleatoria del estado del juego, desde el punto de vista del jugador actual.

``` python
  class Juego:
          .
          .
          .
        def determinacion(self):
                    .
                    .
                    .
            return determinacion
```

Por ejemplo, para un juego de cartas en el que cada jugador tiene una mano, hay una mesa con cartas visibles, una pila de descartes y un mazo de robo inicial, el jugador actual no tiene conocimiento sobre las cartas del rival ni las cartas del mazo de robo, pero si sabe cuáles son sus cartas, las de la mesa y las que han sido mandadas a la pila de descartes, por lo que tiene la información sobre cuáles son las cartas restantes, pero aún no sabe donde se encuentran. 

Con esta información, este método debe dar un estado del juego en el que aleatoriamente se distribuyan las cartas que el jugador no tiene localizadas entre las zonas en las que no sabe que cartas hay, en este caso, las zonas serían las manos de los rivales y el mazo de robo.

### Métodos MO-ISMCTS

Además, para el funcionamiento del algoritmo \textit{MO-ISMCTS} se necesitará otro método adicional:

**•	es_movimiento_visible(movimiento):** Este método, dado un movimiento, devuelve *True* si es un movimiento visible para los rivales, o *False* en caso contrario.

``` python
  class Juego:
          .
          .
          .
        def es_movimiento_visible(movimiento):
                    .
                    .
                    .
            return True
              o
            return False
```

Por ejemplo, un movimiento visible para los rivales sería jugar una carta de tu mano sobre la mesa, por lo que, haría saber a los rivales el lugar exacto de esa carta, cosa que antes no sabían. Sin embargo, un movimiento no visible sería intercambiar una carta de tu mano con el mazo de robo sin revelar ninguna de las dos. Esta acción no mostraría nueva información a ningún rival, ya que no se muestran las cartas y los rivales seguirán sin saber que cartas hay en tu mano ni que cartas hay en el mazo.

### Métodos Minimax

En el caso del algoritmo de *minimax*, además de los 4 métodos generales, se necesita un método que devuelva una heurística sobre el estado del juego, es decir, que evalúe su estado para saber como de bueno es desde el punto de vista de un jugador dado:

**•	heuristica(self, jugador):** Este método debe devolver un número entero que refleje una evaluación sobre como de bueno es el estado para el jugador dado. Esta evaluación debe ser mayor cuanto mejor sea el estado del juego para el jugador dado.

``` python
  class Juego:
          .
          .
          .
        def heuristica(self, jugador):
                    .
                    .
                    .
            return evaluacion
```

Por ejemplo, para el juego de *las damas* una posible heurística sería contar el número de fichas del jugador y restarle el número de fichas del rival. Hay multitud de posibles heurísticas para cada uno de los juegos, y se debe tener un conocimiento sobre el juego para poder crear una buena heurística, ya que la heurística tendrá un gran peso a la hora de decidir cuál es el mejor movimiento.

Al igual que en el método *gana_jugador*, el argumento *jugador* debe ser un número entero positivo, desde el 1, para el primer jugador, hasta *n*, para el último jugador, siendo *n* el número total de jugadores.

### Constructor Algoritmo

Una vez tengamos todos estos métodos solamente debemos llamar a la biblioteca y al constructor del algoritmo que se desee utilizar. A esta llamada le pasaremos como argumentos los métodos necesarios para el uso de este algoritmo junto con algunas otras variables que detallaremos a continuación:

**•	numeroJugadores:** Este argumento es obligatorio para todos los algoritmos,  representará el número de jugadores que contiene el juego, siendo este un número entero mayor que cero.

**•	tiempoEjecucion:** Este argumento es común para todos los algoritmos de Monte Carlo, ya que, estos algoritmos necesitan un tiempo límite de ejecución antes de devolver el mejor movimiento encontrado. Este argumento debe ser un número real mayor que cero y representa el tiempo de ejecución en segundos.

**•	profundidadBusqueda:** Este argumento solo es necesario en la llamada al constructor del algoritmo de \textit{minimax}, y sirve para limitar la profundidad en el árbol de búsqueda. Este argumento debe ser un número entero mayor que cero.

Sabiendo todo esto ya podemos ver como se deben hacer las llamadas a la biblioteca y los constructores para cada uno de los tipos de algoritmos. Es muy importante que se siga el orden mostrado en los argumentos de entrada. Además, recordar que \textit{Juego} es la clase de ejemplo que contiene la información sobre el estado del juego, como el atributo \textit{jugadorActual}, y los métodos explicados anteriormente.

**•	MCTS:**

``` python
  mcts = pyplAI.MCTS(
         Juego.aplica_movimiento,
         Juego.obtiene_movimientos, 
         Juego.es_estado_final, 
         Juego.gana_jugador, 
         numeroJugadores, 
         tiempoEjecucion)
```

**•	MinMax:**

``` python
  minmax = pyplAI.Minimax(
           Juego.aplica_movimiento,
           Juego.obtiene_movimientos, 
           Juego.es_estado_final, 
           Juego.gana_jugador, 
           Juego.heuristica,
           numeroJugadores, 
           profundidadBusqueda)
```

**•	SO-ISMCTS:**

``` python
  so_ismcts = pyplAI.SOISMCTS(
              Juego.aplica_movimiento,
              Juego.obtiene_movimientos, 
              Juego.es_estado_final, 
              Juego.gana_jugador, 
              Juego.determinacion,
              numeroJugadores, 
              tiempoEjecucion)
```

**•	MO-ISMCTS:**

``` python
  mo_ismcts = pyplAI.MOISMCTS(
              Juego.aplica_movimiento,
              Juego.obtiene_movimientos, 
              Juego.es_estado_final, 
              Juego.gana_jugador, 
              Juego.determinacion,
              Juego.es_movimiento_visible,
              numeroJugadores, 
              tiempoEjecucion)
```

**•	Modo *verbose*:**

Si queremos ver algunos detalles cuando ejecutemos el algoritmo, se debe añadir un *True* como último argumento en la llamada al constructor. Este modo mostrará información útil del algoritmo por consola, como por ejemplo, tiempo de ejecución, número de nodos creados y visitados y demás características propias de cada uno de los algoritmos. Un ejemplo de como quedaría la creación del algoritmo de MCTS con este argumento extra sería el siguiente:

``` python
  mcts = pyplAI.MCTS(
         Juego.aplica_movimiento,
         Juego.obtiene_movimientos, 
         Juego.es_estado_final, 
         Juego.gana_jugador, 
         numeroJugadores, 
         tiempoEjecucion,
         True)
```

### Ejecución Algoritmo

Una vez tengamos el objeto del algoritmo que se quiere utilizar solamente se debe llamar a su método *ejecuta* y pasarle como argumento el objeto que contiene el estado actual del juego, esto devolverá el mejor movimiento encontrado durante el tiempo de computación dado, para los algoritmos de *Monte Carlo*, o la profundidad de búsqueda, en el caso del algoritmo *minimax*. A continuación, se mostrará el código de ejemplo en el que se usa el algoritmo de *MCTS* para obtener un movimiento y seguidamente aplicarlo al juego, obtiendo así un nuevo estado del juego:

``` python
  def main():
      juego = Juego()
      movimiento = mcts.ejecuta(juego)
      juego = aplica_movimiento(movimiento)
```


En caso de que el estado del juego no tenga ningún movimiento posible para aplicar los algoritmos devolverán *None*, y si solo hay un posible movimiento para aplicar, para ahorrar cálculos innecesarios, se devolverá el único movimiento posible.

Si se tienen dudas sobre como integrar la biblioteca a juegos propios se recomienda ver los juegos del repositorio de *GitHub* ([*pyplAI*](https://github.com/plss12/pyplAI)) como ejemplos de uso. Este repositorio contiene la biblioteca y todos los juegos nombrados en la introducción de este manual, incluyendo las implementaciones de los algoritmos correspondientes con cada uno de ellos.

## Contacto

En caso de tener alguna duda, idea o aportación sobre la biblioteca por favor contactar al siguiente correo: [pepoluis712@gmail.com](mailto:pepoluis712@gmail.com)

## Referencias

<a id="MCTS"></a>
[1] Cameron B. Browne, Edward Powley, Daniel Whitehouse, Simon M. Lucas, Peter I.Cowling, Philipp Rohlfshagen, Stephen Tavener, Diego Perez, Spyridon Samoth-rakis, and Simon Colton. A survey of monte carlo tree search methods. IEEETransactions on Computational Intelligence and AI in Games, 4(1):1–43, 2012. doi:10.1109/TCIAIG.2012.2186810. URL https://ieeexplore.ieee.org/document/6145622.

<a id="Minimax"></a>
[2] Patricio Mendoza. Alpha-beta pruning algorithm: The intelligence behind strategygames. page 9, 2022. URL https://www.researchgate.net/publication/360872512.

<a id="UltimateTicTacToe"></a>
[3] Eytan Lifshitz and David Tsurel. Ai approaches to ultimate tic-tac-toe. page 5, 2013. URL https://www.cs.huji.ac.il/w~ai/projects/2013/UlitmateTic-Tac-Toe/files/report.pdf.

<a id="ISMCTS"></a>
[4] Peter I. Cowling, Edward J. Powley, and Daniel Whitehouse. Information setmonte carlo tree search. IEEE Transactions on Computational Intelligence and AIin Games, 4(2):120–143, 2012. doi: 10.1109/TCIAIG.2012.2200894. URL https://ieeexplore.ieee.org/document/6203567.
