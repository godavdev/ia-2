"""
    A asterix algorithm implementation
"""

from math import sqrt
from typing import List, Tuple
import pygame

# Configuraciones iniciales
ANCHO_VENTANA = 800
VENTANA = pygame.display.set_mode((ANCHO_VENTANA, ANCHO_VENTANA))
pygame.display.set_caption("Visualización de Nodos")

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)


class Nodo:
    """Nodo docstring"""

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

    def get_pos(self):
        """get_pos docstring"""
        return self.fila, self.col

    def es_pared(self):
        """es_pared docstring"""
        return self.color == NEGRO

    def es_inicio(self):
        """es_inicio docstring"""
        return self.color == NARANJA

    def es_fin(self):
        """es_fin docstring"""
        return self.color == PURPURA

    def restablecer(self):
        """restablecer docstring"""
        self.color = BLANCO

    def hacer_inicio(self):
        """hacer_inicio docstring"""
        self.color = NARANJA

    def hacer_pared(self):
        """hacer_pared docstring"""
        self.color = NEGRO

    def hacer_fin(self):
        """hacer_fin docstring"""
        self.color = PURPURA

    def dibujar(self, ventana: pygame.Surface):
        """dibujar docstring"""
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))


def crear_grid(filas: int, ancho: float) -> List[List[Nodo]]:
    """crear_grid docstring"""
    grid = []
    ancho_nodo = ancho // filas
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j, ancho_nodo)
            grid[i].append(nodo)
    return grid


def dibujar_grid(ventana: pygame.Surface, filas: int, ancho: float):
    """dibujar_grid docstring"""
    ancho_nodo = ancho // filas
    for i in range(filas):
        pygame.draw.line(ventana, GRIS, (0, i * ancho_nodo), (ancho, i * ancho_nodo))
        for j in range(filas):
            pygame.draw.line(
                ventana, GRIS, (j * ancho_nodo, 0), (j * ancho_nodo, ancho)
            )


def dibujar(ventana: pygame.Surface, grid: List[List[Nodo]], filas: int, ancho: float):
    """dibujar docstring"""
    ventana.fill(BLANCO)
    for fila in grid:
        for nodo in fila:
            nodo.dibujar(ventana)

    dibujar_grid(ventana, filas, ancho)
    pygame.display.update()


def obtener_click_pos(pos: Tuple[int, int], filas: int, ancho: float):
    """obtener_click_pos docstring"""
    ancho_nodo = ancho // filas
    y, x = pos
    fila = y // ancho_nodo
    col = x // ancho_nodo
    return fila, col


def heuristica_manhattan(nodo1: Nodo, nodo2: Nodo):
    """heuristica_manhattan docstring"""
    x1, y1 = nodo1.get_pos()
    x2, y2 = nodo2.get_pos()
    return abs(x1 - x2) + abs(y1 - y2)


def heuristica_euclidiana(nodo1: Nodo, nodo2: Nodo):
    """heuristica_euclidiana docstring"""
    x1, y1 = nodo1.get_pos()
    x2, y2 = nodo2.get_pos()
    return sqrt((x1 - x2) ** 2) + ((y1 - y2) ** 2)


def a_asterisco(inicio: Nodo, fin: Nodo, grid: List[List[Nodo]]):
    """a_asterisco docstring"""
    open_set: List[Nodo] = []
    open_set.append(inicio)


def main(ventana, ancho):
    """main docstring"""
    const FILAS = 10
    grid = crear_grid(FILAS, ancho)

    inicio = None
    fin = None

    corriendo = True

    while corriendo:
        dibujar(ventana, grid, FILAS, ancho)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if pygame.mouse.get_pressed()[0]:  # Click izquierdo
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
                nodo = grid[fila][col]
                if not inicio and nodo != fin:
                    inicio = nodo
                    inicio.hacer_inicio()

                elif not fin and nodo != inicio:
                    fin = nodo
                    fin.hacer_fin()

                elif nodo != fin and nodo != inicio:
                    nodo.hacer_pared()

            elif pygame.mouse.get_pressed()[2]:  # Click derecho
                pos = pygame.mouse.get_pos()
                fila, col = obtener_click_pos(pos, FILAS, ancho)
                nodo = grid[fila][col]
                nodo.restablecer()
                if nodo == inicio:
                    inicio = None
                elif nodo == fin:
                    fin = None

    pygame.quit()


main(VENTANA, ANCHO_VENTANA)
