import numpy as np

# 多边形的三角化
def change_to_triangle(type, quadrilateral, triangle):
    # 如果是四边形的话 需要先拆分为三角形 方便着色
    if type == 4:
        for i in range(0, len(quadrilateral), 4):
            face = quadrilateral[i:i + 4]
            triangle.append([face[0], face[1], face[2]])
            triangle.append([face[0], face[2], face[3]])
        triangle = np.array(triangle, dtype=np.uint32)
        triangle = np.array(triangle).flatten()
    # 这里还可以增加更多 if 从而适应面网格由各种各样的面组成
    return triangle


# 将face转化为edge (这里的line是重复的) （且face和edge都是一维数组）  type=1 则处理三角形 type=2 则处理四边形 （默认type为1）
def face_to_line(faces, type=1):
    edges = set()  # 用集合来存储去重后的边

    if type == 1:  # 处理三角形
        for i in range(0, len(faces), 3):
            triangle = faces[i:i + 3]
            # 对边排序并加入集合
            edges.add(tuple(sorted([triangle[0], triangle[1]])))
            edges.add(tuple(sorted([triangle[1], triangle[2]])))
            edges.add(tuple(sorted([triangle[2], triangle[0]])))

    elif type == 2:  # 处理四边形
        for i in range(0, len(faces), 4):
            quad = faces[i:i + 4]
            # 对边排序并加入集合
            edges.add(tuple(sorted([quad[0], quad[1]])))
            edges.add(tuple(sorted([quad[1], quad[2]])))
            edges.add(tuple(sorted([quad[2], quad[3]])))
            edges.add(tuple(sorted([quad[3], quad[0]])))

    # 将集合转换为数组并返回
    return np.array(list(edges)).flatten()


# 用于计算每个面的法向量
def calculate_face_normals(vertices, faces):
    # 计算面法线
    facess = np.array(faces).reshape(-1, 3)

    FN = np.zeros((len(facess), 3), dtype=np.float32)
    for i, f in enumerate(facess):
        v1 = vertices[f[1]] - vertices[f[0]]
        v2 = vertices[f[2]] - vertices[f[0]]
        FN[i] = np.cross(v1, v2)
        FN[i] = FN[i] / np.linalg.norm(FN[i])
    return FN



# 用于计算每个顶点的法向量
def per_vertex_normals(vertices, faces, face_normals):
    # 计算顶点法线
    VN = np.zeros(vertices.shape, dtype=np.float32)

    facess = np.array(faces).reshape(-1, 3)
    for i in range(len(vertices)):
        faces_using = np.where(facess == i)[0]
        for j in faces_using:
            VN[i] += face_normals[j]
        VN[i] = VN[i] / np.linalg.norm(VN[i])
    return VN


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

