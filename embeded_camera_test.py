import pygame
from pygame.locals import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# Inicjalizacja Pygame
pygame.init()
width, height = 1000, 800
screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
clock = pygame.time.Clock()

current_tick = 0

# Konfiguracja kamery
fov = 90.0
aspect = width / height
near = 0.1
far = 50.0
camera_pos = np.array([0, 0, 5], dtype=np.float64)
camera_front = np.array([0, 0, -1], dtype=np.float64)
camera_up = np.array([0, 1, 0], dtype=np.float64)

# Inicjalizacja OpenGL
col = 0.0
glClearColor(col, col, col, 1.0)
glEnable(GL_DEPTH_TEST)

# Przykładowe punkty w 3D
points = np.random.uniform(-2, 2, (100, 3))

# Funkcja do rysowania punktów
def draw_points():
    glBegin(GL_POINTS)
    for point in points:
        glVertex3fv(point)
    glEnd()

# Funkcja do rysowania osi
def draw_axes():
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(1, 0, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 1, 0)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1)
    glEnd()

# Funkcja do aktualizacji widoku kamery
def update_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, aspect, near, far)
    gluLookAt(*camera_pos, *(camera_pos + camera_front), *camera_up)
    glMatrixMode(GL_MODELVIEW)

def draw_text(text, position):
    font = pygame.font.Font(None, 36)  # Ustawienie czcionki i rozmiaru
    text_surface = font.render(text, True, (100, 100, 100))  # Renderowanie tekstu na powierzchni
    screen.blit(text_surface, position)

def get_lookat_matrix():
    # Inicjujemy tablicę o odpowiednim rozmiarze do przechowywania macierzy
    modelview_matrix = np.zeros(16, dtype=np.float32)

    # Uzyskujemy aktualną macierz model-view
    glGetFloatv(GL_PROJECTION_MATRIX, modelview_matrix)

    # Konwertujemy tablicę na macierz 4x4
    lookat_matrix = np.reshape(modelview_matrix, (4, 4))

    return lookat_matrix

# Główna pętla programu
running = True
keys_pressed = set()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)

    camera_speed = 0.08
    if pygame.K_w in keys_pressed:
        camera_pos += (camera_speed * camera_front)
    if pygame.K_s in keys_pressed:
        camera_pos -= (camera_speed * camera_front)
    if pygame.K_a in keys_pressed:
        camera_pos -= (np.cross(camera_front, camera_up) * camera_speed)
    if pygame.K_d in keys_pressed:
        camera_pos += (np.cross(camera_front, camera_up) * camera_speed)

    # Podnoszenie i opuszczanie kamery
    if pygame.K_SPACE in keys_pressed:
        camera_pos[1] += camera_speed
    if pygame.K_LSHIFT in keys_pressed:
        camera_pos[1] -= camera_speed

    cam_speed_2 = 0.03
    # pitch - góra dół -> obrót wokół osi X
    if pygame.K_UP in keys_pressed:
        camera_front[1] += cam_speed_2
    if pygame.K_DOWN in keys_pressed:
        camera_front[1] -= cam_speed_2

    # yaw - prawo lewo -> obrót wokół osi Y
    if pygame.K_LEFT in keys_pressed:
        camera_front[0] -= cam_speed_2
    if pygame.K_RIGHT in keys_pressed:
        camera_front[0] += cam_speed_2

    # roll - pochylenie -> obrót wokół osi Z
    if pygame.K_KP_PLUS in keys_pressed:
        camera_front[2] += cam_speed_2
    if pygame.K_KP_MINUS in keys_pressed:
        camera_front[2] -= cam_speed_2

    if pygame.K_m in keys_pressed:
        fov -= 1
    if pygame.K_n in keys_pressed:
        fov += 1

    if pygame.K_o in keys_pressed:
        camera_front[0] = -0.8
        camera_front[1] = -0.5
        camera_front[2] = -1

        camera_pos[0] = 1
        camera_pos[1] = 0.7
        camera_pos[2] = 1.5

    if pygame.K_p in keys_pressed:
        camera_front[0] = 1
        camera_front[1] = 1
        camera_front[2] = 1

        camera_pos[0] = 0
        camera_pos[1] = 0
        camera_pos[2] = -5

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    update_camera()
    draw_axes()
    draw_points()

    # current_tick = current_tick + 1
    # if current_tick % 40 == 0:
    #     current_tick = 0
    #     print(f"camera_pos: {camera_pos}, camera_front: {camera_front}")
    #     print(get_lookat_matrix())

    # print("LookAt matrix:")
    # print(get_lookat_matrix())

    # print(f'camera_pos: {camera_pos}    camera_front: {camera_front}     camera_up: {camera_up}')

    pitch = np.arcsin(-camera_front[1])
    yaw = np.arctan2(camera_front[0], camera_front[2])
    roll = np.arctan2(camera_up[0], camera_up[1])

    pitch_deg = np.degrees(pitch)
    yaw_deg = np.degrees(yaw)
    roll_deg = np.degrees(roll)

    # print(f'pitch: {pitch_deg}, yaw: {yaw_deg}, roll: {roll_deg}')
    # print(f'pitch: {pitch}, yaw: {yaw}, roll: {roll}')

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
