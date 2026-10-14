"""Tests de los algoritmos de pyplAI."""

import random

import pytest

import pyplAI
from pyplAI.Algoritmos import VICTORIA
from utilidades import TresEnRaya, algoritmos_tres_en_raya

NOMBRES = ["MCTS", "Minimax", "SOISMCTS", "MOISMCTS"]

#X (1) gana en (0, 2)
VICTORIA_INMEDIATA = [[1, 1, 0],
                      [2, 2, 0],
                      [0, 0, 0]]
#Mueve O (2): X amenaza (0, 2) y O no tiene victoria inmediata, así que debe bloquear
BLOQUEO = [[1, 1, 0],
           [2, 0, 0],
           [0, 0, 0]]


@pytest.mark.parametrize("nombre", NOMBRES)
def test_guarda_las_funciones_sin_staticmethod(nombre):
    #En Python < 3.10 un objeto staticmethod no se puede llamar directamente (L1)
    alg = algoritmos_tres_en_raya(pyplAI)[nombre]
    assert not isinstance(alg.aplicar_movimiento, staticmethod)
    assert callable(alg.aplicar_movimiento)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_encuentra_la_victoria_inmediata(nombre):
    random.seed(0)
    alg = algoritmos_tres_en_raya(pyplAI)[nombre]
    estado = TresEnRaya(VICTORIA_INMEDIATA, 1)
    assert alg.ejecuta(estado) == (0, 2)
    assert alg.analiza(estado).movimiento == (0, 2)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_bloquea_la_amenaza_del_rival(nombre):
    random.seed(0)
    alg = algoritmos_tres_en_raya(pyplAI)[nombre]
    assert alg.ejecuta(TresEnRaya(BLOQUEO, 2)) == (0, 2)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_analiza_no_escribe_en_stdout_y_no_modifica_el_estado(nombre, capsys):
    #Un servidor MCP por stdio no puede recibir nada en stdout (L2)
    random.seed(0)
    alg = algoritmos_tres_en_raya(pyplAI, iteraciones=200)[nombre]
    alg.estadisticas = True
    estado = TresEnRaya(BLOQUEO, 2)
    resultado = alg.analiza(estado)
    assert capsys.readouterr().out == ""
    assert estado.tablero == BLOQUEO and estado.jugadorActual == 2
    assert {e.movimiento for e in resultado.movimientos} == set(estado.obtiene_movimientos())
    assert resultado.movimiento == resultado.movimientos[0].movimiento


@pytest.mark.parametrize("nombre", NOMBRES)
def test_estadisticas_sigue_imprimiendo_en_ejecuta(nombre, capsys):
    alg = algoritmos_tres_en_raya(pyplAI, iteraciones=50)[nombre]
    alg.estadisticas = True
    alg.ejecuta(TresEnRaya(BLOQUEO, 2))
    assert "Tiempo de ejecución" in capsys.readouterr().out


@pytest.mark.parametrize("nombre", ["MCTS", "SOISMCTS", "MOISMCTS"])
def test_la_semilla_hace_la_busqueda_reproducible(nombre):
    #L6: con la misma semilla y el mismo número de iteraciones el análisis es idéntico
    def analisis():
        return algoritmos_tres_en_raya(pyplAI, iteraciones=300, semilla=7)[nombre].analiza(TresEnRaya())
    a, b = analisis(), analisis()
    assert [(e.movimiento, e.visitas, e.valor) for e in a.movimientos] == \
           [(e.movimiento, e.visitas, e.valor) for e in b.movimientos]


@pytest.mark.parametrize("nombre", ["MCTS", "SOISMCTS"])
def test_iteraciones_fija_el_numero_de_iteraciones(nombre):
    resultado = algoritmos_tres_en_raya(pyplAI, iteraciones=123)[nombre].analiza(TresEnRaya())
    assert resultado.iteraciones == 123


def test_iteraciones_debe_ser_positivo():
    with pytest.raises(ValueError):
        algoritmos_tres_en_raya(pyplAI, iteraciones=0)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_estado_final_o_sin_movimientos(nombre):
    alg = algoritmos_tres_en_raya(pyplAI)[nombre]
    ganado = TresEnRaya([[1, 1, 1], [2, 2, 0], [0, 0, 0]], 2)
    assert alg.ejecuta(ganado) is None
    assert alg.analiza(ganado).movimiento is None


class SinMovimientos:
    """Juego mal definido: tras el primer movimiento el estado no es final pero no tiene movimientos."""
    jugadorActual = 1

    def __init__(self):
        self.jugado = False

    def obtiene_movimientos(self):
        return [] if self.jugado else ["a", "b"]

    def aplica_movimiento(self, mov):
        self.jugado = True
        self.jugadorActual = 2
        return self

    def es_estado_final(self):
        return False

    def gana_jugador(self, jugador):
        return False

    def heuristica(self, jugador):
        return 0

    def determinization(self):
        return SinMovimientos()


