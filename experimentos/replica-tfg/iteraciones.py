"""Iteraciones de SO-ISMCTS y MO-ISMCTS en el mismo tiempo, en las mismas posiciones y en un solo proceso.

Usa la versión de pyplAI que esté instalada. Con la 1.1.0 lee el resultado de analiza(); con la 1.0.3,
que no lo tiene, lee las iteraciones del modo verbose.

Uso:
    python iteraciones.py                       # pyplAI 1.1.0 y los juegos del repo
    python iteraciones.py --juegos <carpeta>    # en un entorno con pyplAI==1.0.3 y los juegos originales:
                                                # git archive d4b5743 Juegos | tar -x -C <carpeta>
"""

import argparse
import contextlib
import importlib.util
import io
import random
import re
import statistics
from pathlib import Path

import pyplAI

RUTAS = {"phantom": ("SO-MO-ISMCTS/MO/Phantom.py", "Phantom"), "holjjak": ("SO-MO-ISMCTS/MO/Holjjak.py", "Holjjak")}


def cargar(carpeta, nombre):
    ruta, clase = RUTAS[nombre]
    spec = importlib.util.spec_from_file_location(nombre, Path(carpeta) / "Juegos" / ruta)
    modulo = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(modulo)
    return getattr(modulo, clase)


def posiciones(C, n, semilla):
    """Posiciones no finales tras 0 a 6 jugadas aleatorias, con más de un movimiento posible."""
    rng = random.Random(semilla)
    res = []
    while len(res) < n:
        s = C()
        for _ in range(rng.randint(0, 6)):
            if s.es_estado_final():
                break
            s.aplica_movimiento(rng.choice(s.obtiene_movimientos()))
        if not s.es_estado_final() and len(s.obtiene_movimientos()) > 1:
            res.append(s)
    return res


def iteraciones(algoritmo, estado):
    if hasattr(algoritmo, "analiza"):
        return algoritmo.analiza(estado).iteraciones
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        algoritmo.ejecuta(estado)
    return int(re.findall(r"nodos visitados:\s+(\d+)", salida.getvalue())[-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--juegos", default=str(Path(__file__).resolve().parents[2]), help="Carpeta que contiene Juegos/.")
    parser.add_argument("--posiciones", type=int, default=20)
    parser.add_argument("--tiempo", type=float, default=1.0)
    args = parser.parse_args()
    version = getattr(pyplAI, "__version__", "1.0.3")
    verbose = not hasattr(pyplAI.SOISMCTS, "analiza")
    for nombre in RUTAS:
        C = cargar(args.juegos, nombre)
        so = pyplAI.SOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, 2, args.tiempo, verbose)
        mo = pyplAI.MOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, C.accion_visible, 2, args.tiempo, verbose)
        it_so, it_mo, ratios = [], [], []
        for i, estado in enumerate(posiciones(C, args.posiciones, 1)):
            # Se alterna cuál de los dos busca primero en cada posición
            orden = [so, mo] if i % 2 == 0 else [mo, so]
            r = {id(a): iteraciones(a, estado) for a in orden}
            it_so.append(r[id(so)])
            it_mo.append(r[id(mo)])
            ratios.append(r[id(so)] / r[id(mo)])
        print(f"{nombre} ({version}): SO {statistics.mean(it_so) / args.tiempo:.0f} it/s, MO {statistics.mean(it_mo) / args.tiempo:.0f} it/s, "
              f"SO/MO media {statistics.mean(ratios):.2f} (mín {min(ratios):.2f}, máx {max(ratios):.2f}) en {args.posiciones} posiciones")


if __name__ == "__main__":
    main()
