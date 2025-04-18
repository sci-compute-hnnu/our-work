import numpy as np
from collections import Counter


# 判断该cell是tetrahedron或者quadrilateral  (points: (-1 ,3)  cells: (-1, 4))
def determine_tetra_or_quad(points, cells):

    if cells.shape[1] != 4:
        raise ValueError("Cells must have exactly 4 vertices per cell.")

    cell = cells[0]
    # 获取当前单元的顶点坐标
    vertices = points[cell]

    # 计算四点是否共面：通过构造三个向量计算混合积
    vec1 = vertices[1] - vertices[0]
    vec2 = vertices[2] - vertices[0]
    vec3 = vertices[3] - vertices[0]

    # 混合积：vec1 · (vec2 × vec3)
    mixed_product = np.dot(vec1, np.cross(vec2, vec3))

    # 如果混合积接近零，说明四点共面
    if not abs(mixed_product - 0.0) < 10e-5:
        return "tetrahedron"
    else:
        return "quadrilateral"



# 用于计算每个顶点的法向量
def calculate_vertex_normals(vertices, faces):


    # 用于计算每个面的法向量
    def calculate_face_normals(vertices, faces):

        # 计算面法线
        FN = np.zeros((len(faces), 3), dtype=np.float32)
        for i, f in enumerate(faces):
            v1 = vertices[f[1]] - vertices[f[0]]
            v2 = vertices[f[2]] - vertices[f[0]]
            FN[i] = np.cross(v1, v2)
            FN[i] = FN[i] / np.linalg.norm(FN[i])
        return FN

    # 计算面法向量
    face_normals = calculate_face_normals(vertices, faces)

    # 计算顶点法向量
    VN = np.zeros(vertices.shape, dtype=np.float32)

    for i in range(len(vertices)):
        faces_using = np.where(faces == i)[0]
        for j in faces_using:
            VN[i] += face_normals[j]
        VN[i] = VN[i] / np.linalg.norm(VN[i])
    return VN



# 提取边元素
def extract_edges(cells, cell_type):
    """
    提取网格的边

    参数:
    cells 网格单元  shape: (n_cells, num_vector_cell) num_vector_cell e.g. triangle:3 quadrilateral:4
    cell_type  单元类型  可选['triangle', 'quadrilateral', 'tetrahedron', 'hexahedron']

    返回:
    edges 边单元  shape: (n_edges, 2)
    """
    edges = set()
    if cell_type == 'triangle':
        for tri in cells:
            edges.update([
                tuple(sorted((tri[0], tri[1]))),
                tuple(sorted((tri[1], tri[2]))),
                tuple(sorted((tri[2], tri[0])))
            ])
    elif cell_type == 'quadrilateral':
        for quad in cells:
            edges.update([
                tuple(sorted((quad[0], quad[1]))),
                tuple(sorted((quad[1], quad[2]))),
                tuple(sorted((quad[2], quad[3]))),
                tuple(sorted((quad[3], quad[0])))
            ])
    elif cell_type == 'tetrahedron':
        for tet in cells:
            edges.update([
                tuple(sorted((tet[0], tet[1]))),
                tuple(sorted((tet[0], tet[2]))),
                tuple(sorted((tet[0], tet[3]))),
                tuple(sorted((tet[1], tet[2]))),
                tuple(sorted((tet[1], tet[3]))),
                tuple(sorted((tet[2], tet[3])))
            ])
    elif cell_type == 'hexahedron':
        for hex in cells:
            edges.update([
                tuple(sorted((hex[0], hex[1]))),
                tuple(sorted((hex[1], hex[2]))),
                tuple(sorted((hex[2], hex[3]))),
                tuple(sorted((hex[3], hex[0]))),
                tuple(sorted((hex[4], hex[5]))),
                tuple(sorted((hex[5], hex[6]))),
                tuple(sorted((hex[6], hex[7]))),
                tuple(sorted((hex[7], hex[4]))),
                tuple(sorted((hex[0], hex[4]))),
                tuple(sorted((hex[1], hex[5]))),
                tuple(sorted((hex[2], hex[6]))),
                tuple(sorted((hex[3], hex[7])))
            ])
    else:
        raise ValueError("Invalid cell type. Only ['triangle', 'quadrilateral', 'tetrahedron', 'hexahedron'] are supported.")

    # 可以继续添加其他类型单元的边提取方法

    # 将边转换为 NumPy 数组
    edges = np.array(list(edges), dtype=np.uint32)
    return edges


