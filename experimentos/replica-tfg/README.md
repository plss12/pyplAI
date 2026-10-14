# Réplica de los experimentos del TFG con pyplAI 1.1.0

Repetición reducida de las pruebas del capítulo 6 del TFG con la biblioteca y los juegos
corregidos en la versión 1.1.0. Sirve para comprobar qué conclusiones del TFG se mantienen tras
las correcciones. Los PDF del TFG no se modifican: son el trabajo entregado.

## Metodología

- Mismas configuraciones que el TFG: mismos rivales y tiempos de cálculo por jugada, y se alterna
  el jugador que empieza.
- Menos partidas por configuración (entre 12 y 100, frente a 100 en el TFG), así que cada
  porcentaje va con su intervalo de confianza del 95 % (Wilson).
- **Minimax frente a MCTS:**
  - MCTS recibe el tiempo medio de minimax medido en el TFG (tablas de la sección 6.1).
  - En la 1.0.3 una profundidad d exploraba d + 1 jugadas, así que la profundidad d del TFG se
    ejecuta como d + 1 en la 1.1.0.
  - Las damas se juegan con un límite de 100 turnos.
- **Stratego:** límite de 500 turnos, como en el TFG.
- **Ejecución:** el mismo portátil que el TFG (i7-12700H), con 10 procesos en paralelo. El
  recuento de iteraciones se midió aparte, con un único proceso y sin carga.

| Archivo | Contenido |
| --- | --- |
| `replica.py` | Experimentos de información imperfecta y una primera pasada de minimax frente a MCTS con tiempos calibrados contra un agente aleatorio. Se descartó porque esos tiempos son mucho menores que los del TFG. |
| `replica_tfg.py` | Minimax frente a MCTS con los tiempos del TFG. |
| `iteraciones.py`, `iteraciones_103.py` | Iteraciones por segundo de SO-ISMCTS y MO-ISMCTS con la 1.1.0 y con la 1.0.3 y los juegos originales (`git archive d4b5743 Juegos`). |
| `resultados.jsonl`, `resultados_tiempos_tfg.jsonl`, `iteraciones.txt` | Resultados en bruto. |
| `resumen.py` | Genera las tablas a partir de los resultados. |

```bash
python replica.py <ruta del repo> resultados.jsonl 10
python replica_tfg.py <ruta del repo> resultados_tiempos_tfg.jsonl 10
python resumen.py resultados.jsonl
```

## Resultados

Porcentajes de victorias, derrotas y empates. Entre corchetes, el intervalo de confianza del 95 %
de las victorias del algoritmo evaluado.

### Minimax frente a MCTS (MCTS / minimax / empates)

| Juego | Profundidad TFG | TFG | Réplica 1.1.0 | Partidas |
| --- | --- | --- | --- | --- |
| Tres en raya | 3 | 25 / 7 / 68 | 0 / 2 / 98 | 100 |
| Tres en raya | 4 | 28 / 3 / 69 | 0 / 1 / 99 | 100 |
| Tres en raya | 5 | 0 / 3 / 97 | 0 / 0 / 100 | 100 |
| Tres en raya | 6 | 0 / 0 / 100 | 0 / 0 / 100 | 100 |
| Ultimate | 2 | 12 / 40 / 48 | 25 / 62 [47-76] / 12 | 40 |
| Ultimate | 3 | 7 / 39 / 54 | 35 / 45 [31-60] / 20 | 40 |
| Ultimate | 4 | 20 / 24 / 30 | 58 / 42 [19-68] / 0 | 12 |
| Damas | 2 | 5 / 43 / 52 | 71 / 17 [7-36] / 12 | 24 |
| Damas | 3 | 9 / 33 / 58 | 25 / 29 [15-49] / 46 | 24 |
| Damas | 4 | 8 / 30 / 62 | 46 / 21 [9-40] / 33 | 24 |
| Damas | 5 | 15 / 32 / 53 | 38 / 8 [2-26] / 54 | 24 |

### SO-ISMCTS

| Prueba | Tiempo | TFG (victorias / derrotas / empates) | Réplica 1.1.0 | Partidas |
| --- | --- | --- | --- | --- |
| Escoba, contra aleatorio | 0,25 s | 65 / 19 / 16 | 78 [66-87] / 18 / 3 | 60 |
| Escoba, contra aleatorio | 0,5 s | 73 / 13 / 14 | 85 [74-92] / 8 / 7 | 60 |
| Escoba, contra aleatorio | 1 s | 73 / 12 / 15 | 92 [82-96] / 8 / 0 | 60 |
| Escoba, contra aleatorio | 2 s | 77 / 12 / 11 | 90 [80-95] / 7 / 3 | 60 |
| Escoba, 2 SO-ISMCTS contra 2 aleatorios | 0,5 s | 64 / 27 / 9 | 78 [66-87] / 17 / 5 | 60 |
| Stratego, SO-ISMCTS + AG contra aleatorio | 0,5 s | 50 / 1 / 49 | 55 [34-74] / 0 / 45 | 20 |
| Stratego, SO-ISMCTS + AG contra aleatorio | 1 s | 55 / 1 / 44 | 60 [39-78] / 0 / 40 | 20 |
| Stratego, SO-ISMCTS + AG contra SO-ISMCTS | 0,5 s | 43 / 7 / 50 | 55 [34-74] / 5 / 40 | 20 |

