import arcade
from arcade.gui import UIManager, UIAnchorWidget, UILabel
from arcade.experimental.uislider import UISlider
import math, random
import time
import numpy as np

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

class Point:
    def __init__(self, x, y, z):
        self.start_x, self.start_y, self.start_z = x, y, z
        self.x, self.y, self.z = self.start_x, self.start_y, self.start_z

    def rotate(self, rotation_matrix):
        start_position_vector = np.array([self.start_x, self.start_y, self.start_z])
        rotated_position_vector = np.matmul(start_position_vector, rotation_matrix)
        self.x = rotated_position_vector[0]
        self.y = rotated_position_vector[1]
        self.z = rotated_position_vector[2]

        """self.y = self.start_y * math.cos(x_theta) - math.sin(x_theta) * self.start_z
        self.z = self.start_y * math.sin(x_theta) + math.cos(x_theta) * self.start_z
        interim_z = self.z
        # Y rotation
        self.x = math.cos(y_theta) * self.start_x + math.sin(y_theta) * interim_z
        self.z = -math.sin(y_theta) * self.start_x + math.cos(y_theta) * interim_z
        interim_x = self.x
        # Z rotation
        self.x = interim_x * math.cos(z_theta) - math.sin(z_theta) * self.y
        self.y = interim_x * math.sin(z_theta) + math.cos(z_theta) * self.y"""

    def render(self, POV, center_coordinates):
        vector = (self.x+center_coordinates[0]-POV[0], self.y+center_coordinates[1]-POV[1], self.z+center_coordinates[2]-POV[2])
        if POV[2] != 0:
            parameter_value = (-POV[2]) / vector[2]
        else:
            parameter_value = 1/vector[2]
        display_x, display_y = (vector[0] * parameter_value+POV[0]+1)*SCREEN_WIDTH/2, (vector[
            1] * parameter_value+POV[1]+1)*SCREEN_HEIGHT/2 # man adderer med 1 af samme årsag som med matricen. Ellers er det fra -1:1, men ved at addere med 1 bliver det fra 0:2 og så kan man skalere ud fra skærmens størrelse.
        return ((display_x-100, display_y))

    def render_matrix(self, object_center, n=1, f=1000):
        perspective_projection_matrix = np.array([[n, 0, 0, 0], [0,n,0,0], [0,0,f+n,-f*n], [0,0,1,0]])
        x_global, y_global, z_global = self.x+object_center[0], self.y+object_center[1], self.z+object_center[2]
        point_homogen_vector = np.array([x_global, y_global, z_global, 1])
        perspective_vector_product = np.matmul(perspective_projection_matrix, point_homogen_vector)
        if perspective_vector_product[3] != 0:
            perspective_vector_product[0] /= perspective_vector_product[3]
            perspective_vector_product[1] /= perspective_vector_product[3]
            perspective_vector_product[2] /= perspective_vector_product[3]
        return(perspective_vector_product)