def extract_faces(cells, cell_type):
    """
    根据单元类型提取面

    参数:
    cells: 体网格单元  shape: (n_cells, num_vector_cell) num_vector_cell e.g. tetrahedron:4 hexahedron:8
    cell_type  单元类型  可选['tetrahedron', 'hexahedron']

    返回:
    faces: 面单元  shape: (n_faces, num_vector_face)  num_vector_face e.g. triangle:3 quadrilateral:4
    """
    faces = []
    if cell_type == 'tetrahedron':
        for tet in cells:
            # 提取四面体的面
            faces.extend([
                [tet[0], tet[1], tet[2]],  # 三角形面
                [tet[0], tet[1], tet[3]],
                [tet[0], tet[2], tet[3]],
                [tet[1], tet[2], tet[3]],
            ])
    elif cell_type == 'hexahedron':
        for hex in cells:
            # 提取六面体的面
            faces.extend([
                [hex[0], hex[1], hex[2], hex[3]],  # 四边形面
                [hex[4], hex[5], hex[6], hex[7]],
                [hex[0], hex[1], hex[5], hex[4]],
                [hex[2], hex[3], hex[7], hex[6]],
                [hex[1], hex[2], hex[6], hex[5]],
                [hex[3], hex[0], hex[4], hex[7]],
            ])
    else:
        raise ValueError("Invalid cell type. Only ['tetrahedron', 'hexahedron'] are supported.")

    return np.array(faces, dtype=np.uint32)



def check_point_order(face_vertices, reference_direction):
    v1 = face_vertices[1] - face_vertices[0]
    v2 = face_vertices[2] - face_vertices[0]
    normal = np.cross(v1, v2)
    return np.dot(normal, reference_direction) < 0


def get_faces_from_volume_mesh(cells, vertices):
    """
    根据体网格单元提取边界面

    参数:
    cells: 体网格单元  shape: (n_cells, num_vector_cell) num_vector_cell e.g. tetrahedron:4 hexahedron:8
    cell_type  单元类型  可选['tetrahedron', 'hexahedron']
    vertices: 顶点数组 shape: (n_vertices, 3)，每个顶点是一个三维坐标 (x, y, z)

    返回:
    faces: 面单元  shape: (n_faces, 3)，每个面由三个顶点的索引定义
    """
    # 将cells的每三个元素转换为一个面
    # 将cells进行unflatten处理
    faces = cells.reshape(-1, 3)


    # 将每个面转换为元组（如果顶点顺序可能不同而表示同一面，则使用 sorted(tuple(face))）
    face_tuples = [tuple(sorted(face)) for face in faces]

    # 使用 Counter 快速统计每个面出现的次数
    face_counts = Counter(face_tuples)

    # 只保留出现次数为 1 的面，即边界面
    boundary_face_tuples = [face for face, count in face_counts.items() if count == 1]

    # 计算整体的参考方向，例如使用所有顶点的中心到某个顶点的方向
    center = np.mean(vertices, axis=0)
    reference_direction = vertices[0] - center
    reference_direction = reference_direction / np.linalg.norm(reference_direction)

    # 判断面的顶点是否逆时针排序
    boundary_face = []
    for face in boundary_face_tuples:
        face = list(face)
        if not check_point_order(vertices[face], reference_direction):
            face = [face[0], face[2], face[1]]
        boundary_face.append(face)


    # 将boundary_faces转换为np.array
    boundary_face = np.array(boundary_face, dtype=np.uint32)



    return np.array(boundary_face, dtype=np.uint32)



