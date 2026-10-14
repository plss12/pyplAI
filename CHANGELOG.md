# Changelog

## 1.1.0

### Algoritmos

- **Compatibilidad:** la biblioteca funciona desde Python 3.9. La versión 1.0.3 solo funcionaba desde Python 3.10, porque llamaba directamente a objetos `staticmethod`, aunque se podía instalar en versiones anteriores.
- **Nuevo método `analiza(estado)`** en los cuatro algoritmos: devuelve un `ResultadoAnalisis` con el movimiento elegido, el ranking de todos los movimientos (visitas y valor), las iteraciones, los nodos y el tiempo. No escribe nada por consola.
- **Nuevos parámetros opcionales** `iteraciones` y `semilla` en MCTS, SO-ISMCTS y MO-ISMCTS, y `seleccion_final` en MCTS (`"media"`, por defecto, o `"visitas"`).
- **SO-ISMCTS y MO-ISMCTS:**
  - El contador de disponibilidad n′ también se incrementa al expandir, como en Cowling, Powley y Whitehouse (2012).
  - La elección final se limita a los movimientos legales del estado real.
- **Minimax:**
  - Las victorias y derrotas tienen valores finitos (±10⁹ ajustados por la profundidad), así que el algoritmo prefiere ganar antes y perder más tarde.
  - `profundidadBusqueda` es ahora el número de jugadas exploradas. En la 1.0.3 se exploraba una más, así que una profundidad d de la 1.0.3 equivale a d + 1 en la 1.1.0.
- **Errores y estados finales:**
  - Un estado no final sin movimientos lanza un `ValueError` con un mensaje claro.
  - `ejecuta` y `analiza` devuelven `None` en estados finales.

### Juegos de ejemplo

- **Tres en raya, Ultimate Tic-Tac-Toe y damas:**
  - Las simulaciones entre algoritmos contaban las victorias del jugador 2 como empates.
  - Tres en raya: la heurística sumaba las líneas con una ficha como si tuvieran dos.
- **Ultimate Tic-Tac-Toe:** un tablero pequeño lleno sin ganador terminaba la partida si se enviaba a él al rival. Ahora se puede jugar en cualquier otro.
- **Damas:**
  - Se ajustan al reglamento de las damas españolas: captura a distancia de la dama, piezas capturadas que se retiran al final de la jugada, leyes de la cantidad y de la calidad, y tablero con la esquina inferior derecha jugable.
  - Las victorias por bloqueo se contaban como empates.
- **Escoba:** se ajusta al reglamento de la Escoba de 15:
  - Reparto de 3 cartas a cada jugador y escoba de muestra.
  - Obligación de llevarse las cartas que suman 15.
  - Recuento de escobas, cartas, oros, setenta y siete de oros; si hay empate en cartas, oros o setenta, no puntúa nadie.
  - Se corrigen la recogida final de cartas, el recuento de sietes y el jugador aleatorio, que jugaba siempre el primer movimiento.
- **BlackJack:**
  - La determinización conservaba la carta tapada real del croupier, así que el algoritmo jugaba viéndola.
  - Un empate con la banca ya no cuenta como victoria.
- **Holjjak:** la fase de esconder canicas usa el algoritmo de información imperfecta en lugar de MCTS, que veía el número escondido.
- **Stratego:**
  - Se usa la mejor colocación del algoritmo genético.
  - La selección por ruleta funciona con fitness 0.

### Proyecto

- Empaquetado con `pyproject.toml`.
- Tests con pytest.
- Integración continua en Ubuntu y Windows con Python 3.9 a 3.13.

## 1.0.3

Versión del Trabajo de Fin de Grado.
