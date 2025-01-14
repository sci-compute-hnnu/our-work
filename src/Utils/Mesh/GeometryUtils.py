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
