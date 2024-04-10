import pygame
import math
import numpy as np


pygame.init()
width, height = 1000, 800
pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

fov = 90.0
aspect = width / height
near = 0.1
far = 50.0
camera_pos = np.array([0, 0, 5], dtype=np.float64)
camera_up = np.array([0, 1, 0], dtype=np.float64)
camera_front = np.array([0, 0, -1], dtype=np.float64)
pitch, yaw, roll = 0, 180, 0

current_tick = 0


def load_polygons(file_path):
    polygons = []
    with open(file_path, "r") as f:
        for line in f:
            if line[0] != "#":
                line = line.split("#")[0]
                points = []
                for point_str in line.split("), ("):
                    point_str = point_str.replace("(", "").replace(")", "")
                    x, y, z = map(float, point_str.split(","))
                    points.append((x, y, z))
                if len(points) > 0:
                    polygons.append(points)
    return polygons


def draw_axes(screen):
    length = 0.8
    start = project_point(np.array([0, 0, 0]))
    end_x = project_point(np.array([length, 0, 0]))
    end_y = project_point(np.array([0, length, 0]))
    end_z = project_point(np.array([0, 0, length]))

    # print(f'start {start}   end_z {end_z}')

    if start is None:
        return

    if end_x is not None:
        pygame.draw.line(screen, (255, 0, 0), start, end_x, 2)  # Oś X - czerwona
    if end_y is not None:
        pygame.draw.line(screen, (0, 255, 0), start, end_y, 2)  # Oś Y - zielona
    if end_z is not None:
        pygame.draw.line(screen, (0, 0, 255), start, end_z, 2)  # Oś Z - niebieska


def magnitude(v):
    return math.sqrt(np.sum(v ** 2))


def normalize(v):
    m = magnitude(v)
    if m == 0:
        return v
    return v / m


def is_point_in_front_of_camera(point):
    camera_to_point = point - camera_pos
    dot_product = np.dot(camera_front, camera_to_point)
    return dot_product > 0


def build_view_matrix():
    forward = -normalize(camera_front)                  # oś Z
    right = normalize(np.cross(camera_up, forward))     # oś X
    up = np.cross(forward, right)                       # oś Y

    view_matrix = np.array([
        [right[0], right[1], right[2], -np.dot(right, camera_pos)],
        [up[0], up[1], up[2], -np.dot(up, camera_pos)],
        [forward[0], forward[1], forward[2], -np.dot(forward, camera_pos)],
        [0, 0, 0, 1]
    ])

    return view_matrix


def build_projection_matrix():
    projection_matrix = np.array([
        [1 / (aspect * math.tan(math.radians(fov) / 2)), 0, 0, 0],
        [0, 1 / math.tan(math.radians(fov) / 2), 0, 0],
        [0, 0, -1 * (far + near) / (far - near), -1 * (2 * far * near) / (far - near)],
        [0, 0, -1, 0]
    ])
    return projection_matrix


def project_point(point):
    if not is_point_in_front_of_camera(point):
        return None

    point = np.array([point[0], point[1], point[2], 1])

    view_matrix = build_view_matrix()
    projection_matrix = build_projection_matrix()
    transformation_matrix = np.dot(projection_matrix, view_matrix)

    transformed_point = np.dot(transformation_matrix, point)

    if transformed_point[3] == 0:
        transformed_point[3] = 0.001
    normalized_point = transformed_point / transformed_point[3]

    x_screen = int((normalized_point[0] + 1) * 0.5 * width)
    y_screen = int((1 - normalized_point[1]) * 0.5 * height)

    return x_screen, y_screen


# def calculate_camera_parameters_from_euler_angles():
#     global camera_front, camera_up
#
#     pitch_rad = np.radians(pitch)
#     yaw_rad = np.radians(yaw)
#     roll_rad = np.radians(roll)
#
#     front_x = math.cos(pitch_rad) * math.sin(yaw_rad)
#     front_y = math.sin(pitch_rad)
#     front_z = math.cos(pitch_rad) * math.cos(yaw_rad)
#     camera_front = np.array([front_x, front_y, front_z])
#     camera_front = normalize(camera_front)
#
#     world_up = np.array([0, 1, 0])
#     right = normalize(np.cross(world_up, camera_front))
#     camera_up = normalize(np.cross(camera_front, right))
#     roll_rotation_matrix = np.array([[math.cos(roll_rad), -math.sin(roll_rad), 0],
#                                      [math.sin(roll_rad), math.cos(roll_rad), 0],
#                                      [0, 0, 1]])
#     camera_up = np.dot(camera_up, roll_rotation_matrix)
#     camera_up = normalize(camera_up)

def draw_polygons(screen, polygons):
    for points in polygons:
        projected_points = []
        for point in points:
            projected_point = project_point(point)
            if projected_point is None:
                projected_points = []
                break
            projected_points.append(projected_point)
        if len(projected_points) > 0:
            pygame.draw.aalines(screen, (180, 180, 180), True, projected_points)


