# pyplAI

## Introducción
Esta librería para Python es el resultado final de un TFG centrado en la implementación de algoritmos de MCTS para diferentes tipos de juegos de mesa, entre ellos, según clasifica la teoría de juegos, los juegos de información perfecta como lo son el ajedrez o las damas, en los que en todo momento cualquier jugador puede ver toda la información del juego como los posibles movimientos del rival, y juegos de información imperfecta, como lo son la mayoría de juegos de cartas como por ejemplo el Uno o la brisca, en el que los jugadores solo conocen información propia como sus cartas o información general como el estado de la mesa, pero desconocen la información del rival, como las cartas de los demás jugadores.

Para el primer tipo de juegos de información perfecta se han implementado los algoritmos de MCTS con UCT y MinMax con la técnica de poda de Alfa Beta. Además, como ejemplos para ver el correcto uso de la librería se han creado diferentes juegos para hacer uso de esta como ejemplos, entre ellos, TicTacToe (3 y 4 en raya), Ultimate TicTacToe y las damas.

Para el segundo tipo de juegos de información imperfecta se han implementado dos algoritmos, el SO-ISMCTS (Single Observer) y el MO-ISMCTS (Multiple Observer), el primero de ellos crea un único árbol desde el punto de vista del jugador al que le toca jugar, este algoritmo se puede aplicar a cualquier juego de información imperfecta, el segundo algoritmo crea un árbol por cada jugador y agrupa las acciones indiferenciables desde el punto de vista de este en un mismo nodo, es decir, si un jugador rival puede realizar movimientos los cuales los demás jugadores no reciben información sobre este, agrupa estos movimientos en un único nodo, lo cual lo hace más eficiente en juegos con este tipo de movimientos, un ejemplo de un movimiento así sería cuando un jugador intercambia una de las cartas de su mano con cualquier carta de la baraja, cuando el jugador realiza este intercambio los demás jugadores no reciben ningún tipo de información sobre este intercambio de cartas. Para estos algoritmos también se han creado varios juegos como ejemplos de uso de esta librería, aunque ambos algoritmos se pueden usar en todos los juegos de información imperfecta se ha diferenciado entre juegos para el SO y el MO, para el primero se ha creado la escoba, el Stratego y un pequeño BlackJack, para el segundo se ha creado el Holjjak (Juego de adivinar las canicas del rival), con una mezcla de MCTS, y el Phantom (Especie de 4 en raya, pero con los movimientos en secreto).

## Uso
Para el uso de la librería lo primero sería importarla en el archivo del juego al que queremos implementarla, una vez importada debemos crear una clase la cual contenga el estado del juego y dentro de esta clase se tendrán que implementar los siguientes métodos para el correcto funcionamiento:

**•	Obtiene_movimientos(self):** Obtendrá una lista con todos los movimientos posibles de ese estado de la partida, es recomendable mezclar los movimientos antes de devolverlos.

**•	Aplica_movimiento(self, movimiento):** Aplicará el movimiento dado al estado de la partida y devolverá este nuevo estado resultante.

**•	Es_estado_final(self):**  Comprueba si se ha llegado a un estado final de partida y devuelve True, si no es así, devuelve False.

**•	Gana_jugador(self, jugador):** Comprueba si el jugador dado gana la partida con el estado actual.

Estos 4 métodos serán obligatorios para cada uno de los algoritmos, además los algoritmos SO y MO necesitarán otros métodos adicionales, el primero de ellos es obligatorio para estos dos algoritmos:

**•	Determinación(self):** Dado el estado de la partida, usa la información que tiene el jugador actual del juego (al cual le toca jugar) para crear una determinación aleatoria del estado de la partida, por ejemplo, en el caso de que sea un juego de cartas en el que cada jugador contiene una mano, hay una mesa con cartas visibles, una pila de descartes de cartas que han sido retiradas de la mesa y una pila de robo con cartas que no han sido vistas, este método debe repartir aleatoriamente las cartas que aún no sabe donde están entre las manos de los demás jugadores y la pila de robo, sabiendo que el jugador tiene el conocimiento de las cartas de su mano, la mesa y la pila de descartes.

