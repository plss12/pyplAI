"""Réplica reducida de los experimentos del capítulo 6 del TFG con pyplAI 1.1.0 y los juegos corregidos.

Cada partida es una fila de resultados.csv. La semilla de cada partida fija el azar de los juegos y
decide quién empieza, que se alterna entre partidas como en el TFG.

Uso:
    python replica.py [--salida resultados.csv] [--procesos 10]
    python replica.py --salida prueba.csv --partidas 2 --factor-tiempo 0.05   # prueba rápida
"""

import argparse
import contextlib
import csv
import io
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COLUMNAS = ["juego", "agente", "rival", "tiempo", "profundidad_tfg", "jugadores", "semilla", "ganador", "monedas", "jugadas", "segundos"]

# MCTS contra Minimax: MCTS recibe el tiempo medio por jugada de minimax medido en el TFG (sección 6.1).
# En la 1.0.3 una profundidad d exploraba d + 1 jugadas, así que aquí se usa d + 1.
MINIMAX = {
    "tictactoe": {3: (0.06, 100), 4: (0.14, 100), 5: (0.23, 100), 6: (0.8, 100)},
    "ultimate": {2: (0.25, 40), 3: (0.79, 40), 4: (4.02, 12)},
    "damas": {2: (0.15, 24), 3: (0.32, 24), 4: (0.85, 24), 5: (1.77, 24)},
}
CLASES = {"tictactoe": "TicTacToe", "ultimate": "UltimateTTT", "damas": "Damas", "phantom": "Phantom", "holjjak": "Holjjak"}


def cargar(nombre):
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "tests"))
    from utilidades import cargar_juego

    return cargar_juego(nombre)


def aleatorio(obtener_movimientos):
    return lambda estado: random.choice(obtener_movimientos(estado))


def jugar(estado, agentes, es_final, aplicar):
    """Juega hasta el final. agentes: {1: agente, 2: agente}. Devuelve el estado final y las jugadas."""
    jugadas = 0
    while not es_final(estado):
        estado = aplicar(estado, agentes[estado.jugadorActual](estado))
        jugadas += 1
    return estado, jugadas


def ganador(estado):
    return 1 if estado.gana_jugador(1) else 2 if estado.gana_jugador(2) else 0


