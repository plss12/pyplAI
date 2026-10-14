"""Resume resultados.csv: porcentaje de victorias de cada bando con su intervalo de confianza del 95 %.

Uso: python resumen.py [resultados.csv]
"""

import csv
import math
import statistics
import sys
from collections import Counter, defaultdict


def wilson(k, n, z=1.96):
    """Intervalo de confianza de Wilson para una proporción k / n."""
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centro - margen), min(1.0, centro + margen)


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "resultados.csv"
    grupos = defaultdict(list)
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            clave = (fila["juego"], fila["agente"], fila["rival"], fila["profundidad_tfg"], fila["jugadores"], fila["tiempo"])
            grupos[clave].append(fila)

    for (juego, agente, rival, profundidad, jugadores, tiempo), filas in grupos.items():
        n = len(filas)
        etiqueta = f"{juego}: {agente} contra {rival}"
        if profundidad:
            etiqueta += f", profundidad del TFG {profundidad}"
        if jugadores:
            etiqueta += f", {jugadores} jugadores"
        if tiempo:
            etiqueta += f", {tiempo} s"
        if juego == "blackjack":
            monedas = [float(fila["monedas"]) for fila in filas]
            error = f" (error típico {statistics.stdev(monedas) / math.sqrt(n):.2f})" if n > 1 else ""
            print(f"{etiqueta} (n={n}): {statistics.mean(monedas):+.2f} monedas por partida{error}")
            continue
        cuenta = Counter(fila["ganador"] for fila in filas)
        partes = []
        for ganador in (agente, rival, "empate"):
            k = cuenta.get(ganador, 0)
            bajo, alto = wilson(k, n)
            partes.append(f"{ganador} {100 * k / n:.0f} % [{100 * bajo:.0f}-{100 * alto:.0f}]")
        print(f"{etiqueta} (n={n}): " + ", ".join(partes))


if __name__ == "__main__":
    main()