def calculate_v_face_normals(vertices, cell):
    """
            计算每个三角形面的法向量。

            参数:
            vertices: 顶点坐标数组
            cell: 包含三角形面顶点索引的一维数组，每三个元素表示一个面。

            返回:
            face_normals: 面法向量数组，形状为 (n_faces, 3)
            """
    face_normals = np.zeros((len(cell) // 3, 3), dtype=np.float32)
    for i in range(0, len(cell), 3):
        v0, v1, v2 = vertices[cell[i]], vertices[cell[i + 1]], vertices[cell[i + 2]]
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        normal = normal / np.linalg.norm(normal)
        face_normals[i // 3] = normal
    return face_normals

def per_v_vertex_normals(vertices, face_normals, cell):
    """
            根据面法向量计算每个顶点的法向量。

            参数:
            vertices: 顶点坐标数组
            face_normals: 面法向量数组，形状为 (n_faces, 3)
            cell: 包含三角形面顶点索引的一维数组，每三个元素表示一个面。

            返回:
            vertex_normals: 每个顶点的法向量数组，形状为 (n_points, 3)
            """
    vertex_normals = np.zeros((len(vertices), 3), dtype=np.float32)
    for i in range(0, len(cell), 3):
        v0, v1, v2 = cell[i], cell[i + 1], cell[i + 2]
        normal = face_normals[i // 3]
        vertex_normals[v0] += normal
        vertex_normals[v1] += normal
        vertex_normals[v2] += normal

    # 归一化每个顶点的法向量
    for i in range(len(vertex_normals)):
        norm = np.linalg.norm(vertex_normals[i])
        if norm > 0:
            vertex_normals[i] /= norm
        else:
            # 如果法向量为零，直接设置为零向量或其他默认值
            vertex_normals[i] = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    return vertex_normals

def extract_faces(cells):
    """
            提取网格的面，并将其展开为适合 OpenGL 绘制的三角形索引。

            返回:
            faces: 一个字典，键为单元类型，值为对应的三角形面索引数组
            """
    faces = {}
    for cell_type, cell_data in cells.items():
        if cell_type == 'tetra':
            faces[cell_type] = _extract_tetra_faces(cell_data)  # 四面体直接存储三角形面
        elif cell_type == 'hexahedron':
            faces[cell_type] = _extract_hexa_faces(cell_data)  # 六面体分解为三角形面
        # 可以继续添加其他类型单元的面提取方法
    return faces

def extract_edges(cells):
    """
            提取网格的边。

            返回:
            edges: 边的顶点索引数组
            """
    edges = set()
    for cell_type, cell_data in cells.items():
        if cell_type == 'tetra':
            for tet in cell_data:
                edges.update([
                    tuple(sorted((tet[0], tet[1]))),
                    tuple(sorted((tet[0], tet[2]))),
                    tuple(sorted((tet[0], tet[3]))),
                    tuple(sorted((tet[1], tet[2]))),
                    tuple(sorted((tet[1], tet[3]))),
                    tuple(sorted((tet[2], tet[3])))
                ])
        elif cell_type == 'hexahedron':
            for hex in cell_data:
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
        elif cell_type == 'wedge':
            for wedge in cell_data:
                edges.update([
                    tuple(sorted((wedge[0], wedge[1]))),
                    tuple(sorted((wedge[1], wedge[2]))),
                    tuple(sorted((wedge[2], wedge[0]))),
                    tuple(sorted((wedge[3], wedge[4]))),
                    tuple(sorted((wedge[4], wedge[5]))),
                    tuple(sorted((wedge[5], wedge[3]))),
                    tuple(sorted((wedge[0], wedge[3]))),
                    tuple(sorted((wedge[1], wedge[4]))),
                    tuple(sorted((wedge[2], wedge[5])))
                ])
        elif cell_type == 'pyramid':
            for pyramid in cell_data:
                edges.update([
                    tuple(sorted((pyramid[0], pyramid[1]))),
                    tuple(sorted((pyramid[1], pyramid[2]))),
                    tuple(sorted((pyramid[2], pyramid[3]))),
                    tuple(sorted((pyramid[3], pyramid[0]))),
                    tuple(sorted((pyramid[0], pyramid[4]))),
                    tuple(sorted((pyramid[1], pyramid[4]))),
                    tuple(sorted((pyramid[2], pyramid[4]))),
                    tuple(sorted((pyramid[3], pyramid[4])))
                ])
        # 可以继续添加其他类型单元的边提取方法

    # 将边转换为 NumPy 数组
    edges = np.array(list(edges), dtype=np.uint32)
    return edges

def _extract_tetra_faces(tetrahedra):
    """
           提取四面体的面

           参数:
           tetrahedra: 四面体的顶点索引数组

           返回:
           faces: 四面体的面顶点索引数组
           """
    faces = []
    for tet in tetrahedra:
        faces.extend([
            [tet[0], tet[1], tet[2]],  # 三角形面
            [tet[0], tet[1], tet[3]],
            [tet[0], tet[2], tet[3]],
            [tet[1], tet[2], tet[3]],
        ])
    return np.array(faces, dtype=np.uint32)

# 四边形化三角形
def help_reshape(faces_old):
    result = []
    for arr in faces_old:
        if len(arr) == 3:
            result.append(arr)
        elif len(arr) == 4:
            result.append([arr[0], arr[1], arr[2]])
            result.append([arr[0], arr[2], arr[3]])
    return result

def _extract_hexa_faces(hexahedra):
    """
            提取六面体的面

            参数:
            hexahedra: 六面体的顶点索引数组

            返回:
            faces: 六面体的面顶点索引数组
            """
    faces = []
    for hex in hexahedra:
        faces.extend([
            [hex[0], hex[1], hex[2], hex[3]],  # 四边形面
            [hex[4], hex[5], hex[6], hex[7]],
            [hex[0], hex[1], hex[5], hex[4]],
            [hex[2], hex[3], hex[7], hex[6]],
            [hex[1], hex[2], hex[6], hex[5]],
            [hex[3], hex[0], hex[4], hex[7]],
        ])
    faces = help_reshape(faces)
    return np.array(faces, dtype=np.uint32)

def _extract_wedge_faces(wedges):
    """
            提取楔形体的面

            参数:
            wedges: 楔形体的顶点索引数组

            返回:
            faces: 楔形体的面顶点索引数组
            """
    faces = []
    for wedge in wedges:
        faces.extend([
            [wedge[0], wedge[1], wedge[2]],  # 三角形面
            [wedge[3], wedge[4], wedge[5]],
            [wedge[0], wedge[1], wedge[4], wedge[3]],  # 四边形面
            [wedge[1], wedge[2], wedge[5], wedge[4]],
            [wedge[2], wedge[0], wedge[3], wedge[5]],
        ])
    faces = help_reshape(faces)
    return np.array(faces, dtype=np.uint32)

def _extract_wedge_faces(wedges):
    """
            提取楔形体的面

            参数:
            wedges: 楔形体的顶点索引数组

            返回:
            faces: 楔形体的面顶点索引数组
            """
    faces = []
    for wedge in wedges:
        faces.extend([
            [wedge[0], wedge[1], wedge[2]],  # 三角形面
            [wedge[3], wedge[4], wedge[5]],
            [wedge[0], wedge[1], wedge[4], wedge[3]],  # 四边形面
            [wedge[1], wedge[2], wedge[5], wedge[4]],
            [wedge[2], wedge[0], wedge[3], wedge[5]],
        ])
    faces = help_reshape(faces)
    return np.array(faces, dtype=np.uint32)