def partida(tarea):
    """Juega una partida y devuelve su fila del CSV."""
    import pyplAI

    juego, agente, rival, tiempo, extra, semilla = tarea
    random.seed(semilla)
    fila = dict.fromkeys(COLUMNAS, "")
    fila.update(juego=juego, agente=agente, rival=rival, tiempo=tiempo, semilla=semilla, **extra)
    lado = 1 + semilla % 2  # lado del agente: se alterna quién empieza
    t0 = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        if rival == "minimax":
            C = getattr(cargar(juego), CLASES[juego])
            minimax = pyplAI.Minimax(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.heuristica, 2, extra["profundidad_tfg"] + 1)
            mcts = pyplAI.MCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, 2, tiempo)
            estado = C(100) if juego == "damas" else C()
            final, jugadas = jugar(estado, {lado: mcts.ejecuta, 3 - lado: minimax.ejecuta}, C.es_estado_final, C.aplica_movimiento)
            g = final.ganador()
            fila.update(ganador="empate" if g == 0 else "mcts" if g == lado else "minimax", jugadas=jugadas)

        elif juego in ("phantom", "holjjak"):
            C = getattr(cargar(juego), CLASES[juego])

            def crear(nombre):
                if nombre == "mo-ismcts":
                    return pyplAI.MOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, C.accion_visible, 2, tiempo).ejecuta
                if nombre == "so-ismcts":
                    return pyplAI.SOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, 2, tiempo).ejecuta
                return aleatorio(C.obtiene_movimientos)

            final, jugadas = jugar(C(), {lado: crear(agente), 3 - lado: crear(rival)}, C.es_estado_final, C.aplica_movimiento)
            g = ganador(final)
            fila.update(ganador="empate" if g == 0 else agente if g == lado else rival, jugadas=jugadas)

        elif juego == "escoba":
            E = cargar("escoba").Escoba
            n = extra["jugadores"]
            con_so = 1 if n == 2 else 2
            so = pyplAI.SOISMCTS(E.aplicarMovimiento, E.obtieneMovimientos, E.esEstadoFinal, E.ganaJugador, E.determinization, n, tiempo)
            # Los asientos de SO-ISMCTS rotan con la semilla; con 4 jugadores son asientos opuestos
            asientos = {((semilla + k * (n // con_so)) % n) + 1 for k in range(con_so)}
            estado = E(n, False)
            while not estado.esEstadoFinal():
                agente_turno = so.ejecuta if estado.jugadorActual in asientos else aleatorio(E.obtieneMovimientos)
                estado.aplicarMovimiento(agente_turno(estado))
            ganadores = estado.finalPartida()
            de_so = sum(1 for g in ganadores if g in asientos)
            de_aleatorio = len(ganadores) - de_so
            fila.update(ganador="so-ismcts" if de_so > de_aleatorio else "aleatorio" if de_aleatorio > de_so else "empate")

        elif juego == "blackjack":
            B = cargar("blackjack").BlackJack
            p = B(100)
            so = pyplAI.SOISMCTS(B.aplica_accion, B.posibles_acciones, B.es_estado_final_ronda, B.gana_jugador_ronda, B.determinization, 2, tiempo) if agente == "so-ismcts" else None
            while not p.es_estado_final():
                p.comprobarNuevaRonda()
                if not p.iniciarRonda:
                    p.rondaMCTS(so) if so else p.rondaPrueba()
            fila.update(monedas=p.jugador.creditos - p.jugador.creditosIniciales)

        elif juego == "stratego":
            m = cargar("stratego")
            S = m.Stratego
            colocacion = m.posicionFichasAlgoritmoGenetico()
            so_ag = pyplAI.SOISMCTS(S.aplica_movimiento, S.obtiene_movimientos, S.es_estado_final, S.gana_jugador, S.determinization, 2, tiempo)
            if rival == "so-ismcts":
                otro = pyplAI.SOISMCTS(S.aplica_movimiento, S.obtiene_movimientos, S.es_estado_final, S.gana_jugador, S.determinization, 2, tiempo).ejecuta
            else:
                otro = aleatorio(S.obtiene_movimientos)
            estado = S(500, colocacion, None) if lado == 1 else S(500, None, colocacion)
            final, jugadas = jugar(estado, {lado: so_ag.ejecuta, 3 - lado: otro}, S.es_estado_final, S.aplica_movimiento)
            g = ganador(final)
            fila.update(ganador="empate" if g == 0 else agente if g == lado else rival, jugadas=jugadas)
    fila["segundos"] = round(time.perf_counter() - t0, 2)
    return fila


def tareas(limite, factor):
    """(juego, agente, rival, tiempo, extra, partidas) de cada configuración, de la más larga a la más corta."""
    configuraciones = []
    for juego in ("damas", "ultimate", "tictactoe"):
        for d, (t, n) in sorted(MINIMAX[juego].items(), reverse=True):
            configuraciones.append((juego, "mcts", "minimax", t, {"profundidad_tfg": d}, n))
    configuraciones += [("stratego", "so-ismcts+ag", "aleatorio", t, {}, 20) for t in (0.5, 1)]
    configuraciones += [("stratego", "so-ismcts+ag", "so-ismcts", 0.5, {}, 20)]
    configuraciones += [("escoba", "so-ismcts", "aleatorio", t, {"jugadores": 2}, 60) for t in (0.25, 0.5, 1, 2)]
    configuraciones += [("escoba", "so-ismcts", "aleatorio", 0.5, {"jugadores": 4}, 60)]
    configuraciones += [("blackjack", "so-ismcts", "croupier", t, {}, 40) for t in (0.25, 1)]
    configuraciones += [("blackjack", "aleatorio", "croupier", "", {}, 100)]
    for t in (0.25, 1):
        configuraciones += [("phantom", "mo-ismcts", "aleatorio", t, {}, 60), ("holjjak", "mo-ismcts", "aleatorio", t, {}, 60), ("holjjak", "mo-ismcts", "so-ismcts", t, {}, 60)]
    configuraciones += [("phantom", "mo-ismcts", "so-ismcts", t, {}, 60) for t in (0.5, 2)]
    for juego, agente, rival, t, extra, n in configuraciones:
        tiempo = round(t * factor, 4) if t != "" else ""
        for semilla in range(min(n, limite) if limite else n):
            yield (juego, agente, rival, tiempo, extra, semilla)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--salida", default="resultados.csv")
    parser.add_argument("--procesos", type=int, default=10)
    parser.add_argument("--partidas", type=int, default=0, help="Máximo de partidas por configuración (0 = las de la réplica).")
    parser.add_argument("--factor-tiempo", type=float, default=1.0, help="Multiplica los tiempos de búsqueda, para pruebas rápidas.")
    args = parser.parse_args()
    nuevo = not Path(args.salida).exists()
    with mp.Pool(args.procesos) as pool, open(args.salida, "a", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, COLUMNAS, lineterminator="\n")
        if nuevo:
            escritor.writeheader()
        for fila in pool.imap_unordered(partida, tareas(args.partidas, args.factor_tiempo)):
            escritor.writerow(fila)
            f.flush()
            print(fila["juego"], fila["agente"], fila["rival"], fila["tiempo"], fila["ganador"] or fila["monedas"], flush=True)


if __name__ == "__main__":
    main()
