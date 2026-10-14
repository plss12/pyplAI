"""Tests de reglas de los juegos de ejemplo de Juegos/."""

import contextlib
import io
import random

import pytest

import pyplAI
from utilidades import cargar_juego


def tablero_vacio_damas():
    return tuple([0] * 8 for _ in range(8))


#Coordenadas de los movimientos de las damas: (columna, fila) con la fila 0 abajo
def c(i, j):
    return (j, 7 - i)


# ---------------------------------------------------------------- tres en raya


def test_tres_en_raya_ganador_distingue_al_jugador_2():
    #J1: antes se guardaba gana_jugador(1) y las victorias del jugador 2 contaban como empates
    T = cargar_juego("tictactoe").TicTacToe
    s = T()
    s.tablero = ([2, 2, 2], [1, 1, 0], [1, 0, 0])
    assert s.ganador() == 2


def test_tres_en_raya_heuristica_distingue_dos_en_linea_de_una():
    #J8: las líneas con una sola ficha sumaban como si tuvieran dos
    T = cargar_juego("tictactoe").TicTacToe
    s = T()
    s.tablero = ([1, 0, 0], [0, 0, 0], [0, 0, 0])
    #Una ficha en una esquina abre 3 líneas con una ficha propia
    assert s.heuristica(1) == 3


# ---------------------------------------------------------------- Ultimate


def test_ultimate_subtablero_lleno_en_tablas_permite_jugar_en_otro():
    #J2: antes la partida terminaba en empate al enviar a un subtablero lleno
    U = cargar_juego("ultimate").UltimateTTT
    s = U()
    jugadas = [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 0, 2), (0, 0, 1, 1), (0, 0, 1, 0), (0, 0, 1, 2),
               (0, 0, 2, 1), (0, 0, 2, 0), (0, 0, 2, 2)]
    for mov in jugadas:
        s.tableroJugada = (0, 0)
        s.aplica_movimiento(mov)
    assert s.tableroPrincipal[0][0] == U.TABLAS
    s.tableroJugada = (0, 0)
    movimientos = s.obtiene_movimientos()
    assert len(movimientos) == 72
    assert all((m[0], m[1]) != (0, 0) for m in movimientos)
    assert not s.es_estado_final()


def test_ultimate_ganador():
    U = cargar_juego("ultimate").UltimateTTT
    s = U()
    s.tableroPrincipal = ([2, 2, 2], [0, 1, 0], [1, 0, 0])
    assert s.ganador() == 2


# ---------------------------------------------------------------- damas


def test_damas_posicion_inicial_reglamentaria():
    D = cargar_juego("damas").Damas
    s = D(100)
    #Esquina inferior derecha jugable, 12 piezas por bando y salen las blancas (2) con 7 movimientos
    assert s.tablero[7][7] == 2 and s.tablero[0][0] == 1
    assert sum(fila.count(1) for fila in s.tablero) == 12
    assert sum(fila.count(2) for fila in s.tablero) == 12
    assert s.jugadorActual == 2
    assert len(s.obtiene_movimientos()) == 7


def test_damas_peon_solo_captura_hacia_delante():
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[4][3] = 2  #Peón blanco, avanza hacia la fila 0
    s.tablero[5][4] = 1  #Peón negro detrás de él
    s.tablero[3][2] = 1  #Peón negro delante de él
    s.jugadorActual = 2
    movimientos = s.obtiene_movimientos()
    assert movimientos == [[c(4, 3) + c(2, 1), [c(3, 2)]]]


def test_damas_captura_obligatoria_ley_de_la_cantidad():
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[6][1] = 2  #Puede capturar dos piezas seguidas
    s.tablero[5][2] = 1
    s.tablero[3][4] = 1
    s.tablero[6][5] = 2  #Solo puede capturar una
    s.tablero[5][6] = 1
    s.jugadorActual = 2
    assert s.obtiene_movimientos() == [[c(6, 1) + c(2, 5), [c(5, 2), c(3, 4)]]]


def test_damas_ley_de_la_calidad():
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[6][1] = 2
    s.tablero[5][2] = 1  #Captura un peón
    s.tablero[6][7] = 2
    s.tablero[5][6] = 3  #Captura una dama
    s.jugadorActual = 2
    assert s.obtiene_movimientos() == [[c(6, 7) + c(4, 5), [c(5, 6)]]]