def rotate_vector_around_axis(vector, axis, angle):
    # Obliczenie macierzy obrotu
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    rotation_matrix = np.array([
        [cos_angle + (1 - cos_angle) * axis[0]**2, (1 - cos_angle) * axis[0] * axis[1] - sin_angle * axis[2], (1 - cos_angle) * axis[0] * axis[2] + sin_angle * axis[1]],
        [(1 - cos_angle) * axis[1] * axis[0] + sin_angle * axis[2], cos_angle + (1 - cos_angle) * axis[1]**2, (1 - cos_angle) * axis[1] * axis[2] - sin_angle * axis[0]],
        [(1 - cos_angle) * axis[2] * axis[0] - sin_angle * axis[1], (1 - cos_angle) * axis[2] * axis[1] + sin_angle * axis[0], cos_angle + (1 - cos_angle) * axis[2]**2]
    ])

    # Obliczenie przekształconego wektora
    rotated_vector = np.dot(rotation_matrix, vector)

    return rotated_vector


if __name__ == "__main__":
    polygons = load_polygons("polygons.txt")

    for i, points in enumerate(polygons):
        print(f'Polygon {i + 1}: {points}')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys_pressed = pygame.key.get_pressed()

        camera_movement_speed = 0.08
        if keys_pressed[pygame.K_w]:
            camera_pos += camera_movement_speed * camera_front
        if keys_pressed[pygame.K_s]:
            camera_pos -= camera_movement_speed * camera_front
        if keys_pressed[pygame.K_a]:
            camera_pos -= np.cross(camera_front, camera_up) * camera_movement_speed
        if keys_pressed[pygame.K_d]:
            camera_pos += np.cross(camera_front, camera_up) * camera_movement_speed

        if keys_pressed[pygame.K_SPACE]:
            camera_pos += camera_up * camera_movement_speed
        if keys_pressed[pygame.K_LSHIFT]:
            camera_pos -= camera_up * camera_movement_speed

        camera_rotation_speed = 0.05

        camera_right = np.cross(camera_front, camera_up)
        camera_right = normalize(camera_right)

        # góra/dół -> zmiana orientacji kamery wokół osi X
        if keys_pressed[pygame.K_DOWN]:
            camera_front = rotate_vector_around_axis(camera_front, camera_right, -camera_rotation_speed)
            camera_up = rotate_vector_around_axis(camera_up, camera_right, -camera_rotation_speed)
        if keys_pressed[pygame.K_UP]:
            camera_front = rotate_vector_around_axis(camera_front, camera_right, camera_rotation_speed)
            camera_up = rotate_vector_around_axis(camera_up, camera_right, camera_rotation_speed)

        # prawo lewo -> obrót wokół osi Y
        if keys_pressed[pygame.K_RIGHT]:
            camera_front = rotate_vector_around_axis(camera_front, camera_up, -camera_rotation_speed)
            camera_right = rotate_vector_around_axis(camera_right, camera_up, -camera_rotation_speed)
        if keys_pressed[pygame.K_LEFT]:
            camera_front = rotate_vector_around_axis(camera_front, camera_up, camera_rotation_speed)
            camera_right = rotate_vector_around_axis(camera_right, camera_up, camera_rotation_speed)

        # pochylenie -> obrót wokół osi Z
        if keys_pressed[pygame.K_e]:
            camera_front = rotate_vector_around_axis(camera_front, camera_front, camera_rotation_speed)
            camera_up = rotate_vector_around_axis(camera_up, camera_front, camera_rotation_speed)
        if keys_pressed[pygame.K_q]:
            camera_front = rotate_vector_around_axis(camera_front, camera_front, -camera_rotation_speed)
            camera_up = rotate_vector_around_axis(camera_up, camera_front, -camera_rotation_speed)

        if keys_pressed[pygame.K_m]:
            fov -= 1
            if fov < 1:
                fov = 1
        if keys_pressed[pygame.K_n]:
            fov += 1
            if fov >= 359:
                fov = 359

        # print(f'camera_pos: {camera_pos}    camera_front: {camera_front}     camera_up: {camera_up}')

        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))

        draw_axes(screen)
        draw_polygons(screen, polygons)

        current_tick = current_tick + 1
        if current_tick % 40 == 0:
            current_tick = 0
            pitch = np.degrees(np.arcsin(-camera_front[1]))
            yaw = np.degrees(np.arctan2(camera_front[0], camera_front[2]))
            roll = np.degrees(np.arctan2(camera_up[0], camera_up[1]))
            print(f"camera_pos: {camera_pos}, camera_front: {camera_front}, camera_up: {camera_up}, pitch: {pitch}, yaw: {yaw}, roll: {roll}, fov: {fov}")


        # draw_points(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
