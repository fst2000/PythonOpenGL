import math
from functools import reduce
from operator import mul
import glfw

from OpenGL.GLUT import *
from OpenGL.GL import *

def length(vec): return math.sqrt(sum(map(lambda i: i * i), vec))

def angle(v1, v2): return math.acos(dot_vec(v1, v2) / length(v1) * length(v2))

def dot_vec(v1, v2): return sum(map(lambda a1, a2: a1 * a2, v1, v2))

def sum_vec(*vecs): return tuple(sum(values) for values in zip(*vecs))

def scale_vec(vec, scale): return tuple(map(lambda value: value * scale, vec))

def average_vec(*vecs): return scale_vec(sum_vec(vecs), len(vecs))

def cross(v1, v2): pass

def vertex(point, texcoord, normal): return {"point" : point, "texcoord": texcoord, "normal": normal}

def matrix(size : int): return enumerated_matrix(lambda i, j: 1 if i == j else 0, size)

def enumerated_matrix(function, size : int): return tuple(tuple(function(i, j) for j in range(size)) for i in range(size))

def map_matrix(function, matrix): return tuple(map(lambda row: tuple(map(lambda a: function(a), row)), matrix))

def transpose(m): return enumerated_matrix(lambda i, j: m[j[i]])

def column(matrix, idx : int): return tuple(map(lambda row: row[idx], matrix))

def dot_mat(m1, m2): return tuple(enumerated_matrix(lambda i, j: dot_vec(m1[i], column(m2, j)), len(m1)))

def dot_mat_vec(m, v):
    if len(v) < len(m): v = v + ((0,) * (len(m) - len(v) - 1) + (1, ))
    return tuple(dot_vec(row, v) for row in m)

def y_rot_mat(angle): return [
    [math.cos(angle), 0, math.sin(angle), 0],
    [0, 1, 0, 0],
    [-math.sin(angle), 0, math.cos(angle), 0],
    [0, 0, 0, 1]
    ]

def transform_face(matrix, face): return tuple(map(lambda v: vertex(dot_mat_vec(matrix, v["point"]), v["texcoord"], v["normal"]), face))

def transform_mesh(matrix, mesh): return tuple(map(lambda f: transform_face(matrix, f), mesh))

def mesh_from_obj(obj_file):
    lines = obj_file.split("\n")
    filtered_lines = lambda s: tuple(map(lambda line: line.replace(s, ""), filter(lambda line: line.startswith(s), lines)))
    floats_from_string = lambda l: tuple(map(lambda val: float(val), l.split()))
    points = tuple(map(floats_from_string, filtered_lines("v ")))
    texcoords = tuple(map(floats_from_string, filtered_lines("vt ")))
    normals = tuple(map(floats_from_string, filtered_lines("vn ")))
    vertex_from_ids = lambda v_id, vt_id, vn_id: vertex(points[v_id], texcoords[vt_id], normals[vn_id])
    face_from_line = lambda line: tuple(map(lambda ids_str: vertex_from_ids(*map(lambda id_str: int(id_str) - 1, ids_str.split("/"))), line.split()))
    return tuple(face_from_line(line) for line in filtered_lines("f "))

def draw_face(face, vertex_col_func):
    for vertex in face:
        glColor3f(*vertex_col_func(vertex))
        glVertex(*vertex["point"])

def normal(face):
    return

def draw(mesh, vertex_col_func):
    glBegin(GL_TRIANGLES)
    for face in mesh: draw_face(face, vertex_col_func)
    glEnd()

def start_window():
    window = glfw.create_window(1000, 1000, "draw_test", None, None)
    glfw.make_context_current(window)
    if not window:
        glfw.terminate()
        print("Glfw window can't be created")
        exit()
    return window

def main():
    glfw.init()
    window = start_window()
    glEnable(GL_DEPTH_TEST)
    angle = 0.0
    pyramid_mesh = mesh_from_obj(open("papa.obj").read())
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        transform_matrix = y_rot_mat(angle)
        draw(transform_mesh(
            transform_matrix, pyramid_mesh),
            lambda vertex: scale_vec((1.0, 1.0, 1.0), dot_vec(vertex["normal"], dot_mat_vec(transform_matrix, (0.0, 0.0, -1.0)))))
        angle += 0.01
        glfw.swap_buffers(window)
    glfw.terminate()
main()