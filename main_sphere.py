import math

import pygame
import numpy as np

pygame.init()
width, height = 1000, 800
centerX, centerY = width // 2, height // 2
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# specular_strength = 0.5     # siła składowej zwierciadlanej
light_pos = np.array([300, 200, 100], dtype=np.float64)  # Dodaliśmy trzecią współrzędną dla światła
light_color = np.array([255, 255, 255], dtype=np.float64)
distance_attenuation = 0.4  # współczynnik tłumienia źródła z odległością (f_att)

ambient_color = (50, 50, 50)
ka = 1.0                    # współczynnik odbicia światła otoczenia (tła)
ks = 0.25                   # współczynnik odbicia światła kierunkowego
kd = 0.75                   # współczynnik odbicia światła rozproszonego
shininess = 50              # współczynnik n potęgi cos(alfa)

ball_radius = 75
ball_scale_factor = 2

current_material = 0


def setup_material():
    global ks, kd, ka, shininess, ambient_color
    print('Aktualnie wybrano kulkę:')
    if current_material == 0:
        ka = 0.19225
        ks = 0.508273
        kd = 0.50754
        shininess = 51.2
        ambient_color = (112, 112, 112)
        print('metalową (srebro)')
    if current_material == 1:
        ka = 0.1
        ks = 0.5
        kd = 0.6
        shininess = 64
        ambient_color = (235, 20, 20)
        print('pomalowaną farbą')
    if current_material == 2:
        ka = 0.05
        ks = 0.2
        kd = 0.6
        shininess = 32
        ambient_color = (139, 69, 19)
        print('drewnianą')
    if current_material == 3:
        ka = 0.2
        ks = 0.3
        kd = 0.7
        shininess = 128
        ambient_color = (10, 165, 180)
        print('plastikową')


def toggle_ball_quality():
    global ball_radius, ball_scale_factor
    if ball_radius == 75:
        print('Dostosowano do lepszej jakości')
        ball_radius = 150
        ball_scale_factor = 1
    else:
        print('Dostosowano do większej szybkości')
        ball_radius = 75
        ball_scale_factor = 2


def phong_model(normal, view_dir, light_dir):
    ambient = ka * np.array(ambient_color)
    diffuse = distance_attenuation * max(np.dot(normal, light_dir), 0) * kd * light_color

    reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir

    # krótszy sposób
    specular = max(np.dot(view_dir, reflect_dir), 0) ** shininess * ks * light_color #* specular_strength

    # sposób z wykorzystaniem cos(alfa)
    # obliczamy kąt między wektorem odbitego światła (reflect_dir) a wektorem widoku (view_dir)
    cos_alpha = np.dot(view_dir, reflect_dir) / (np.linalg.norm(view_dir) * np.linalg.norm(reflect_dir))
    alpha = math.acos(max(cos_alpha, 0))  # Uwzględnienie ograniczenia, aby wartość była między 0 a π
    specular = distance_attenuation * light_color * ks * math.cos(alpha) ** shininess

    return ambient + diffuse + specular


def draw_ball(screen):
    real_radius = ball_radius * ball_scale_factor
    for y in range(centerY - real_radius, centerY + real_radius, ball_scale_factor):
        for x in range(centerX - real_radius, centerX + real_radius, ball_scale_factor):
            distance_sq = (x - centerX) ** 2 + (y - centerY) ** 2
            if distance_sq <= real_radius ** 2:
                z = np.sqrt(real_radius ** 2 - distance_sq)

                # normalizacja współrzędnych punktu na sferze do wektora normalnego
                normal = np.array([x - centerX, y - centerY, z], dtype=np.float64)
                normal /= np.linalg.norm(normal)

                view_dir = np.array([0, 0, 1], dtype=np.float64)  # kierunek widoku (patrzymy na kulę z przodu)

                light_dir = light_pos - np.array([x, y, 0], dtype=np.float64)  # kierunek światła
                light_dir /= np.linalg.norm(light_dir)

                color = phong_model(normal, view_dir, light_dir)
                color = tuple(int(max(min(c, 255), 0)) for c in color)

                # screen.set_at((x, y), color)
                pygame.draw.circle(screen, color, (x, y), ball_scale_factor)


def next_material():
    global current_material
    current_material += 1
    if current_material > 3:
        current_material = 0
    setup_material()


if __name__ == "__main__":
    setup_material()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    next_material()
                if event.key == pygame.K_o:
                    toggle_ball_quality()

        keys_pressed = pygame.key.get_pressed()
        speed = 30
        if keys_pressed[pygame.K_UP]:
            light_pos[1] -= speed
        if keys_pressed[pygame.K_DOWN]:
            light_pos[1] += speed
        if keys_pressed[pygame.K_LEFT]:
            light_pos[0] -= speed
        if keys_pressed[pygame.K_RIGHT]:
            light_pos[0] += speed
        if keys_pressed[pygame.K_n]:
            distance_attenuation -= 0.1
            if distance_attenuation < 0:
                distance_attenuation = 0
        if keys_pressed[pygame.K_m]:
            distance_attenuation += 0.1
            if distance_attenuation > 0.9:
                distance_attenuation = 0.9

        screen.fill((0, 0, 0))

        draw_ball(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
