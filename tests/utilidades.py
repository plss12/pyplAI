"""Juegos mínimos y utilidades compartidas por los tests."""

import importlib.util
import sys
from pathlib import Path

JUEGOS = Path(__file__).resolve().parent.parent / "Juegos"
RUTAS = {
    "tictactoe": "Minimax-MCTS/Tic-Tac-Toe.py",
    "ultimate": "Minimax-MCTS/Ultimate Tic-Tac-Toe.py",
    "damas": "Minimax-MCTS/Damas.py",
    "phantom": "SO-MO-ISMCTS/MO/Phantom.py",
    "holjjak": "SO-MO-ISMCTS/MO/Holjjak.py",
    "escoba": "SO-MO-ISMCTS/SO/Escoba.py",
    "blackjack": "SO-MO-ISMCTS/SO/BlackJack.py",
    "stratego": "SO-MO-ISMCTS/SO/Stratego.py",
}


def cargar_juego(nombre):
    """Importa uno de los juegos de ejemplo de Juegos/ como módulo."""
    modulo = "juego_" + nombre
    if modulo not in sys.modules:
        spec = importlib.util.spec_from_file_location(modulo, JUEGOS / RUTAS[nombre])
        sys.modules[modulo] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[modulo])
    return sys.modules[modulo]


class TresEnRaya:
    """Tres en raya con movimientos en orden fijo, para tests deterministas."""

    jugadores = 2

    def __init__(self, tablero=None, jugadorActual=1):
        self.tablero = [fila[:] for fila in tablero] if tablero else [[0] * 3 for _ in range(3)]
        self.jugadorActual = jugadorActual

    def obtiene_movimientos(self):
        if self.gana_jugador(1) or self.gana_jugador(2):
            return []
        return [(i, j) for i in range(3) for j in range(3) if self.tablero[i][j] == 0]

    def aplica_movimiento(self, mov):
        self.tablero[mov[0]][mov[1]] = self.jugadorActual
        self.jugadorActual = 3 - self.jugadorActual
        return self

    def gana_jugador(self, jugador):
        t = self.tablero
        lineas = [t[0], t[1], t[2], [t[0][0], t[1][0], t[2][0]], [t[0][1], t[1][1], t[2][1]],
                  [t[0][2], t[1][2], t[2][2]], [t[0][0], t[1][1], t[2][2]], [t[0][2], t[1][1], t[2][0]]]
        return any(linea == [jugador] * 3 for linea in lineas)

    def es_estado_final(self):
        return len(self.obtiene_movimientos()) == 0

    def heuristica(self, jugador):
        return 0

    def determinization(self):
        return TresEnRaya(self.tablero, self.jugadorActual)

    @staticmethod
    def accion_visible(accion):
        return True


def algoritmos_tres_en_raya(pyplAI, iteraciones=3000, profundidad=9, semilla=1):
    """Los cuatro algoritmos configurados sobre TresEnRaya."""
    T = TresEnRaya
    return {
        "MCTS": pyplAI.MCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador,
                            2, 1, iteraciones=iteraciones, semilla=semilla),
        "Minimax": pyplAI.Minimax(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador,
                                  T.heuristica, 2, profundidad),
        "SOISMCTS": pyplAI.SOISMCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador,
                                    T.determinization, 2, 1, iteraciones=iteraciones, semilla=semilla),
        "MOISMCTS": pyplAI.MOISMCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador,
                                    T.determinization, T.accion_visible, 2, 1, iteraciones=iteraciones,
                                    semilla=semilla),
    }
