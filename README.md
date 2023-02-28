# pyplAI

## Introducción
Esta librería para Python es el resultado final de un TFG centrado en la implementación de algoritmos de MCTS para diferentes tipos de juegos de mesa, entre ellos, según clasifica la teoría de juegos, los juegos de información perfecta como lo son el ajedrez o las damas, en los que en todo momento cualquier jugador puede ver toda la información del juego como los posibles movimientos del rival, y juegos de información imperfecta, como lo son la mayoría de juegos de cartas como por ejemplo el Uno o la brisca, en el que los jugadores solo conocen información propia como sus cartas o información general como el estado de la mesa, pero desconocen la información del rival, como las cartas de los demás jugadores.

### Juegos de Información Perfecta

Para el primer tipo de juegos de información perfecta se han implementado los algoritmos de MCTS con UCT y MinMax con la técnica de poda de Alfa Beta. Además, como ejemplos para ver el correcto uso de la librería, se han creado diferentes juegos para hacer uso de esta como ejemplos, entre ellos, TicTacToe (3 en raya), Ultimate TicTacToe y las damas.

### Juegos de Información Imperfecta

Para el segundo tipo de juegos de información imperfecta se han implementado dos algoritmos, el SO-ISMCTS (Single Observer) y el MO-ISMCTS (Multiple Observer), el primero de ellos genera un único árbol desde el punto de vista del jugador al que le toca jugar y el segundo algoritmo crea un árbol por cada jugador y agrupa las acciones indiferenciables desde el punto de vista de este en un mismo nodo, es decir, si un jugador rival puede realizar movimientos los cuales para los demás jugadores no se recibe nueva información sobre el estado de la partida, agrupa estos movimientos en un único nodo.

Un ejemplo serían los juegos en los que un jugador intercambia una de las cartas de su mano con cualquier carta de la baraja, cuando el jugador efectúa este intercambio los demás jugadores no reciben ningún tipo de información sobre este intercambio de cartas, por lo que su conocimiento sobre el estado de la partida no cambia. 

Para estos algoritmos también se han desarrollado varios juegos como ejemplos de uso de esta librería, aunque ambos algoritmos se pueden usar en todos los juegos de información imperfecta, se ha diferenciado entre juegos para el SO y el MO, para el primero se ha creado la escoba, el Stratego y el BlackJack, para el segundo se ha creado el Holjjak (Juego de adivinar las canicas del rival) y el Phantom (Especie de 4 en raya, pero con los movimientos en secreto).

## Manual de Uso
Lo primero de todo, se debe importar la librería en el archivo de python del juego al que queremos implementarla, es imprescindible que haya una clase que guarde la información necesaria sobre el estado del juego, además esta clase deberá implementar los siguientes métodos (puedes llamar a estos métodos de forma diferente a lo que se muestra, pero deben contener las mismas variables):

### Métodos Generales

Los siguientes 4 métodos serán obligatorios para todos los algoritmos que se implementan en esta biblioteca.

**•	Obtiene_movimientos(self):** Obtendrá una lista con todos los movimientos posibles de ese estado de la partida, es recomendable mezclar los movimientos antes de devolverlos con alguna función de la biblioteca "random".

**•	Aplica_movimiento(self, movimiento):** Aplicará el movimiento dado al estado de la partida y devolverá este nuevo estado resultante (return self).

**•	Es_estado_final(self):** Comprueba si se ha llegado a un estado final de partida y si es así, devuelve True, si no, devuelve False.

**•	Gana_jugador(self, jugador):** Comprueba si el jugador dado gana la partida con el estado actual y si es así, devuelve True, si no, devuelve False. La variable jugador debe ser un número entero, empezando por 1 para el primer jugador hasta n para el número de jugadores que contiene la partida.

### Métodos SO/MO-ISMCTS

Además de los 4 métodos anteriores, los algoritmos de SO-ISMCTS y MO-ISMCTS necesitan un método adicional para su uso, el cual se explica a continuación:

**•	Determinación(self):** Devuelve una determinación aleatoria del estado de la partida, usando la información que sabe el jugador actual de la partida (el que tiene el turno de juego).

Por ejemplo, en el caso de que sea un juego de cartas en el que cada jugador tiene una mano, hay una mesa con cartas visibles, una pila de descartes con las cartas jugadas y un mazo de robo inicial, en este caso el jugador actual no tiene conocimiento sobre las cartas del rival ni las cartas del mazo de robo, pero si sabe cuáles son sus cartas, las de la mesa y las que han sido mandadas a la pila de descartes, por lo que tiene la información sobre el conjunto de cartas restantes que aún no sabe donde se encuentran. 

Con esta información, este método debe dar un estado de la partida en el que aleatoriamente se dividan las cartas que el jugador no sabe donde se encuentran entre las zonas en las que no sabe qué cartas hay, en este caso las manos de los rivales y el mazo de robo.

### Métodos MO-ISMCTS

Además, para el funcionamiento del algoritmo MO-ISMCTS se necesitará otro método adicional más:

**•	Accion_visible(accion):** Este método, dado una acción, devuelve True si es una acción la cual actualiza la información del estado de la partida a los rivales, si no da información a los rivales devuelve False.

