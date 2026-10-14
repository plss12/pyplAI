"""Réplica reducida de los experimentos del TFG (capítulo 6) con pyplAI 1.1.0 y los juegos corregidos.

Uso: python replica.py <repo pyplAI> <salida.jsonl> [procesos]
"""
import contextlib
import io
import json
import multiprocessing as mp
import random
import statistics
import sys
import time

REPO = None
CLASES = {"tictactoe": "TicTacToe", "ultimate": "UltimateTTT", "damas": "Damas"}


def preparar(repo):
    global REPO
    REPO = repo
    sys.path.insert(0, repo)
    sys.path.insert(0, repo + "/tests")


def juego(nombre):
    from utilidades import cargar_juego
    return cargar_juego(nombre)


# ---------------------------------------------------------------- agentes


class Medido:
    """Envuelve un algoritmo para medir tiempos e iteraciones por jugada."""
    def __init__(self, alg):
        self.alg, self.tiempos, self.iteraciones = alg, [], []

    def __call__(self, estado):
        t0 = time.perf_counter()
        movs = self.alg.obtener_movimientos(estado)
        if len(movs) == 1:
            mov = movs[0]
        elif hasattr(self.alg, "presupuesto"):
            r = self.alg.analiza(estado)
            self.iteraciones.append(r.iteraciones)
            mov = r.movimiento
        else:
            mov = self.alg.ejecuta(estado)
        self.tiempos.append(time.perf_counter() - t0)
        return mov


def aleatorio(obtener):
    return lambda estado: random.choice(obtener(estado))


def crear(nombre, tipo, valor):
    import pyplAI
    m = juego(nombre)
    if nombre in ("tictactoe", "ultimate", "damas"):
        C = getattr(m, CLASES[nombre])
        if tipo == "minimax":
            return Medido(pyplAI.Minimax(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.heuristica, 2, valor))
        if tipo == "mcts":
            return Medido(pyplAI.MCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, 2, valor))
        return aleatorio(C.obtiene_movimientos)
    if nombre in ("phantom", "holjjak"):
        C = m.Phantom if nombre == "phantom" else m.Holjjak
        if tipo == "so":
            return Medido(pyplAI.SOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, 2, valor))
        if tipo == "mo":
            return Medido(pyplAI.MOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, C.accion_visible, 2, valor))
        return aleatorio(C.obtiene_movimientos)
    if nombre == "escoba":
        C = m.Escoba
        if tipo == "so":
            return Medido(pyplAI.SOISMCTS(C.aplicarMovimiento, C.obtieneMovimientos, C.esEstadoFinal, C.ganaJugador, C.determinization, valor[1], valor[0]))
        return aleatorio(C.obtieneMovimientos)
    if nombre == "stratego":
        C = m.Stratego
        if tipo == "so":
            return Medido(pyplAI.SOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, 2, valor))
        return aleatorio(C.obtiene_movimientos)
    raise ValueError(nombre)


# ---------------------------------------------------------------- partidas


def partida_dos(nombre, estado, agentes, es_final, aplicar, ganador):
    """agentes: {1: agente, 2: agente}. Devuelve el jugador ganador o 0."""
    jugadas = 0
    while not es_final(estado):
        estado = aplicar(estado, agentes[estado.jugadorActual](estado))
        jugadas += 1
    return ganador(estado), jugadas


def tarea(args):
    repo, exp, config, semilla = args
    preparar(repo)
    random.seed(semilla)
    t0 = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        res = ejecutar(exp, config, semilla)
    res.update(exp=exp, config=config, semilla=semilla, segundos=round(time.perf_counter() - t0, 2))
    return res


