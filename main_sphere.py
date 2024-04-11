import pygame
import numpy as np

pygame.init()
width, height = 1000, 800
centerX, centerY = width // 2, height // 2
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

light_pos = np.array([300, 200, 100], dtype=np.float64)  # Dodaliśmy trzecią współrzędną dla światła
light_color = np.array([255, 255, 255], dtype=np.float64)
ambient_color = np.array([50, 50, 50], dtype=np.float64)
diffuse_strength = 0.5      # siła składowej dyfuzyjnej
specular_strength = 0.5     # siła składowej zwierciadlanej
shininess = 64              # połysk powierzchni
ka = 0.9                    # współczynnik odbicia światła otoczenia (tła)
ks = 0.25                   # współczynnik odbicia światła kierunkowego
kd = 0.75                   # współczynnik odbicia światła rozproszonego

ball_radius = 150

current_material = 0


def phong_model(normal, view_dir, light_dir):
    ambient = ambient_color
    diffuse = diffuse_strength * max(np.dot(normal, light_dir), 0) * kd * light_color
    reflect_dir = 2 * np.dot(normal, light_dir) * normal - light_dir
    specular = specular_strength * max(np.dot(view_dir, reflect_dir), 0) ** shininess * ks * light_color
    return ambient + diffuse + specular


def draw_ball(screen):
    for y in range(centerY - ball_radius, centerY + ball_radius):
        for x in range(centerX - ball_radius, centerX + ball_radius):
            distance_sq = (x - centerX) ** 2 + (y - centerY) ** 2
            if distance_sq <= ball_radius ** 2:
                z = np.sqrt(ball_radius ** 2 - distance_sq)

                # normalizacja współrzędnych punktu na sferze do wektora normalnego
                normal = np.array([x - centerX, y - centerY, z], dtype=np.float64)
                normal /= np.linalg.norm(normal)

                view_dir = np.array([0, 0, 1], dtype=np.float64)  # kierunek widoku (patrzymy na kulę z przodu)

                light_dir = light_pos - np.array([x, y, 0], dtype=np.float64)  # kierunek światła
                light_dir /= np.linalg.norm(light_dir)

                color = phong_model(normal, view_dir, light_dir)
                color = tuple(int(max(min(c, 255), 0)) for c in color)

                screen.set_at((x, y), color)


def setup_material():
    global specular_strength, shininess, ambient_color
    print('Aktualnie wybrano kulkę:')
    if current_material == 0:
        specular_strength = 0.9
        shininess = 128
        ambient_color = (112, 112, 112)
        print('metalową')
    if current_material == 1:
        specular_strength = 0.6
        shininess = 16
        ambient_color = (235, 0, 0)
        print('pomalowaną farbą')
    if current_material == 2:
        specular_strength = 0.1
        shininess = 32
        ambient_color = (139, 69, 19)
        print('drewnianą')
    if current_material == 3:
        specular_strength = 0.5
        shininess = 64
        ambient_color = (10, 165, 180)
        print('plastikową')


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
            diffuse_strength -= 0.1
            if diffuse_strength < 0:
                diffuse_strength = 0
        if keys_pressed[pygame.K_m]:
            diffuse_strength += 0.1
            if diffuse_strength > 0.9:
                diffuse_strength = 0.9

        screen.fill((0, 0, 0))

        draw_ball(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
