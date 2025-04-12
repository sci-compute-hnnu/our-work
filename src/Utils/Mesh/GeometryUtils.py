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
def calculate_vertex_normals(vertices, faces, plane=None):
    # 用于计算每个面的法向量
    def calculate_face_normals(vertices, faces):
        # 计算面法线
        FN = np.zeros((len(faces), 3), dtype=np.float32)
        for i, f in enumerate(faces):
            v1 = vertices[f[1]] - vertices[f[0]]
            v2 = vertices[f[2]] - vertices[f[0]]
            FN[i] = np.cross(v1, v2)
            if np.linalg.norm(FN[i]) == 0:
                FN[i] = np.array([0, 0, 0], dtype=np.float32)
            else:
                FN[i] = FN[i] / np.linalg.norm(FN[i])
        return FN

    # 计算面法向量
    face_normals = calculate_face_normals(vertices, faces)

    # 计算顶点法向量
    VN = np.zeros(vertices.shape, dtype=np.float32)

    for i in range(len(vertices)):
        if plane is not None:
            a, b, c, d = plane
            x, y, z = vertices[i]
            if abs(a * x + b * y + c * z + d) < 1e-6:
                VN[i] = np.array([a, b, c], dtype=np.float32)
                continue
        faces_using = np.where(faces == i)[0]
        for j in faces_using:
            VN[i] += face_normals[j]
        if np.linalg.norm(VN[i]) != 0:
            VN[i] = VN[i] / np.linalg.norm(VN[i])
        else:
            VN[i] = np.mean(face_normals, axis=0)

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

def wireframe_data(vertices, faces):
    """
    :param vertices: 包含正方体和内部几何体的所有顶点坐标数组，形状为 (n, 3)
    :param faces: 所有面的顶点索引数组，形状为 (m, 3)
    :return: 内部几何体的面以及正方体的边
    """
    # 首先计算出这个正方体的中心点
    center = np.mean(vertices, axis=0)
    # 找出距离这个正方体中心点最远的八个点的索引
    distances = np.linalg.norm(vertices - center, axis=1)
    farthest_indices = np.argsort(distances)[-8:]

    # 将这8个点连接成12条边，将这个顶点的索引两两连接构成一条边
    edges = []
    for i in range(8):
        for j in range(i + 1, 8):
            edges.append((farthest_indices[i], farthest_indices[j]))
    # 取出这些边距离最短的12条边
    edges = sorted(edges, key=lambda x: np.linalg.norm(vertices[x[0]] - vertices[x[1]]))[:12]
    cube_edges = np.array(edges, dtype=np.uint32)

    # 将正方体的八个点的坐标中心点移动到原点
    vertices = vertices - center
    # 计算正方体的边界
    min_x, max_x = np.min(vertices[:, 0]), np.max(vertices[:, 0])
    min_y, max_y = np.min(vertices[:, 1]), np.max(vertices[:, 1])
    min_z, max_z = np.min(vertices[:, 2]), np.max(vertices[:, 2])
    # 对上面的min_x, max_x,min_y, max_y, min_z, max_z保留两位小数
    min_x = round(min_x, 2)
    max_x = round(max_x, 2)
    min_y = round(min_y, 2)
    max_y = round(max_y, 2)
    min_z = round(min_z, 2)
    max_z = round(max_z, 2)

    inner_vertex_indices = []
    # inner_point = []
    for i, vertex in enumerate(vertices):
        # 首先对这个点的坐标进行保留两位小数
        vertex_new = np.round(vertex, 2)
        # 判断这个点是否在正方体内,并且误差范围在0.01以内
        if min_x < vertex_new[0] < max_x and min_y < vertex_new[1] < max_y and min_z < vertex_new[2] < max_z:
            inner_vertex_indices.append(i)
            # inner_point.append(vertex)

    inner_face_indices = []
    for i, face in enumerate(faces):
        is_inner_face = all(index in inner_vertex_indices for index in face)
        if is_inner_face:
            inner_face_indices.append(face)

    inner_faces = np.array(inner_face_indices, dtype=np.uint32)

    # # 按照inner_point，重新映射inner_faces中点的索引
    # inner_new_faces = np.array([[inner_vertex_indices.index(vertex) for vertex in face] for face in inner_faces], dtype=np.uint32)
    cube_edges = np.array(cube_edges, dtype=np.uint32)

    return inner_faces, cube_edges