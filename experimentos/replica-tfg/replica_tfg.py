"""Segunda pasada: MCTS contra Minimax con los tiempos por jugada de las tablas del TFG (sección 6.1).

Uso: python replica_tfg.py <repo pyplAI> <salida.jsonl> [procesos]
"""
import json
import multiprocessing as mp
import sys

import replica

#Tiempo medio de minimax por jugada medido en el TFG, que se dio a MCTS en cada enfrentamiento
TIEMPOS_TFG = {
    "tictactoe": {3: 0.06, 4: 0.14, 5: 0.23, 6: 0.8},
    "ultimate": {2: 0.25, 3: 0.79, 4: 4.02},
    "damas": {2: 0.15, 3: 0.32, 4: 0.85, 5: 1.77},
}
PARTIDAS = {"tictactoe": {3: 100, 4: 100, 5: 100, 6: 100}, "ultimate": {2: 40, 3: 40, 4: 12}, "damas": {2: 24, 3: 24, 4: 24, 5: 24}}


def main():
    repo, salida = sys.argv[1], sys.argv[2]
    procesos = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    tareas = []
    #Primero las más largas
    for nombre in ("damas", "ultimate", "tictactoe"):
        for d in sorted(TIEMPOS_TFG[nombre], reverse=True):
            config = {"juego": nombre, "profundidad": d + 1, "tfg": d, "tiempo": TIEMPOS_TFG[nombre][d], "turnos": 100 if nombre == "damas" else None}
            tareas += [(repo, "mcts_vs_minimax", config, s) for s in range(PARTIDAS[nombre][d])]
    with mp.Pool(procesos) as pool, open(salida, "a", encoding="utf-8") as f:
        for r in pool.imap_unordered(replica.tarea, tareas):
            r.pop("tiempos_minimax", None)
            f.write(json.dumps(r) + "\n")
            f.flush()
            print(r["config"]["juego"], r["config"]["tfg"], r["resultado"], r["segundos"], flush=True)
    print("FIN", flush=True)


if __name__ == "__main__":
    main()