@pytest.mark.parametrize("nombre", NOMBRES)
def test_error_claro_si_un_estado_no_final_no_tiene_movimientos(nombre):
    #L7: antes fallaba con IndexError o ValueError sin explicación
    S = SinMovimientos
    alg = {
        "MCTS": pyplAI.MCTS(S.aplica_movimiento, S.obtiene_movimientos, S.es_estado_final, S.gana_jugador, 2, 1, iteraciones=10),
        "Minimax": pyplAI.Minimax(S.aplica_movimiento, S.obtiene_movimientos, S.es_estado_final, S.gana_jugador, S.heuristica, 2, 2),
        "SOISMCTS": pyplAI.SOISMCTS(S.aplica_movimiento, S.obtiene_movimientos, S.es_estado_final, S.gana_jugador, S.determinization, 2, 1, iteraciones=10),
        "MOISMCTS": pyplAI.MOISMCTS(S.aplica_movimiento, S.obtiene_movimientos, S.es_estado_final, S.gana_jugador, S.determinization, lambda a: True, 2, 1, iteraciones=10),
    }[nombre]
    with pytest.raises(ValueError, match="no es final pero no tiene movimientos"):
        alg.ejecuta(SinMovimientos())


def test_minimax_usa_valores_finitos_y_premia_la_victoria_rapida():
    #L4: con ±inf una victoria en 1 jugada valía lo mismo que una en 5
    alg = algoritmos_tres_en_raya(pyplAI, profundidad=9)["Minimax"]
    resultado = alg.analiza(TresEnRaya(VICTORIA_INMEDIATA, 1))
    assert resultado.movimientos[0].valor == VICTORIA - 1
    assert all(abs(e.valor) < float("inf") for e in resultado.movimientos)


def test_minimax_profundidad_es_el_numero_de_niveles():
    #L9: profundidad 1 evalúa solo los 9 hijos de la raíz; profundidad 2 también sus 8 hijos
    T = TresEnRaya
    estados = []
    for profundidad in (1, 2):
        alg = pyplAI.Minimax(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador, T.heuristica, 2, profundidad)
        estados.append(alg.analiza(TresEnRaya()).iteraciones)
    assert estados == [1 + 9, 1 + 9 + 9 * 8]


def test_minimax_ejecuta_y_analiza_coinciden_en_el_valor():
    random.seed(3)
    alg = algoritmos_tres_en_raya(pyplAI, profundidad=4)["Minimax"]
    estado = TresEnRaya([[1, 0, 0], [0, 2, 0], [0, 0, 0]], 1)
    analisis = alg.analiza(estado)
    mejores = [e.movimiento for e in analisis.movimientos if e.valor == analisis.movimientos[0].valor]
    assert alg.ejecuta(estado) in mejores


def test_mcts_eleccion_final_por_media_o_por_visitas():
    #L3: Browne et al. devuelven BESTCHILD(v0, 0) (mejor media); seleccion_final="visitas" elige el más visitado
    T = TresEnRaya
    def raiz(alg):
        v0 = alg.nodo(None)
        v0.n, v0.q = 91, [0, 0]
        for mov, n, q in [((0, 0), 90, 80), ((1, 1), 1, 1)]:
            hijo = alg.nodo(v0, mov)
            hijo.n, hijo.q = n, [q, 0]
            v0.hijos.append(hijo)
        return v0
    media = pyplAI.MCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador, 2, 1)
    visitas = pyplAI.MCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador, 2, 1, seleccion_final="visitas")
    assert media._ordena_hijos(raiz(media), 0)[0].mov == (1, 1)
    assert visitas._ordena_hijos(raiz(visitas), 0)[0].mov == (0, 0)
    with pytest.raises(ValueError):
        pyplAI.MCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador, 2, 1, seleccion_final="otra")


class Trampa:
    """La determinización ofrece una acción que no es legal en el estado real y siempre gana."""
    def __init__(self, real=True):
        self.real = real
        self.jugadorActual = 1
        self.jugado = None

    def obtiene_movimientos(self):
        if self.jugado is not None:
            return []
        return ["a", "b"] if self.real else ["a", "b", "trampa"]

    def aplica_movimiento(self, mov):
        self.jugado = mov
        self.jugadorActual = 2
        return self

    def es_estado_final(self):
        return self.jugado is not None

    def gana_jugador(self, jugador):
        return jugador == 1 and self.jugado == "trampa"

    def determinization(self):
        return Trampa(real=False)


@pytest.mark.parametrize("clase", ["SOISMCTS", "MOISMCTS"])
def test_ismcts_solo_elige_movimientos_legales(clase):
    #L5: la elección final se filtra por los movimientos legales del estado real
    T = Trampa
    if clase == "SOISMCTS":
        alg = pyplAI.SOISMCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador, T.determinization, 2, 1, iteraciones=100, semilla=1)
    else:
        alg = pyplAI.MOISMCTS(T.aplica_movimiento, T.obtiene_movimientos, T.es_estado_final, T.gana_jugador, T.determinization, lambda a: True, 2, 1, iteraciones=100, semilla=1)
    resultado = alg.analiza(Trampa())
    assert resultado.movimiento in ("a", "b")
    assert "trampa" not in [e.movimiento for e in resultado.movimientos]


def test_so_ismcts_cuenta_la_disponibilidad_al_expandir():
    #L8: Cowling et al. incrementan n' de todos los hijos compatibles con la determinización
    T = TresEnRaya
    alg = algoritmos_tres_en_raya(pyplAI)["SOISMCTS"]
    v0 = alg.nodo(None)
    v0.r = [0, 0]
    estado = TresEnRaya()
    movs = estado.obtiene_movimientos()
    alg.expand(v0, estado, movs, movs)
    existente = v0.c[0]
    restantes = v0.actions_of_determinization_without_children(movs)
    alg.expand(v0, estado, restantes, movs)
    assert existente.nP == 2
    assert v0.c[1].nP == 1


def test_resultado_analisis_exportado():
    assert pyplAI.ResultadoAnalisis(None).movimientos == []
    assert pyplAI.__version__ == "1.1.0"
