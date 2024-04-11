import numpy as np


class Polygon:
    def __init__(self, vertices):
        self.vertices = vertices
        self.normal = self.calculate_normal()

    def calculate_normal(self):
        v0 = np.array(self.vertices[0])
        v1 = np.array(self.vertices[1])
        v2 = np.array(self.vertices[2])
        return np.cross(v1 - v0, v2 - v0)


class BSPNode:
    def __init__(self, polygons):
        self.polygons = polygons
        self.front = None
        self.back = None
        self.partition_plane = None

    def build_tree(self):
        if len(self.polygons) == 0:
            return

        # wybieramy pierwszy wielokąt jako płaszczyzna podziału
        self.partition_plane = self.polygons[0]

        front_polygons = []
        back_polygons = []

        for polygon in self.polygons[1:]:
            if self.is_front(polygon):
                print(f'Polygon {polygon.vertices} is in front of polygon {self.partition_plane.vertices} with normal to {self.partition_plane.normal}')
                front_polygons.append(polygon)
            elif self.is_back(polygon):
                print(
                    f'Polygon {polygon.vertices} is in behind polygon {self.partition_plane.vertices} with normal to {self.partition_plane.normal}')
                back_polygons.append(polygon)
            else:
                # wielokąt przecina płaszczyznę podziału
                # dzielimy wielokąt na 2 części
                print(f'splitting {polygon.vertices}')
                front_part, back_part = self.split_polygon(polygon)
                if front_part:
                    print(f'added front after split {front_part.vertices}')
                    front_polygons.append(front_part)
                if back_part:
                    print(f'added back after split {back_part.vertices}')
                    back_polygons.append(back_part)

        # rekurencyjnie budujemy drzewo BSP
        if front_polygons:
            self.front = BSPNode(front_polygons)
            self.front.build_tree()

        if back_polygons:
            self.back = BSPNode(back_polygons)
            self.back.build_tree()

    def is_front(self, polygon):
        for vertex in polygon.vertices:
            if np.dot(np.array(vertex) - np.array(self.partition_plane.vertices[0]), self.partition_plane.normal) < 0:
                return False
        return True

    def is_back(self, polygon):
        for vertex in polygon.vertices:
            if np.dot(np.array(vertex) - np.array(self.partition_plane.vertices[0]), self.partition_plane.normal) > 0:
                return False
        return True

    def split_polygon(self, polygon):
        front_part = []
        back_part = []

        for i, vertex in enumerate(polygon.vertices):
            next_index = (i + 1) % len(polygon.vertices)

            current_vertex = np.array(vertex)
            next_vertex = np.array(polygon.vertices[next_index])

            # sprawdzenie, czy krawędź przecina płaszczyznę podziału
            current_dot = np.dot(current_vertex - np.array(self.partition_plane.vertices[0]),
                                 self.partition_plane.normal)
            next_dot = np.dot(next_vertex - np.array(self.partition_plane.vertices[0]), self.partition_plane.normal)

            if current_dot >= 0:
                front_part.append(current_vertex)
            else:
                back_part.append(current_vertex)

            # jeśli punkty na obu końcach krawędzi należą do różnych stron płaszczyzny, znajdź punkt przecięcia
            if current_dot * next_dot < 0:
                # obliczenie punktu przecięcia z płaszczyzną podziału
                t = current_dot / (current_dot - next_dot)
                intersection_point = current_vertex + t * (next_vertex - current_vertex)

                front_part.append(intersection_point)
                back_part.append(intersection_point)

        if front_part and back_part:
            return Polygon(front_part), Polygon(back_part)
        else:
            return None, None

    def traverse(self, camera_pos, camera_front):
        visible_polygons = []
        invisible_polygons = []

        if self.partition_plane is None:
            return []

        dot = np.dot(np.array(camera_pos) - np.array(self.partition_plane.vertices[0]), self.partition_plane.normal)

        if dot > 0:
            if self.front:
                visible_polygons.extend(self.front.traverse(camera_pos, camera_front))
            visible_polygons.append(self.partition_plane)
            if self.back:
                visible_polygons.extend(self.back.traverse(camera_pos, camera_front))
        else:
            if self.back:
                invisible_polygons.extend(self.back.traverse(camera_pos, camera_front))
            invisible_polygons.append(self.partition_plane)
            if self.front:
                invisible_polygons.extend(self.front.traverse(camera_pos, camera_front))

        return invisible_polygons + visible_polygons

    def print_tree(self, indent=0):
        prefix = "    " * indent
        print(prefix + "Partition Plane:", self.partition_plane.vertices if self.partition_plane else None, " normal:", self.partition_plane.normal if self.partition_plane else None)
        print(prefix + "Front:")
        if self.front:
            self.front.print_tree(indent + 1)
        else:
            print(prefix + "    (Empty)")
        print(prefix + "Back:")
        if self.back:
            self.back.print_tree(indent + 1)
        else:
            print(prefix + "    (Empty)")