def test_damas_dama_vuela_y_elige_casilla_de_caida():
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[7][0] = 4  #Dama blanca en la esquina
    s.tablero[4][3] = 1  #Peón negro a distancia en la diagonal
    s.jugadorActual = 2
    destinos = sorted(m[0][2:] for m in s.obtiene_movimientos())
    #Puede caer en cualquier casilla libre detrás de la pieza capturada: (3,4), (2,5), (1,6) y (0,7)
    assert destinos == sorted([c(3, 4), c(2, 5), c(1, 6), c(0, 7)])


def test_damas_no_se_salta_dos_veces_la_misma_pieza():
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[4][4] = 4
    s.tablero[3][3] = 1
    s.jugadorActual = 2
    for movimiento in s.obtiene_movimientos():
        assert len(movimiento[1]) == len(set(movimiento[1])) == 1


def test_damas_secuencia_de_dama_sin_ficha_fantasma():
    #J7: tras la primera captura la dama sigue capturando desde una casilla lejana
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[7][0] = 4
    s.tablero[5][2] = 1
    s.tablero[2][3] = 1
    s.jugadorActual = 2
    movimientos = s.obtiene_movimientos()
    assert all(len(m[1]) == 2 for m in movimientos)
    assert any(m[0][2:] == c(1, 2) for m in movimientos)


def test_damas_coronacion_y_aplicacion_de_captura():
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[2][1] = 2
    s.tablero[1][2] = 1
    s.jugadorActual = 2
    (movimiento,) = s.obtiene_movimientos()
    s.aplica_movimiento(movimiento)
    assert s.tablero[0][3] == 4 and s.tablero[1][2] == 0 and s.tablero[2][1] == 0


def test_damas_imprime_final_detecta_victoria_por_bloqueo():
    #J5: se pasaba la lista de movimientos en lugar de su número y salía empate
    D = cargar_juego("damas").Damas
    s = D(100)
    s.tablero = tablero_vacio_damas()
    s.tablero[7][7] = 2
    s.tablero[6][6] = 1
    s.tablero[5][5] = 1
    s.jugadorActual = 2
    assert s.obtiene_movimientos() == []
    with contextlib.redirect_stdout(io.StringIO()):
        assert s.imprime_final() == 1
    assert s.ganador() == 1


# ---------------------------------------------------------------- Phantom y Holjjak


def test_phantom_determinizacion_conserva_lo_que_sabe_el_jugador():
    P = cargar_juego("phantom").Phantom
    random.seed(4)
    s = P()
    for mov in [(0, 0), (1, 1), (0, 1), (2, 2)]:
        s.aplica_movimiento(mov)
    #El jugador 1 intenta jugar en (2, 2), ocupada por el rival: la descubre y repite turno
    s.aplica_movimiento((2, 2))
    for _ in range(50):
        d = s.determinization()
        assert d.tablero[0][0] == 1 and d.tablero[0][1] == 1 and d.tablero[2][2] == 2
        assert sum(fila.count(2) for fila in d.tablero) == 2


def test_holjjak_usa_ismcts_al_esconder_canicas():
    #J6: al esconder canicas se usaba MCTS de información perfecta, que ve el número escondido
    H = cargar_juego("holjjak").Holjjak

    class Registro:
        llamadas = 0

        def ejecuta(self, estado):
            Registro.llamadas += 1
            return estado.obtiene_movimientos()[0]

    s = H()
    with contextlib.redirect_stdout(io.StringIO()):
        s.turno_mcts(Registro())
    assert Registro.llamadas == 1 and s.turno == 1


# ---------------------------------------------------------------- Escoba


def test_escoba_cartas_obligadas_a_capturar_y_libres_para_dejar():
    E = cargar_juego("escoba").Escoba
    random.seed(0)
    s = E(2, False)
    s.mesa.cartas = [[5, "copas"], [2, "oros"]]
    s.jugadores[0].cartas = [[10, "bastos"], [1, "espadas"], [9, "oros"]]
    movimientos = s.obtieneMovimientos()
    #El rey (10) suma 15 con el 5 y debe capturarlo; el 1 y el caballo no suman 15 y se dejan en la mesa
    assert [[10, "bastos"], [[5, "copas"]]] in movimientos
    assert [[10, "bastos"]] not in movimientos
    assert [[1, "espadas"]] in movimientos and [[9, "oros"]] in movimientos
    assert len(movimientos) == 3


