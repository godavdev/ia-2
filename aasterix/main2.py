# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring, invalid-name

from math import sqrt
from queue import PriorityQueue
import time
from typing import Callable, Dict, List, Set, Tuple
import pygame

pygame.init()

# Reloj
clock = pygame.time.Clock()
FPS = 60
STEPS_PER_SECOND = 3

# Configuraciones iniciales
ANCHO_VENTANA = 800
VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ANCHO_VENTANA))
pygame.display.set_caption("Visualización de Nodos")

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
VERDE = (95, 242, 75)
ROJO = (255, 66, 95)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
AZUL = (51, 85, 255)

# Costos por moverse
RECT_COST = 1.0
DIAG_COST = 1.4


class Nodo:
    def __init__(
        self,
        fila: int,
        col: int,
        ancho: float,
    ):
        self.fila = fila
        self.col = col
        self.x = fila * ancho
        self.y = col * ancho
        self.color = BLANCO
        self.ancho = ancho
        self.vecinos: List[Tuple[Nodo, float]] = []

    def get_pos(self):
        return self.fila, self.col

    def es_pared(self):
        return self.color == NEGRO

    def es_inicio(self):
        return self.color == NARANJA

    def es_fin(self):
        return self.color == PURPURA

    def restablecer(self):
        self.vecinos = []
        self.color = BLANCO

    def hacer_inicio(self):
        self.color = NARANJA

    def hacer_pared(self):
        self.color = NEGRO

    def hacer_fin(self):
        self.color = PURPURA

    def hacer_cerrado(self):
        self.color = ROJO

    def hacer_abierto(self):
        self.color = VERDE

    def hacer_camino(self):
        self.color = AZUL

    def dibujar(self, ventana: pygame.Surface):
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))

    def inicializar_vecinos(self, grid: List[List["Nodo"]], filas: int):
        # Inicializar arriba
        if self.fila > 0 and not grid[self.fila - 1][self.col].es_pared():
            self.vecinos.append((grid[self.fila - 1][self.col], RECT_COST))

        # Inicializar abajo
        if self.fila < filas - 1 and not grid[self.fila + 1][self.col].es_pared():
            self.vecinos.append((grid[self.fila + 1][self.col], RECT_COST))

        # Inicializar izq
        if self.col > 0 and not grid[self.fila][self.col - 1].es_pared():
            self.vecinos.append((grid[self.fila][self.col - 1], RECT_COST))

        # Inicializar derecha
        if self.col < filas - 1 and not grid[self.fila][self.col + 1].es_pared():
            self.vecinos.append((grid[self.fila][self.col + 1], RECT_COST))

        # Inicializar diagonal arriba izq
        if (
            self.fila > 0
            and self.col > 0
            and not grid[self.fila - 1][self.col - 1].es_pared()
        ):
            self.vecinos.append((grid[self.fila - 1][self.col - 1], DIAG_COST))

        # Inicializar diagonal arriba derecha
        if (
            self.fila > 0
            and self.col < filas - 1
            and not grid[self.fila - 1][self.col + 1].es_pared()
        ):
            self.vecinos.append((grid[self.fila - 1][self.col + 1], DIAG_COST))

        # Inicializar diagonal abajo izq
        if (
            self.fila < filas - 1
            and self.col > 0
            and not grid[self.fila + 1][self.col - 1].es_pared()
        ):
            self.vecinos.append((grid[self.fila + 1][self.col - 1], DIAG_COST))

        # Inicializar diagonal abajo derecha
        if (
            self.fila < filas - 1
            and self.col < filas - 1
            and not grid[self.fila + 1][self.col + 1].es_pared()
        ):
            self.vecinos.append((grid[self.fila + 1][self.col + 1], DIAG_COST))