class Object:
    def __init__(self, center_coords, punkter, faces = []):
        self.points3D = punkter
        self.coords = list(center_coords)
        self.faces = []
        for face in faces:
            self.faces.append([face, (random.randint(0,255),random.randint(0,255),random.randint(0,255))])

        for i in range(len(self.points3D)):
            punkt = self.points3D[i]

    def rotate(self, x_theta, y_theta, z_theta):
        rotation_x = np.array(
            [[1, 0, 0], [0, math.cos(x_theta), math.sin(x_theta)], [0, -math.sin(x_theta), math.cos(x_theta)]])
        rotation_y = np.array(
            [[math.cos(y_theta), 0, -math.sin(y_theta)], [0, 1, 0], [math.sin(y_theta), 0, math.cos(y_theta)]])
        rotation_z = np.array(
            [[math.cos(z_theta), math.sin(z_theta), 0], [-math.sin(z_theta), math.cos(z_theta), 0], [0, 0, 1]])
        rotation_xy = np.matmul(rotation_x, rotation_y)
        rotation_xyz = np.matmul(rotation_xy, rotation_z)
        for punkt in self.points3D:
            punkt.rotate(rotation_xyz)

    def move(self, *vector):
        self.coords[0] += vector[0]
        self.coords[1] += vector[1]
        self.coords[2] += vector[2]

    def scale(self, *scale):
        for punkt in self.points3D:
            punkt.start_x *= scale[0]
            punkt.start_y *= scale[1]
            punkt.start_z *= scale[2]

    def render(self, POV):
        points2D = []
        for punkt in self.points3D:
            points2D.append(punkt.render(POV, self.coords))

        for face_list in self.faces:
            face = face_list[0]
            A_x = self.points3D[face[1]].x - self.points3D[face[0]].x
            B_x = self.points3D[face[2]].x - self.points3D[face[0]].x

            A_y = self.points3D[face[1]].y - self.points3D[face[0]].y
            B_y = self.points3D[face[2]].y - self.points3D[face[0]].y

            A_z = self.points3D[face[1]].z - self.points3D[face[0]].z
            B_z = self.points3D[face[2]].z - self.points3D[face[0]].z

            N_x = A_y*B_z-A_z*B_y
            N_y = A_z*B_x-A_x*B_z
            N_z = A_x*B_y-A_y*B_x
            if N_x*(self.points3D[face[0]].x+self.coords[0]-POV[0])+N_y*(self.points3D[face[0]].y+self.coords[1]-POV[1])+N_z*(self.points3D[face[0]].z+self.coords[2]-POV[2]) > 0:
                if len(face_list[0]) == 3:
                    arcade.draw_triangle_filled(points2D[face[0]][0], points2D[face[0]][1],
                                                points2D[face[1]][0], points2D[face[1]][1],
                                                points2D[face[2]][0], points2D[face[2]][1], face_list[1])
                else:
                    arcade.draw_triangle_filled(points2D[face[0]][0], points2D[face[0]][1],
                                                points2D[face[1]][0], points2D[face[1]][1],
                                                points2D[face[2]][0], points2D[face[2]][1], face_list[1])
                    arcade.draw_triangle_filled(points2D[face[3]][0], points2D[face[3]][1],
                                                points2D[face[1]][0], points2D[face[1]][1],
                                                points2D[face[2]][0], points2D[face[2]][1], face_list[1])

    def render_matrix(self, POV):
        points2D = []
        for punkt in self.points3D:
            projected_point = punkt.render_matrix(self.coords)
            projected_point[0] += 1
            projected_point[1] += 1
            projected_point[0]*=SCREEN_WIDTH/2
            projected_point[1]*=SCREEN_HEIGHT/2
            points2D.append(projected_point)

        faces_distances = []
        for face_list in self.faces:
            face = face_list[0]
            A_x = self.points3D[face[1]].x - self.points3D[face[0]].x
            B_x = self.points3D[face[2]].x - self.points3D[face[0]].x

            A_y = self.points3D[face[1]].y - self.points3D[face[0]].y
            B_y = self.points3D[face[2]].y - self.points3D[face[0]].y

            A_z = self.points3D[face[1]].z - self.points3D[face[0]].z
            B_z = self.points3D[face[2]].z - self.points3D[face[0]].z

            N_x = A_y * B_z - A_z * B_y
            N_y = A_z * B_x - A_x * B_z
            N_z = A_x * B_y - A_y * B_x

            if N_x * (self.points3D[face[0]].x + self.coords[0] - POV[0]) + N_y * (
                    self.points3D[face[0]].y + self.coords[1] - POV[1]) + N_z * (
                    self.points3D[face[0]].z + self.coords[2] - POV[2]) > 0:
                # Tegn fladen
                face_average_distance = (math.sqrt((POV[0] - (self.points3D[face[0]].x + self.coords[0])) ** 2 + (
                            POV[1] - (self.points3D[face[0]].y + self.coords[1])) ** 2 + (POV[2] - (
                            self.points3D[face[0]].z + self.coords[2])) ** 2) + math.sqrt(
                    (POV[0] - (self.points3D[face[1]].x + self.coords[0])) ** 2 + (
                                POV[1] - (self.points3D[face[1]].y + self.coords[1])) ** 2 + (
                                POV[2] - (self.points3D[face[1]].z + self.coords[2])) ** 2) + math.sqrt(
                    (POV[0] - (self.points3D[face[2]].x + self.coords[0])) ** 2 + (
                                POV[1] - (self.points3D[face[2]].y + self.coords[1])) ** 2 + (
                                POV[2] - (self.points3D[face[2]].z + self.coords[2])) ** 2)) / 3

                if len(faces_distances) == 0 or face_average_distance > faces_distances[0][0]:
                    faces_distances.insert(0, (face_average_distance, face, face_list[1]))

                else:
                    inserted = False
                    for face_distance_i in range(len(faces_distances)):
                        if face_average_distance <= faces_distances[face_distance_i][0] and len(
                                faces_distances) >= face_distance_i + 2 and face_average_distance >= \
                                faces_distances[face_distance_i + 1][0]:
                            inserted = True
                            faces_distances.insert(face_distance_i + 1, (face_average_distance, face, face_list[1]))
                            break
                    if not inserted:
                        faces_distances.append((face_average_distance, face, face_list[1]))

        for face_i in range(len(list(zip(*faces_distances))[1])):
            face = list(zip(*faces_distances))[1][face_i]
            face_color = list(zip(*faces_distances))[2][face_i]

            if len(face) == 3:
                arcade.draw_triangle_filled(points2D[face[0]][0], points2D[face[0]][1],
                                            points2D[face[1]][0], points2D[face[1]][1],
                                            points2D[face[2]][0], points2D[face[2]][1], face_color)
            else:
                print("2d", points2D[face[0]][0], points2D[face[0]][1], face_color)
                arcade.draw_triangle_filled(points2D[face[0]][0], points2D[face[0]][1],
                                            points2D[face[1]][0], points2D[face[1]][1],
                                            points2D[face[2]][0], points2D[face[2]][1], face_color)
                arcade.draw_triangle_filled(points2D[face[3]][0], points2D[face[3]][1],
                                            points2D[face[2]][0], points2D[face[2]][1],
                                            points2D[face[0]][0], points2D[face[0]][1], face_color)