Además, para el algoritmo MO se necesitará otro método adicional:

**•	Acciones_compatibles():**

También, para el caso de MinMax, necesitamos un método que le de una valoración a la partida dependiendo de como de bueno sea el estado para el jugador dado:

**•	Heurística(self, jugador):** Este método debe devolver una nota que refleje como de bueno es el estado para el jugador dado, por ejemplo, para el juego de las damas una posible heurística sería contar el número de fichas del jugador y restarle el número de fichas del rival. Hay infinitas posibilidades de heurísticas para cada uno de los juegos, y se debe tener un conocimiento sobre el juego para poder crear un método que funcione ya que este tendrá un gran peso en la decisión de cual es el mejor movimiento. Se recomienda realizar una heurística delimitada entre valores no muy altos.

Por último, pero igual de importante, los algoritmos necesitan saber cual es el jugador al cuál le toca jugar en los turnos, para ello es obligatorio crear un atributo **jugadorActual** en la clase del juego, es importante que tenga este mismo nombre para que la librería pueda acceder a este, y debe contener el jugador el cuál le toca jugar en ese turno, empezando por el jugador 1, este jugador se debe actualizar al aplicar movimientos si estos hacen que se cambie con ello, por ejemplo en el caso de las damas, en el método aplica_movimiento antes de devolver el estado de la partida se actualiza el jugadorActual con el jugador rival, al cual le tocaría jugador en el siguiente turno, si el jugadorActual es 1 se pasará el turno al jugador 2, si el jugadorActual es 2 se pasará el turno al jugador 1.

![image](https://user-images.githubusercontent.com/80253708/217592563-b0dfb18e-5087-4172-908c-0cd7919df42e.png)

Una vez tengamos todos estos métodos solamente debemos llamar a la librería y el algoritmo que deseamos utilizar, a esta llamada le pasaremos estos métodos, el número de jugadores del juego y el tiempo de ejecución en segundos para los algoritmos de MCTS y la profundidad de búsqueda para MinMax, vemos los ejemplos a continuación:

**•	MCTS:**

tiempoEjecucion = x (segundos)
numeroJugadores = x

mcts = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
numeroJugadores, 
tiempoEjecucion)

**•	MinMax:**

depth = x (segundos)
numeroJugadores = x

minmax = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
Juego.heuristica,
numeroJugadores, 
depth)

**•	SO-ISMCTS:**

tiempoEjecucion = x (segundos)
numeroJugadores = x

so_ismcts = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
Juego.determinacion,
numeroJugadores, 
tiempoEjecucion)

**•	MO-ISMCTS:**

tiempoEjecucion = x (segundos)
numeroJugadores = x

mo_ismcts = Algoritmos.MCTS(Juego.aplica_movimiento,
Juego.obtiene_movimientos, 
Juego.es_estado_final, 
Juego.gana_jugador, 
Juego.determinacion,
Juego.acciones_compatibles,
numeroJugadores, 
tiempoEjecucion)

Una vez ya tengamos el objeto del algoritmo que queramos utilizar solamente debemos llamar a su método ejecuta y pasarle el objeto de la partida con el estado actual, esto devolverá el movimiento optimo que calcule en el tiempo de computación dado o la profundidad en el caso del minmax. Un ejemplo para el mcts sería así:
movimiento = mcts.ejecuta(juego)
Con este movimiento podemos continuar la partida aplicándolo al estado de esta:
juego = juego.aplica_movimiento(movimiento)
Estas dos líneas nos jugarían un turno completo, obteniendo y aplicando un movimiento.
En caso de no que el estado de la partida no tenga ningún movimiento posible para aplicar, los algoritmos devolverán None, y si solo hay un posible movimiento para aplicar, los algoritmos no calcularán nada y se devolverá el único movimiento posible directamente.

Si se tienen dudas sobre como integrar la librería a vuestros propios juegos se recomienda ver los ejemplos con los diferentes juegos desarrollados.

En caso de tener alguna duda, idea o aportación extra sobre la librería porfavor contactar al correo pepoluis712@gmail.com
