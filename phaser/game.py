# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=global-variable-not-assigned
# pylint: disable=global-statement
import random
import pygame
import pandas as pd
import numpy as np
from keras._tf_keras.keras.models import Sequential
from keras._tf_keras.keras.layers import Dense
from sklearn.tree import DecisionTreeClassifier

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
w, h = 800, 400
pantalla = pygame.display.set_mode((w, h))
pygame.display.set_caption("Juego: Disparo de Bala, Salto, Nave y Menú")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Variables del jugador, bala, nave, fondo, etc.
jugador = None
bala = None
fondo = None
nave = None
menu = None

# Variables de salto
salto = False
salto_altura = 15  # Velocidad inicial de salto
gravedad = 1
en_suelo = True

# Variables de pausa y menú
pausa = False
fuente = pygame.font.SysFont("Arial", 24)
menu_activo = True
modo_auto = False  # Indica si el modo de juego es automático

# Lista para guardar los datos de velocidad, distancia y salto (target)
datos_modelo = []

# Cargar las imágenes
jugador_frames = [
    pygame.image.load("phaser/assets/sprites/mono_frame_1.png"),
    pygame.image.load("phaser/assets/sprites/mono_frame_2.png"),
    pygame.image.load("phaser/assets/sprites/mono_frame_3.png"),
    pygame.image.load("phaser/assets/sprites/mono_frame_4.png"),
]

bala_img = pygame.image.load("phaser/assets/sprites/purple_ball.png")
fondo_img = pygame.image.load("phaser/assets/game/fondo2.png")
nave_img = pygame.image.load("phaser/assets/game/ufo.png")
menu_img = pygame.image.load("phaser/assets/game/menu.png")

# Escalar la imagen de fondo para que coincida con el tamaño de la pantalla
fondo_img = pygame.transform.scale(fondo_img, (w, h))

# Crear el rectángulo del jugador y de la bala
jugador = pygame.Rect(50, h - 100, 32, 48)
bala = pygame.Rect(w - 50, h - 90, 16, 16)
nave = pygame.Rect(w - 100, h - 100, 64, 64)
menu_rect = pygame.Rect(w // 2 - 135, h // 2 - 90, 270, 180)  # Tamaño del menú

# Variables para la animación del jugador
current_frame = 0
frame_speed = 10  # Cuántos frames antes de cambiar a la siguiente imagen
frame_count = 0

# Variables para la bala
velocidad_bala = -10  # Velocidad de la bala hacia la izquierda
bala_disparada = False

# Variables para el fondo en movimiento
fondo_x1 = 0
fondo_x2 = w

selected_model = None

# Inicialización de NN
nn_model = Sequential(
    [
        Dense(4, input_dim=2, activation="relu"),
        Dense(1, activation="sigmoid"),
    ]
)
nn_model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])


def train_nn():
    global nn_model, datos_modelo
    X = np.array([x[:2] for x in datos_modelo])
    y = np.array([x[2] for x in datos_modelo])
    nn_model.fit(X, y, epochs=1000, batch_size=1, verbose=1)


# Inicialización de Árbol de Decisión
dt_model = DecisionTreeClassifier(random_state=42, max_depth=1)


def train_dt():
    global dt_model, datos_modelo
    X = np.array([x[:2] for x in datos_modelo])
    y = np.array([x[2] for x in datos_modelo])
    dt_model.fit(X, y)


# Función para disparar la bala
def disparar_bala():
    global bala_disparada, velocidad_bala  # pylint: disable=global-statement
    if not bala_disparada:
        velocidad_bala = random.randint(
            -8, -3
        )  # Velocidad aleatoria negativa para la bala
        bala_disparada = True


# Función para reiniciar la posición de la bala
def reset_bala():
    global bala, bala_disparada
    bala.x = w - 50  # Reiniciar la posición de la bala
    bala_disparada = False


# Función para manejar el salto
def manejar_salto():
    global jugador, salto, salto_altura, gravedad, en_suelo

    if salto:
        jugador.y -= salto_altura  # Mover al jugador hacia arriba
        salto_altura -= gravedad  # Aplicar gravedad (reduce la velocidad del salto)

        # Si el jugador llega al suelo, detener el salto
        if jugador.y >= h - 100:
            jugador.y = h - 100
            salto = False
            salto_altura = 15  # Restablecer la velocidad de salto
            en_suelo = True


# Función para actualizar el juego
def update():
    global bala, velocidad_bala, current_frame, frame_count, fondo_x1, fondo_x2

    # Mover el fondo
    fondo_x1 -= 1
    fondo_x2 -= 1

    # Si el primer fondo sale de la pantalla, lo movemos detrás del segundo
    if fondo_x1 <= -w:
        fondo_x1 = w

    # Si el segundo fondo sale de la pantalla, lo movemos detrás del primero
    if fondo_x2 <= -w:
        fondo_x2 = w

    # Dibujar los fondos
    pantalla.blit(fondo_img, (fondo_x1, 0))
    pantalla.blit(fondo_img, (fondo_x2, 0))

    # Animación del jugador
    frame_count += 1
    if frame_count >= frame_speed:
        current_frame = (current_frame + 1) % len(jugador_frames)
        frame_count = 0

    # Dibujar el jugador con la animación
    pantalla.blit(jugador_frames[current_frame], (jugador.x, jugador.y))

    # Dibujar la nave
    pantalla.blit(nave_img, (nave.x, nave.y))

    # Mover y dibujar la bala
    if bala_disparada:
        bala.x += velocidad_bala

    # Si la bala sale de la pantalla, reiniciar su posición
    if bala.x < 0:
        reset_bala()

    pantalla.blit(bala_img, (bala.x, bala.y))

    # Colisión entre la bala y el jugador
    if jugador.colliderect(bala):
        reiniciar_juego()  # Terminar el juego y mostrar el menú