class Vindue(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        cube = Object((0, 0, 3), [Point(-1, -1, 1), Point(1, -1, 1), Point(1, 1, 1), Point(-1, 1, 1), Point(-1, -1, -1),  Point(1, -1, -1), Point(1, 1, -1), Point(-1, 1, -1)], [[0, 2, 1], [0, 3, 2], [0, 7, 3], [0, 4, 7], [0, 1, 5], [0, 5, 4], [6, 2, 3], [6, 3, 7],[6, 1, 2],[6, 5, 1], [6, 4, 5], [6, 7, 4]])
        self.setup_ui()
        self.objects = [cube]
        #self.load_obj("./teapot.obj")
        self.POV = (0, 0, 0)
        self.time = 0

    def setup_ui(self):
        self.UI_manager = UIManager()
        self.UI_manager.enable()
        self.ui_sliders = []
        for i in range(3):
            if i == 1:
                slider = UISlider(value=0 * 100 / 360, width=150, height=25)
            elif i == 2:
                slider = UISlider(value=200 * 100 / 360, width=150, height=25)
            else:
                slider = UISlider(value=200 * 100 / 360, width=150, height=25)
            label = UILabel(text=("Rotation z", "Rotation y", "Rotation x")[i], text_color=(255,255,255), font_size=9)
            label_min = UILabel(text="0", text_color=(255,255,255), font_size=7)
            label_max = UILabel(text="2π", text_color=(255,255,255), font_size=7)
            self.ui_sliders.append(slider)
            self.UI_manager.add(UIAnchorWidget(child=label, align_x=-285, align_y=35 * (i + 1) - 235))
            self.UI_manager.add(UIAnchorWidget(child=label_min, align_x=-350, align_y=35 * (i + 1) - 238))
            self.UI_manager.add(UIAnchorWidget(child=label_max, align_x=-220, align_y=35 * (i + 1) - 235))
            self.UI_manager.add(UIAnchorWidget(child=slider, align_y=35 * -(i + 1) - 110, align_x=-285))

    def load_obj(self, path_to_file):
        punkter = []
        faces = []
        with open(path_to_file) as fil:
            for linje in fil:
                linje.replace(r"\n", "")
                linje_klippet = linje.split(" ")
                if linje_klippet[0] == "v":
                    punkter.append(Point(round(float(linje_klippet[2]),5), round(float(linje_klippet[3]),5), round(float(linje_klippet[4]),5)))
                elif linje_klippet[0] == "f":
                    if len(linje_klippet) == 5:
                        faces.append([int(math.fabs(int(linje_klippet[1].split("/")[0]))-1),int(math.fabs(int(linje_klippet[2].split("/")[0]))-1),int(math.fabs(int(linje_klippet[3].split("/")[0]))-1)])
                    else:
                        faces.append([int(linje_klippet[1].split("/")[0]) - 1, int(linje_klippet[2].split("/")[0]) - 1,
                                      int(linje_klippet[3].split("/")[0]) - 1, int(linje_klippet[4].split("/")[0]) - 1])

        object = Object((1, -50, 150), punkter, faces)
        object.scale(1, 1, 1)
        self.objects.append(object)


    def update(self, delta_time: float):
        self.time += delta_time
        for object in self.objects:
            object.rotate(2*math.pi*self.ui_sliders[0].value/100, 2*math.pi*self.ui_sliders[1].value/100, 2*math.pi*self.ui_sliders[2].value/100)
            #object.move(0, 0, math.cos(self.time))
            #object.scale(1, 1, 1+math.cos(self.time)/100)
            #object.scale(1+math.cos(self.time)/100, 1+math.sin(self.time)/100, 1-math.cos(self.time+math.pi/4)/100)
            pass

    def on_draw(self):
        self.clear()
        for object in self.objects:
            #object.render(self.POV)
            object.render_matrix(self.POV)
        self.UI_manager.draw()

if __name__ == "__main__":
    vindue = Vindue(SCREEN_WIDTH, SCREEN_HEIGHT, "SOP 3D program")
    arcade.run()