Por ejemplo, una acción que da o actualiza información sobre el estado de la partida sería jugar una carta de tu mano a la mesa siendo vista por los demás jugadores, esta acción haría saber a los demás jugadores el lugar exacto de esa carta, cosa que antes no sabían. Sin embargo, una acción no visible sería intercambiar una carta de tu mano con el mazo de robo, esta acción no mostraría nueva información a ningún rival, ya que no se muestran las cartas y los rivales seguirán sin saber qué cartas tienes en la mano ni que cartas hay el mazo de robo.

### Métodos MinMax

En cuanto a métodos, por último, para el caso del algoritmo de MinMax, además de los 4 métodos generales, se necesita un método evalúe el estado de la partida para saber como de bueno es desde el punto de vista de un jugador dado:

**•	Heurística(self, jugador):** Este método debe devolver una nota que refleje como de bueno es el estado para el jugador dado.

Por ejemplo, para el juego de las damas una posible heurística sería contar el número de fichas del jugador y restarle el número de fichas del rival. Hay infinitas posibilidades de heurísticas para cada uno de los juegos, y se debe tener un conocimiento sobre el juego para poder crear un método que funcione, ya que este tendrá un gran peso en la decisión de cuál es el mejor movimiento. Se recomienda realizar una heurística delimitada entre valores no muy altos.

Al igual que en el método gana_jugador, la variable jugador debe ser un número entero, empezando por 1 para el primer jugador hasta n para el número de jugadores que contiene la partida.

### Atributos Generales Obligatorios

Por último, los algoritmos necesitan saber cuál es el jugador al cual le toca jugar en cada uno de los turnos, para ello es obligatorio añadir un atributo **jugadorActual** en la clase del juego, es importante que tenga este mismo nombre para que la librería pueda acceder a este sin problemas.

Este atributo debe ser un valor numérico y debe contener el jugador el cual le toca jugar en ese turno, empezando por el jugador 1. Este atributo debe ir actualizándose conforme se avance en el juego, por ejemplo, en el juego del 3 en raya, este atributo se debe iniciar con el valor 1, pero cuando el primer jugador realice su movimiento, este se deberá actualizar con el valor 2, indicando que es el segundo jugador el cual debe realizar su jugada.

![image](https://user-images.githubusercontent.com/80253708/217592563-b0dfb18e-5087-4172-908c-0cd7919df42e.png)

### Creación Objeto

Una vez tengamos todos estos métodos solamente debemos llamar a la librería y el algoritmo que deseamos utilizar, a esta llamada le pasaremos los métodos necesarios para el uso de este algoritmo, el número de jugadores del juego y el tiempo de ejecución en segundos para los algoritmos de MCTS y la profundidad de búsqueda para MinMax, todo esto en el orden indicado que veremos a continuación:

Juego será el nombre de la clase la cual contiene los métodos y el estado de la partida, incluido el atributo jugadorActual.

**•	MCTS:**

numeroJugadores = int (Número de jugadores de la partida)

tiempoEjecucion = int (Segundos de computación del algoritmo)

mcts = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
numeroJugadores, 
tiempoEjecucion)

**•	MinMax:**

numeroJugadores = int (Número de jugadores de la partida)

depth = int (Profundidad de jugadas calculadas por el algoritmo)

minmax = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
Juego.heuristica,
numeroJugadores, 
depth)

**•	SO-ISMCTS:**

numeroJugadores = int (Número de jugadores de la partida)

tiempoEjecucion = int (Segundos de computación del algoritmo)

so_ismcts = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
Juego.determinacion,
numeroJugadores, 
tiempoEjecucion)

**•	MO-ISMCTS:**

numeroJugadores = int (Número de jugadores de la partida)

tiempoEjecucion = int (Segundos de computación del algoritmo)

mo_ismcts = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
Juego.determinacion,
Juego.accion_visible,
numeroJugadores, 
tiempoEjecucion)

### Llamada Objeto

Una vez ya tengamos el objeto del algoritmo que queramos utilizar solamente debemos llamar a su método **ejecuta** y pasarle el objeto de la partida con el estado actual, esto devolverá el movimiento óptimo que calcule en el tiempo de computación dado o la profundidad en el caso del minmax. Un ejemplo para el algoritmo de mcts sería así:

movimiento = mcts.ejecuta(juego)

Con este movimiento podemos continuar la partida aplicándolo y actualizando el estado de esta:

juego = juego.aplica_movimiento(movimiento)

Estas dos líneas nos jugarían un turno completo, obteniendo un movimiento y aplicandolo al estado de la partida.

En caso de que el estado de la partida no tenga ningún movimiento posible para aplicar, los algoritmos devolverán None, y si solo hay un posible movimiento para aplicar, para ahorrar cálculos innecesarios, se devolverá el único movimiento posible directamente.

Si se tienen dudas sobre como integrar la librería a vuestros propios juegos, se recomienda ver los ejemplos con los diferentes juegos desarrollados.

## Contacto

En caso de tener alguna duda, idea o aportación extra sobre la librería por favor contactar al correo pepoluis712@gmail.com