# Función para guardar datos del modelo en modo manual
def guardar_datos():
    global jugador, bala, velocidad_bala, salto
    distancia = abs(jugador.x - bala.x)
    salto_hecho = 1 if salto else 0  # 1 si saltó, 0 si no saltó
    # Guardar velocidad de la bala, distancia al jugador y si saltó o no
    datos_modelo.append((velocidad_bala, distancia, salto_hecho))


# Función para pausar el juego y guardar los datos
def pausa_juego():
    global pausa
    pausa = not pausa
    if pausa:
        print("Juego pausado. Datos registrados hasta ahora:", datos_modelo)
    else:
        print("Juego reanudado.")


# Función para mostrar el menú y seleccionar el modo de juego
def mostrar_menu():
    global menu_activo, modo_auto, selected_model, datos_modelo
    pantalla.fill(NEGRO)
    has_data = len(datos_modelo) > 0
    print(has_data)
    txt = (
        "Presiona 'M' para Manual, o 'Q' para Salir"
        if not has_data
        else "Presiona 'N' para Red, 'T' para Arbol, 'M' para Manual, o 'Q' para Salir"
    )
    texto = fuente.render(
        txt,
        True,
        BLANCO,
    )
    texto_rect = texto.get_rect(center=(w // 2, h // 2))
    pantalla.blit(texto, texto_rect)
    pygame.display.flip()

    while menu_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if has_data and (evento.key == pygame.K_n or evento.key == pygame.K_t):
                    if evento.key == pygame.K_n:
                        train_nn()
                        selected_model = "nn"
                    else:
                        train_dt()
                        selected_model = "dt"
                    # selected_model = "nn" if evento.key == pygame.K_n else "dt"
                    modo_auto = True
                    menu_activo = False
                elif evento.key == pygame.K_m:
                    datos_modelo.clear()
                    modo_auto = False
                    menu_activo = False
                elif evento.key == pygame.K_q:
                    print("Juego terminado. Datos recopilados:", datos_modelo)
                    pygame.quit()
                    exit()


# Función para cargar los datos del juego
def load_data():
    global datos_modelo
    df = pd.read_csv("phaser/data/data.csv", header=None)
    datos_modelo = [tuple(map(int, row)) for row in df.values]


# Función para guardar los datos del juego
def save_data():
    df = pd.DataFrame(
        datos_modelo,
        # columns=["Velocidad", "Distancia", "Saltando"]
    )
    df.to_csv("phaser/data/data.csv", index=False, header=False)


# Función para reiniciar el juego tras la colisión
def reiniciar_juego():
    global menu_activo, jugador, bala, nave, bala_disparada, salto, en_suelo
    menu_activo = True  # Activar de nuevo el menú
    jugador.x, jugador.y = 50, h - 100  # Reiniciar posición del jugador
    bala.x = w - 50  # Reiniciar posición de la bala
    nave.x, nave.y = w - 100, h - 100  # Reiniciar posición de la nave
    bala_disparada = False
    salto = False
    en_suelo = True
    # # Mostrar los datos recopilados hasta el momento
    # print("Datos recopilados para el modelo: ", datos_modelo)
    mostrar_menu()  # Mostrar el menú de nuevo para seleccionar modo


# Funcion para predecir si es que va a saltar
def predict_jump():
    global jugador, bala, velocidad_bala, nn_model, dt_model, selected_model
    distancia = abs(jugador.x - bala.x)
    formatted = np.array([[velocidad_bala, distancia]])
    if selected_model == "nn":
        res = nn_model.predict(formatted, verbose=0)[0][0]
        rounded = int(np.round(res))
        return True if rounded == 1 else False
    if selected_model == "dt":
        res = dt_model.predict(formatted)[0]
        return True if res == 1 else False


def main():
    global salto, en_suelo, bala_disparada
    # load_data()  # Cargar los datos del juego
    reloj = pygame.time.Clock()
    mostrar_menu()  # Mostrar el menú al inicio
    correr = True

    while correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                correr = False
            if evento.type == pygame.KEYDOWN:
                if (
                    evento.key == pygame.K_SPACE and en_suelo and not pausa
                ):  # Detectar la tecla espacio para saltar
                    salto = True
                    en_suelo = False
                if evento.key == pygame.K_p:  # Presiona 'p' para pausar el juego
                    pausa_juego()
                if evento.key == pygame.K_q:  # Presiona 'q' para terminar el juego
                    pygame.quit()
                    exit()
                if evento.key == pygame.K_r:
                    reiniciar_juego()

        if not pausa:
            # Modo manual: el jugador controla el salto
            if not modo_auto:
                if salto:
                    manejar_salto()
                # Guardar los datos si estamos en modo manual
                guardar_datos()
            # Modo automático: el salto se activa automáticamente
            if modo_auto:
                if predict_jump():
                    salto = True
                    en_suelo = False
                if salto:
                    manejar_salto()

            # Actualizar el juego
            if not bala_disparada:
                disparar_bala()
            update()

        # Actualizar la pantalla
        pygame.display.flip()
        reloj.tick(30)  # Limitar el juego a 30 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