class Grid:
    def __init__(self, filas: int, ancho_ventana: float):
        self.filas = filas
        self.ancho_ventana = ancho_ventana
        self.nodos = self.crear()

    def crear(self) -> List[List[Nodo]]:
        nodos = []
        ancho_nodo = self.ancho_ventana // self.filas
        for i in range(self.filas):
            nodos.append([])
            for j in range(self.filas):
                nodo = Nodo(i, j, ancho_nodo)
                nodos[i].append(nodo)
        return nodos

    def dibujar_grid(self, ventana: pygame.Surface):
        ancho_nodo = self.ancho_ventana // self.filas
        for i in range(self.filas):
            pygame.draw.line(
                ventana, GRIS, (0, i * ancho_nodo), (ANCHO_VENTANA, i * ancho_nodo)
            )
            for j in range(self.filas):
                pygame.draw.line(
                    ventana, GRIS, (j * ancho_nodo, 0), (j * ancho_nodo, ANCHO_VENTANA)
                )

    def dibujar(self, ventana: pygame.Surface):
        VENTANA.fill(BLANCO)
        for fila in self.nodos:
            for nodo in fila:
                nodo.dibujar(VENTANA)
        self.dibujar_grid(ventana)

    def get_nodo(self, pos: Tuple[int, int]):
        fila, col = pos
        return self.nodos[fila][col]

    def inicializar_vecinos(self):
        for fila in self.nodos:
            for nodo in fila:
                nodo.inicializar_vecinos(self.nodos, self.filas)

    def reiniciar(self):
        for fila in self.nodos:
            for nodo in fila:
                nodo.restablecer()