def test_escoba_recuento_con_sietes_y_empates():
    E = cargar_juego("escoba").Escoba
    s = E(2, False)
    sietes = [[7, palo] for palo in ("oros", "copas", "espadas", "bastos")]
    s.jugadores[0].capturadas = sietes + [[1, "oros"]]
    s.jugadores[1].capturadas = [[2, "copas"], [3, "copas"], [4, "copas"], [5, "copas"], [6, "oros"]]
    s.jugadores[0].escobas = s.jugadores[1].escobas = 0
    #J4b: antes los sietes no contaban. Cartas 5-5 (empate, nadie puntúa), oros 2-1, setenta y siete de oros para el 1
    assert s.recuentoPuntos() == [3, 0]
    assert s.ganaJugador(1) and not s.ganaJugador(2)


def test_escoba_empate_en_puntos_no_da_la_victoria():
    E = cargar_juego("escoba").Escoba
    s = E(2, False)
    for jugador in s.jugadores:
        jugador.capturadas, jugador.escobas = [], 1
    assert not s.ganaJugador(1) and not s.ganaJugador(2)


def test_escoba_partida_completa_conserva_las_40_cartas():
    #J4a: la recogida final dejaba cartas en la mesa y duplicaba capturas al repetir la comprobación
    E = cargar_juego("escoba").Escoba
    random.seed(11)
    s = E(2, False)
    rondas = 0
    while not s.esEstadoFinal():
        s.aplicarMovimiento(random.choice(s.obtieneMovimientos()))
        rondas += 1
        s.esEstadoFinal()
    assert rondas == 36
    assert s.mesa.cartas == []
    assert sum(len(j.capturadas) for j in s.jugadores) == 40


def test_escoba_de_muestra_para_el_que_reparte():
    E = cargar_juego("escoba").Escoba
    for semilla in range(500):
        random.seed(semilla)
        s = E(2, False)
        if s.jugadores[1].escobas == 1:
            assert s.mesa.cartas == [] and len(s.jugadores[1].capturadas) == 4
            break
    else:
        pytest.fail("Ninguna semilla generó una escoba de muestra")


def test_escoba_jugador_aleatorio_no_siempre_juega_lo_mismo():
    #J4c: rondaPrueba jugaba siempre el primer movimiento de la lista
    E = cargar_juego("escoba").Escoba
    elegidos = set()
    for semilla in range(30):
        random.seed(semilla)
        s = E(2, False)
        s.mesa.cartas = [[1, "copas"]]
        s.jugadores[0].cartas = [[1, "bastos"], [2, "bastos"], [3, "bastos"]]
        with contextlib.redirect_stdout(io.StringIO()):
            s.rondaPrueba()
        elegidos.add(tuple(map(tuple, s.mesa.cartas)))
    assert len(elegidos) > 1


# ---------------------------------------------------------------- BlackJack


def test_blackjack_determinizacion_oculta_la_carta_tapada():
    #J3: la mano del croupier conservaba la carta real y el algoritmo jugaba viéndola
    B = cargar_juego("blackjack").BlackJack
    random.seed(1)
    s = B(100)
    s.iniciarRonda = False
    s.nuevaRonda()
    real = s.croupier.mano[0]
    distintas = 0
    for _ in range(200):
        d = s.determinization()
        assert d.croupier.cartaOculta is d.croupier.mano[0]
        assert len(d.baraja.cartas) == len(s.baraja.cartas)
        if d.croupier.mano[0] != real:
            distintas += 1
    assert distintas > 150


def test_blackjack_empate_con_la_banca_no_es_victoria():
    #J9: el empate daba recompensa 1 a los dos jugadores
    B = cargar_juego("blackjack").BlackJack
    s = B(100)
    assert not s.gana_jugador_ronda(1) and not s.gana_jugador_ronda(2)
    s.jugador.creditos += 2
    assert s.gana_jugador_ronda(1) and not s.gana_jugador_ronda(2)


# ---------------------------------------------------------------- Stratego