def ejecutar(exp, c, semilla):
    m = None
    if exp in ("calibracion", "mcts_vs_minimax"):
        nombre = c["juego"]
        m = juego(nombre)
        C = getattr(m, CLASES[nombre])
        nuevo = (lambda: C(c["turnos"])) if nombre == "damas" else C
        mm = crear(nombre, "minimax", c["profundidad"])
        otro = crear(nombre, "mcts", c["tiempo"]) if exp == "mcts_vs_minimax" else crear(nombre, "aleatorio", None)
        #Se alterna quién juega primero (en damas empieza el jugador 2)
        a_minimax = 1 + semilla % 2
        agentes = {a_minimax: mm, 3 - a_minimax: otro}
        g, jugadas = partida_dos(nombre, nuevo(), agentes, C.es_estado_final, C.aplica_movimiento, C.ganador)
        etiqueta = "empate" if g == 0 else ("minimax" if g == a_minimax else ("mcts" if exp == "mcts_vs_minimax" else "aleatorio"))
        return {"resultado": etiqueta, "jugadas": jugadas, "tiempos_minimax": mm.tiempos}

    if exp in ("phantom", "holjjak"):
        m = juego(exp)
        C = m.Phantom if exp == "phantom" else m.Holjjak
        a = crear(exp, c["a"], c["tiempo"])
        b = crear(exp, c["b"], c["tiempo"])
        lado_a = 1 + semilla % 2
        g, jugadas = partida_dos(exp, C(), {lado_a: a, 3 - lado_a: b}, C.es_estado_final, C.aplica_movimiento,
                                 lambda s: 1 if s.gana_jugador(1) else (2 if s.gana_jugador(2) else 0))
        etiqueta = "empate" if g == 0 else (c["a"] if g == lado_a else c["b"])
        return {"resultado": etiqueta, "jugadas": jugadas,
                "iter_a": getattr(a, "iteraciones", []), "iter_b": getattr(b, "iteraciones", [])}

    if exp == "escoba":
        C = juego("escoba").Escoba
        n = c["jugadores"]
        so = crear("escoba", "so", (c["tiempo"], n))
        #Los asientos del SO-ISMCTS rotan con la semilla
        asientos_so = {((semilla + k * (n // c["so"])) % n) + 1 for k in range(c["so"])}
        estado = C(n, False)
        alea = crear("escoba", "aleatorio", None)
        while not estado.esEstadoFinal():
            agente = so if estado.jugadorActual in asientos_so else alea
            estado.aplicarMovimiento(agente(estado))
        ganadores = estado.finalPartida()
        so_g = sum(1 for g in ganadores if g in asientos_so)
        al_g = len(ganadores) - so_g
        etiqueta = "so" if so_g > al_g else ("aleatorio" if al_g > so_g else "empate")
        return {"resultado": etiqueta}

    if exp == "blackjack":
        B = juego("blackjack").BlackJack
        p = B(100)
        so = None
        if c["agente"] == "so":
            import pyplAI
            so = pyplAI.SOISMCTS(B.aplica_accion, B.posibles_acciones, B.es_estado_final_ronda, B.gana_jugador_ronda, B.determinization, 2, c["tiempo"])
        while not p.es_estado_final():
            p.comprobarNuevaRonda()
            if not p.iniciarRonda:
                if so:
                    p.rondaMCTS(so)
                else:
                    p.rondaPrueba()
        return {"resultado": p.jugador.creditos - p.jugador.creditosIniciales}

    if exp == "stratego":
        mod = juego("stratego")
        S = mod.Stratego
        ga = mod.posicionFichasAlgoritmoGenetico()
        so_ga = crear("stratego", "so", c["tiempo"])
        rival = crear("stratego", c["rival"], c["tiempo"])
        lado = 1 + semilla % 2
        estado = S(500, ga, None) if lado == 1 else S(500, None, ga)
        g, jugadas = partida_dos("stratego", estado, {lado: so_ga, 3 - lado: rival}, S.es_estado_final, S.aplica_movimiento,
                                 lambda s: 1 if s.gana_jugador(1) else (2 if s.gana_jugador(2) else 0))
        etiqueta = "empate" if g == 0 else ("so_ga" if g == lado else c["rival"])
        return {"resultado": etiqueta, "jugadas": jugadas}
    raise ValueError(exp)


# ---------------------------------------------------------------- plan


#Profundidades del TFG y su equivalente en pyplAI 1.1 (antes se exploraban d + 1 niveles)
PERFECTA = {
    "tictactoe": {"tfg": [3, 4, 5, 6], "partidas": 100, "calibracion": 10},
    "ultimate": {"tfg": [2, 3, 4], "partidas": {2: 40, 3: 40, 4: 12}, "calibracion": 2},
    "damas": {"tfg": [2, 3, 4, 5], "partidas": 24, "calibracion": 2, "turnos": 100},
}


def main():
    repo, salida = sys.argv[1], sys.argv[2]
    procesos = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    preparar(repo)
    pool = mp.Pool(procesos)
    resultados = []

    def lanzar(tareas):
        with open(salida, "a", encoding="utf-8") as f:
            for r in pool.imap_unordered(tarea, tareas):
                f.write(json.dumps(r) + "\n")
                f.flush()
                resultados.append(r)
                print(r["exp"], r["config"], r["resultado"] if not isinstance(r["resultado"], list) else "", r["segundos"], flush=True)

    #1. Calibración: tiempo medio por jugada de minimax para cada profundidad
    calib = []
    for nombre, cfg in PERFECTA.items():
        for d in cfg["tfg"]:
            for s in range(cfg["calibracion"]):
                calib.append((repo, "calibracion", {"juego": nombre, "profundidad": d + 1, "tfg": d, "turnos": cfg.get("turnos")}, s))
    lanzar(calib)
    tiempos = {}
    for r in resultados:
        if r["exp"] == "calibracion":
            tiempos.setdefault((r["config"]["juego"], r["config"]["tfg"]), []).extend(r["tiempos_minimax"])
    medias = {k: statistics.mean(v) for k, v in tiempos.items()}
    with open(salida, "a", encoding="utf-8") as f:
        f.write(json.dumps({"exp": "tiempos_minimax", "medias": {f"{k[0]}:{k[1]}": v for k, v in medias.items()}}) + "\n")

    #2. El resto de experimentos, de más largo a más corto
    tareas = []
    for nombre, cfg in PERFECTA.items():
        for d in cfg["tfg"]:
            n = cfg["partidas"][d] if isinstance(cfg["partidas"], dict) else cfg["partidas"]
            for s in range(n):
                tareas.append((repo, "mcts_vs_minimax", {"juego": nombre, "profundidad": d + 1, "tfg": d,
                               "tiempo": medias[(nombre, d)], "turnos": cfg.get("turnos")}, s))
    for t in (0.5, 1):
        tareas += [(repo, "stratego", {"tiempo": t, "rival": "aleatorio"}, s) for s in range(20)]
    tareas += [(repo, "stratego", {"tiempo": 0.5, "rival": "so"}, s) for s in range(20)]
    for t in (0.25, 0.5, 1, 2):
        tareas += [(repo, "escoba", {"tiempo": t, "jugadores": 2, "so": 1}, s) for s in range(60)]
    tareas += [(repo, "escoba", {"tiempo": 0.5, "jugadores": 4, "so": 2}, s) for s in range(60)]
    for t in (0.25, 1):
        tareas += [(repo, "blackjack", {"agente": "so", "tiempo": t}, s) for s in range(40)]
    tareas += [(repo, "blackjack", {"agente": "aleatorio"}, s) for s in range(100)]
    for t in (0.25, 1):
        tareas += [(repo, "phantom", {"a": "mo", "b": "aleatorio", "tiempo": t}, s) for s in range(60)]
        tareas += [(repo, "holjjak", {"a": "mo", "b": "aleatorio", "tiempo": t}, s) for s in range(60)]
        tareas += [(repo, "holjjak", {"a": "mo", "b": "so", "tiempo": t}, s) for s in range(60)]
    for t in (0.5, 2):
        tareas += [(repo, "phantom", {"a": "mo", "b": "so", "tiempo": t}, s) for s in range(60)]
    lanzar(tareas)
    pool.close()
    pool.join()
    print("FIN", flush=True)


if __name__ == "__main__":
    main()