class Message:
    def __init__(self, message: str):
        self.message = message
        self.shown = False
        self.counter = 0
        self.cool_down_secs = 3 * FPS

    def show(self):
        self.shown = True
        self.counter = 0

    def draw(self, ventana: pygame.Surface):
        if self.shown:
            if self.counter < self.cool_down_secs:
                self.counter += 1
                fuente = pygame.font.Font(None, 50)
                texto = fuente.render(self.message, True, BLANCO)
                rect_texto = texto.get_rect(
                    center=(ANCHO_VENTANA // 2, ANCHO_VENTANA // 2)
                )
                pygame.draw.rect(ventana, NEGRO, rect_texto.inflate(20, 20))
                ventana.blit(texto, rect_texto)
            else:
                self.shown = False


def obtener_click_pos(pos: Tuple[int, int], filas: int, ancho: float):
    ancho_nodo = ancho // filas
    y, x = pos
    fila = y // ancho_nodo
    col = x // ancho_nodo
    return fila, col


def heuristica_manhattan(tuple1: Tuple[int, int], tuple2: Tuple[int, int]):
    x1, y1 = tuple1
    x2, y2 = tuple2
    return abs(x1 - x2) + abs(y1 - y2)


def heuristica_euclidiana(tuple1: Tuple[int, int], tuple2: Tuple[int, int]):
    x1, y1 = tuple1
    x2, y2 = tuple2
    return sqrt((x1 - x2) ** 2) + ((y1 - y2) ** 2)


def reconstruir_camino(came_from: Dict[Nodo, Nodo], actual: Nodo):
    cerrada: List[Nodo] = []
    while actual in came_from:
        cerrada.append(actual)
        actual = came_from[actual]
        actual.hacer_camino()
    cerrada.reverse()

    print("Lista cerrada: ")
    for nodo in cerrada:
        print(f"Nodo:{nodo.col}, {nodo.fila}")


def main():
    FILAS = 10
    grid = Grid(FILAS, ANCHO_VENTANA)
    run = True
    algo_count = 0

    # Variables para el algoritmo
    active = False
    start = None
    end = None

    count = 0

    # Cola de prioridad
    open_set: PriorityQueue[Tuple[float, int, Nodo]] = PriorityQueue()

    # Diccionario para ver de donde vinieron los nodos
    came_from: Dict[Nodo, Nodo] = {}

    # Inicialización de los costos de g
    g_score: Dict[Nodo, float] = {}

    # Inicialización de los costos de f
    f_score: Dict[Nodo, float] = {}

    open_set_hash: Set[Nodo] = set()

    # Mensajes posibles
    not_found_message = Message(message="No se encontró el camino")
    found_message = Message(message="Se encontró el camino")

    def iniciar_algo():
        nonlocal active, start, end, count, open_set, g_score, f_score, open_set_hash, count, algo_count
        algo_count = 0
        active = True
        count = 0
        # Inicialización de los costos de g
        g_score = {nodo: float("inf") for fila in grid.nodos for nodo in fila}

        # Inicialización de los costos de f
        f_score = {nodo: float("inf") for fila in grid.nodos for nodo in fila}

        # Inicialización del diccionario de nodos
        open_set_hash = {start}

        # Inicialización del primer nodo
        open_set.put((0, count, start))
        g_score[start] = 0
        f_score[start] = heuristica_manhattan(start.get_pos(), end.get_pos())

    def a_asterisco():
        nonlocal active, start, end, count, open_set, came_from, g_score, f_score, open_set_hash
        if not open_set.empty():

            # Obtenemos el nodo actual segun la cola de prioridad
            current = open_set.get()[2]

            # Lo eliminamos del diccionario
            open_set_hash.remove(current)

            # Si llegamos al final, reconstruimos el camino
            if current == end:
                end.hacer_fin()
                reconstruir_camino(came_from, end)
                start.hacer_inicio()
                found_message.show()
                active = False
                return

            # Iteramos sobre los vecinos
            for vecino, costo in current.vecinos:
                # Nuevo costo de g
                tentative_g_score = g_score[current] + costo

                # Si el costo es menor, actualizamos los valores
                if tentative_g_score < g_score[vecino]:
                    came_from[vecino] = current
                    g_score[vecino] = tentative_g_score
                    f_score[vecino] = g_score[vecino] + heuristica_manhattan(
                        vecino.get_pos(), end.get_pos()
                    )
                    if vecino not in open_set_hash:
                        count += 1
                        open_set.put((f_score[vecino], count, vecino))
                        open_set_hash.add(vecino)
                        vecino.hacer_abierto()

            if current != start:
                current.hacer_cerrado()
        else:
            not_found_message.show()
            active = False

    def reiniciar():
        nonlocal start, end, not_found_message, found_message, active, g_score, f_score, open_set, open_set_hash, came_from
        start = None
        end = None
        not_found_message.shown = False
        found_message.shown = False
        active = False
        g_score = {}
        f_score = {}
        open_set = PriorityQueue()
        open_set_hash = set()
        came_from = {}
        grid.reiniciar()

    while run:
        # Capar fps
        clock.tick(FPS)
        # Eventos
        for event in pygame.event.get():

            # Salir del juego por X
            if event.type == pygame.QUIT:
                run = False

            # Click izquierdo
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ANCHO_VENTANA)
                nodo = grid.get_nodo((fila, col))
                if not start and nodo != end:
                    start = nodo
                    start.hacer_inicio()

                elif not end and nodo != start:
                    end = nodo
                    end.hacer_fin()

                elif nodo != end and nodo != start:
                    nodo.hacer_pared()

            # Click derecho
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ANCHO_VENTANA)
                nodo = grid.get_nodo((fila, col))
                nodo.restablecer()
                if nodo == start:
                    start = None
                elif nodo == end:
                    end = None

            # Eventos del teclado
            if event.type == pygame.KEYDOWN:

                # Evento para salir por medio del teclado
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    run = False

                # Evento para reiniciar
                if event.key == pygame.K_r:
                    reiniciar()

                # Evento para iniciar el algoritmo
                if event.key == pygame.K_SPACE and start and end:
                    grid.inicializar_vecinos()
                    iniciar_algo()

        # Dibujar todas las cosas
        grid.dibujar(VENTANA)

        # Dibujar mensajes
        not_found_message.draw(VENTANA)
        found_message.draw(VENTANA)

        # Si se activó el algoritmo
        if active:
            if algo_count % (FPS / STEPS_PER_SECOND) == 0:
                a_asterisco()
            algo_count += 1

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