def test_stratego_usa_la_mejor_colocacion_del_genetico():
    #J10: se elegía una colocación al azar y las que empataban en fitness se perdían
    m = cargar_juego("stratego")
    genes = m.cargar_genes()
    assert len(genes) == 10
    mejor = max(genes, key=lambda g: g[0])[1]
    assert m.posicionFichasAlgoritmoGenetico() == mejor


def test_stratego_ruleta_con_fitness_cero():
    m = cargar_juego("stratego")
    poblacion = m.Poblacion([m.Cromosoma() for _ in range(4)])
    for cromosoma in poblacion.poblacion:
        cromosoma.fitness = 0
    poblacion.prepararPoblacion()
    assert poblacion.selecciona() in poblacion.poblacion


# ---------------------------------------------------------------- partidas completas


def jugar(estado, elegir, es_final, aplicar):
    jugadas = 0
    while not es_final(estado):
        estado = aplicar(estado, elegir(estado))
        jugadas += 1
        assert jugadas < 2000
    return estado


@pytest.mark.parametrize("nombre", ["tictactoe", "ultimate", "damas"])
def test_partidas_completas_informacion_perfecta(nombre):
    m = cargar_juego(nombre)
    C = {"tictactoe": m.__dict__.get("TicTacToe"), "ultimate": m.__dict__.get("UltimateTTT"), "damas": m.__dict__.get("Damas")}[nombre]
    random.seed(5)
    crear = (lambda: C(60)) if nombre == "damas" else C
    mcts = pyplAI.MCTS(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, 2, 1, iteraciones=30, semilla=1)
    minimax = pyplAI.Minimax(C.aplica_movimiento, C.obtiene_movimientos, C.es_estado_final, C.gana_jugador, C.heuristica, 2, 1)
    def elegir(s):
        return (mcts if s.jugadorActual == 1 else minimax).ejecuta(s)
    final = jugar(crear(), elegir, C.es_estado_final, C.aplica_movimiento)
    assert final.ganador() in (0, 1, 2)


def test_partidas_completas_informacion_imperfecta():
    random.seed(6)
    P = cargar_juego("phantom").Phantom
    so = pyplAI.SOISMCTS(P.aplica_movimiento, P.obtiene_movimientos, P.es_estado_final, P.gana_jugador, P.determinization, 2, 1, iteraciones=30)
    mo = pyplAI.MOISMCTS(P.aplica_movimiento, P.obtiene_movimientos, P.es_estado_final, P.gana_jugador, P.determinization, P.accion_visible, 2, 1, iteraciones=30)
    jugar(P(), lambda s: (so if s.jugadorActual == 1 else mo).ejecuta(s), P.es_estado_final, P.aplica_movimiento)

    H = cargar_juego("holjjak").Holjjak
    mo = pyplAI.MOISMCTS(H.aplica_movimiento, H.obtiene_movimientos, H.es_estado_final, H.gana_jugador, H.determinization, H.accion_visible, 2, 1, iteraciones=30)
    jugar(H(), mo.ejecuta, H.es_estado_final, H.aplica_movimiento)

    E = cargar_juego("escoba").Escoba
    so = pyplAI.SOISMCTS(E.aplicarMovimiento, E.obtieneMovimientos, E.esEstadoFinal, E.ganaJugador, E.determinization, 2, 1, iteraciones=30)
    final = jugar(E(2, False), so.ejecuta, E.esEstadoFinal, E.aplicarMovimiento)
    assert sum(len(j.capturadas) for j in final.jugadores) == 40

    S = cargar_juego("stratego").Stratego
    so = pyplAI.SOISMCTS(S.aplica_movimiento, S.obtiene_movimientos, S.es_estado_final, S.gana_jugador, S.determinization, 2, 1, iteraciones=10)
    jugar(S(40), so.ejecuta, S.es_estado_final, S.aplica_movimiento)

    B = cargar_juego("blackjack").BlackJack
    so = pyplAI.SOISMCTS(B.aplica_accion, B.posibles_acciones, B.es_estado_final_ronda, B.gana_jugador_ronda, B.determinization, 2, 1, iteraciones=30)
    partida = B(20)
    with contextlib.redirect_stdout(io.StringIO()):
        while not partida.es_estado_final():
            partida.comprobarNuevaRonda()
            if not partida.iniciarRonda:
                partida.rondaMCTS(so)