| Blackjack (monedas ganadas por partida, de media) | TFG | Réplica 1.1.0 | Partidas |
| --- | --- | --- | --- |
| SO-ISMCTS, 0,25 s | −6,59 | −8,97 (error típico 2,30) | 40 |
| SO-ISMCTS, 1 s | −5,60 | −10,75 (error típico 3,39) | 40 |
| Agente aleatorio | −28,58 | −28,84 (error típico 1,48) | 100 |

### MO-ISMCTS

| Prueba | Tiempo | TFG (victorias / derrotas / empates) | Réplica 1.1.0 | Partidas |
| --- | --- | --- | --- | --- |
| Phantom, contra aleatorio | 0,25 s | 76 / 3 / 21 | 80 [68-88] / 2 / 18 | 60 |
| Phantom, contra aleatorio | 1 s | 87 / 0 / 13 | 85 [74-92] / 2 / 13 | 60 |
| Phantom, contra SO-ISMCTS | 0,5 s | 32 / 37 / 31 | 40 [29-53] / 23 / 37 | 60 |
| Phantom, contra SO-ISMCTS | 2 s | 30 / 30 / 40 | 33 [23-46] / 23 / 43 | 60 |
| Holjjak, contra aleatorio | 0,25 s | 60 / 40 / 0 | 65 [52-76] / 35 / 0 | 60 |
| Holjjak, contra aleatorio | 1 s | 59 / 41 / 0 | 67 [54-77] / 33 / 0 | 60 |
| Holjjak, contra SO-ISMCTS | 0,25 s | 44 / 56 / 0 | 87 [76-93] / 13 / 0 | 60 |
| Holjjak, contra SO-ISMCTS | 1 s | 48 / 52 / 0 | 83 [72-91] / 17 / 0 | 60 |

| Iteraciones de SO-ISMCTS respecto a MO-ISMCTS en el mismo tiempo (1 s, 20 posiciones) | 1.0.3 | 1.1.0 |
| --- | --- | --- |
| Phantom | +10 % (entre −1 % y +26 %) | +9 % (entre −5 % y +21 %) |
| Holjjak | −23 % | −25 % |

## Conclusiones

- **Se mantiene:**
  - SO-ISMCTS gana con claridad a agentes aleatorios. En la Escoba gana incluso más que en el
    TFG.
  - Con las colocaciones del algoritmo genético, SO-ISMCTS gana con claridad a SO-ISMCTS con
    colocaciones aleatorias en Stratego: 55 % frente a 5 %.
  - MO-ISMCTS es claramente superior a un agente aleatorio.
  - En Blackjack, SO-ISMCTS pierde mucho menos que un agente aleatorio.
- **Cambia:**
  - **MO-ISMCTS frente a SO-ISMCTS.** Ahora MO-ISMCTS supera a SO-ISMCTS en los dos juegos, ya
    no solo los iguala. En Holjjak la diferencia es grande (83-87 % de victorias) porque antes
    las dos variantes usaban MCTS para esconder canicas.
  - **Iteraciones.** Lo que dice el TFG («entre un 15 % y un 30 % más» en Phantom) no se
    reproduce ni con el código original en este equipo: es alrededor de un 10 % de media, con
    posiciones de hasta un 26 %. En Holjjak, SO-ISMCTS hace menos iteraciones.
  - **Minimax frente a MCTS:**
    - En Ultimate se mantiene la tendencia: minimax gana con poco tiempo (62 % frente a 25 %) y la
      ventaja se reduce al dar más tiempo, hasta invertirse con la profundidad 4, con pocas
      partidas.
    - En las damas cambia: con los tiempos del TFG, MCTS gana o empata. El generador de
      movimientos nuevo es mucho más rápido y MCTS hace muchas más simulaciones en el mismo
      tiempo, así que esos tiempos ya no equilibran los dos algoritmos.
    - En el tres en raya, prácticamente todo son empates, que es el resultado esperado entre dos
      jugadores que no cometen errores. Las victorias de MCTS del TFG (25-28 %) no se reproducen.
  - **Blackjack.** SO-ISMCTS pierde algo más que en el TFG, donde veía la carta tapada del
    croupier.
