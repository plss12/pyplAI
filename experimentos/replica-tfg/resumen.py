"""Resume resultados.jsonl de la réplica."""
import json
import math
import statistics
import sys
from collections import Counter, defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return (0, 0)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0, c - h), min(1, c + h))


grupos = defaultdict(list)
for linea in open(sys.argv[1], encoding="utf-8"):
    r = json.loads(linea)
    if r["exp"] in ("calibracion", "tiempos_minimax"):
        if r["exp"] == "tiempos_minimax":
            print("Tiempos medios de minimax (calibración):", {k: round(v, 3) for k, v in r["medias"].items()})
        continue
    c = dict(r["config"])
    c.pop("tiempo", None) if r["exp"] == "mcts_vs_minimax" else None
    clave = (r["exp"], json.dumps(c, sort_keys=True))
    grupos[clave].append(r)

for (exp, config), rs in sorted(grupos.items()):
    n = len(rs)
    if exp == "blackjack":
        v = [r["resultado"] for r in rs]
        print(f"{exp:16s} {config:60s} n={n:3d} media={statistics.mean(v):+.2f} monedas (de {statistics.stdev(v)/math.sqrt(n):.2f} e.e.)")
        continue
    cuenta = Counter(r["resultado"] for r in rs)
    partes = []
    for etiqueta, k in cuenta.most_common():
        lo, hi = wilson(k, n)
        partes.append(f"{etiqueta} {100*k/n:.0f}% [{100*lo:.0f}-{100*hi:.0f}]")
    extra = ""
    if exp == "phantom" and '"b": "so"' in config:
        ia = [x for r in rs for x in r["iter_a"]]
        ib = [x for r in rs for x in r["iter_b"]]
        if ia and ib:
            extra = f" | iter/jugada MO={statistics.mean(ia):.0f} SO={statistics.mean(ib):.0f} (SO/MO={statistics.mean(ib)/statistics.mean(ia):.2f})"
    if exp == "holjjak" and '"b": "so"' in config:
        ia = [x for r in rs for x in r["iter_a"]]
        ib = [x for r in rs for x in r["iter_b"]]
        if ia and ib:
            extra = f" | iter/jugada MO={statistics.mean(ia):.0f} SO={statistics.mean(ib):.0f} (SO/MO={statistics.mean(ib)/statistics.mean(ia):.2f})"
    print(f"{exp:16s} {config:60s} n={n:3d} " + ", ".join(partes) + extra)
