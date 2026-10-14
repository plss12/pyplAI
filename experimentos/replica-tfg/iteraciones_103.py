"""Lo mismo que iteraciones.py, con pyplAI 1.0.3 y los juegos originales (lee las iteraciones del modo verbose).

Uso: python iteraciones_103.py <carpeta con Juegos originales>
"""
import contextlib
import importlib.util
import io
import random
import re
import statistics
import sys

import pyplAI

TIEMPO = 1.0
RUTAS = {"phantom": ("SO-MO-ISMCTS/MO/Phantom.py", "Phantom"), "holjjak": ("SO-MO-ISMCTS/MO/Holjjak.py", "Holjjak")}


def cargar(nombre):
    ruta, clase = RUTAS[nombre]
    spec = importlib.util.spec_from_file_location(nombre, sys.argv[1] + "/Juegos/" + ruta)
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return getattr(m, clase)


def posiciones(C, n, semilla):
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


def iteraciones(alg, s):
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        alg.ejecuta(s)
    visitados = re.findall(r"nodos visitados:\s+(\d+)", salida.getvalue())
    return int(visitados[-1])


for nombre in ("phantom", "holjjak"):
    C = cargar(nombre)
    so = pyplAI.SOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, 2, TIEMPO, True)
    mo = pyplAI.MOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, C.accion_visible, 2, TIEMPO, True)
    ratios, it_so, it_mo = [], [], []
    for i, s in enumerate(posiciones(C, 20, 1)):
        jugador = s.jugadorActual
        orden = [so, mo] if i % 2 == 0 else [mo, so]
        r = {}
        for a in orden:
            r[id(a)] = iteraciones(a, s)
        it_so.append(r[id(so)])
        it_mo.append(r[id(mo)])
        ratios.append(r[id(so)] / r[id(mo)])
    print(f"{nombre} (1.0.3): SO {statistics.mean(it_so):.0f} it/s, MO {statistics.mean(it_mo):.0f} it/s, "
          f"SO/MO media {statistics.mean(ratios):.2f} (mín {min(ratios):.2f}, máx {max(ratios):.2f}) en 20 posiciones")
