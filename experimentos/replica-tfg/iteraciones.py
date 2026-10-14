"""Iteraciones por segundo de SO-ISMCTS y MO-ISMCTS en las mismas posiciones, en un solo proceso.

Uso: python iteraciones.py <repo pyplAI>
"""
import random
import statistics
import sys

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, sys.argv[1] + "/tests")
import pyplAI  # noqa: E402
from utilidades import cargar_juego  # noqa: E402

TIEMPO = 1.0


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


for nombre, clase in (("phantom", "Phantom"), ("holjjak", "Holjjak")):
    C = getattr(cargar_juego(nombre), clase)
    so = pyplAI.SOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, 2, TIEMPO)
    mo = pyplAI.MOISMCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.determinization, C.accion_visible, 2, TIEMPO)
    ratios, it_so, it_mo = [], [], []
    for i, s in enumerate(posiciones(C, 20, 1)):
        orden = [so, mo] if i % 2 == 0 else [mo, so]
        r = {id(a): a.analiza(s).iteraciones for a in orden}
        it_so.append(r[id(so)])
        it_mo.append(r[id(mo)])
        ratios.append(r[id(so)] / r[id(mo)])
    print(f"{nombre}: SO {statistics.mean(it_so):.0f} it/s, MO {statistics.mean(it_mo):.0f} it/s, "
          f"SO/MO media {statistics.mean(ratios):.2f} (mín {min(ratios):.2f}, máx {max(ratios):.2f}) en 20 posiciones")
