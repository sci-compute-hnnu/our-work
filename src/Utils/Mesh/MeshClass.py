import numpy as np

from Utils.Mesh.GeometryUtils import calculate_face_normals, per_vertex_normals, face_to_line

# 这个是用于绘制面网格的
class FaceMesh():

    def __init__(self, points, cell, cell_type,  var=np.array([])):

        # 单元类型
        self.cell_type = cell_type

        # 点 ：包含网格中所有顶点的坐标。
        self.points = points.astype(np.float32)  # numpy.ndarray 是一个二维数组，形状为 (顶点数, 3)，每行包含一个顶点的三维坐标（x, y, z）。
        # 全部统一为三角形绘制
        self.cell = cell.flatten().astype(np.uint32)  # numpy.ndarray 是一个一维数组，每三个连续的元素表示一个三角形的三个顶点索引。
        # (边)
        self.edges = face_to_line(self.cell).astype(np.uint32)  # numpy.ndarray 是一个一维数组，每两个连续的元素表示一条边的两个顶点索引。

        self.var = var.astype(np.float32)   # 可选的变量数据，形状与顶点数相同。

        # 点数
        self.nPoints = len(points)  # points因为是二维数组，所以直接调len得到的就是顶点数
        # 三角形个数
        self.ntriangle = len(cell) // 3

        """计算面的法向量和顶点的法向量(相邻面的平均法向量)"""
        self.faces_normal = calculate_face_normals(self.points, self.cell)

        # 每个点的法线
        self.normal = per_vertex_normals(self.points, self.cell, self.faces_normal)

        # 计算所需数据
        self.solve_vertexs = self.points
        self.solve_faces = self.cell.reshape(-1, 3)



# 这个是用于绘制体网格的
class BodyMesh:
    def __init__(self, points, cells=None, var=np.array([])):
        """
        初始化 BodyMesh 对象

        参数:
        points: 顶点数据，形状为 (n_points, 3)，表示所有顶点的坐标。
        cells: 一个字典，键为单元类型（如 'tetra', 'hexahedron'），值为对应单元的顶点索引数组。
        """
        self.points = points.astype(np.float32)  # 存储顶点数据
        if cells is None:
            cells = {}
        self.cells = cells.astype(np.uint32)
        self.nPoints = len(points)  # 顶点数量
        self.nCells = {cell_type: len(cells[cell_type]) for cell_type in self.cells}  # 每种单元类型的单元数量

        # 如果要画边的话
        self.edges = None
        self.extract_edges()
        self.edges = np.array(self.edges).flatten()
        self.edges = np.array(self.edges, dtype=np.uint32)

        self.var = var  # 可选的变量数据，形状与顶点数相同。

        # cell 表示面
        self.cell = self.extract_faces()
        result = []
        for barrays in self.cell.values():
            for arr in barrays:
                if len(arr) == 3:
                    # 如果是三角形，直接添加
                    result.append(arr)
                elif len(arr) == 4:
                    # 如果是四边形，拆分为两个三角形a
                    result.append([arr[0], arr[1], arr[2]])
                    result.append([arr[0], arr[2], arr[3]])
        self.cell = np.array(result, dtype=np.uint32).flatten()

        # 计算每个面元的法向量和每个顶点的法向量
        self.faces_normal = self.calculate_face_normals(self.points, self.cell)
        self.normal = self.per_vertex_normals(self.points, self.faces_normal, self.cell)

    def calculate_face_normals(self, vertices, cell):
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

    def per_vertex_normals(self, vertices, face_normals, cell):
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

    def extract_faces(self):
        """
        提取网格的面，并将其展开为适合 OpenGL 绘制的三角形索引。

        返回:
        faces: 一个字典，键为单元类型，值为对应的三角形面索引数组
        """
        faces = {}
        for cell_type, cell_data in self.cells.items():
            if cell_type == 'tetra':
                faces[cell_type] = self._extract_tetra_faces(cell_data)  # 四面体直接存储三角形面
            elif cell_type == 'hexahedron':
                faces[cell_type] = self._extract_hexa_faces(cell_data)  # 六面体分解为三角形面
            # 可以继续添加其他类型单元的面提取方法
        return faces

    def extract_edges(self):
        """
        提取网格的边。

        返回:
        edges: 边的顶点索引数组
        """
        edges = set()
        for cell_type, cell_data in self.cells.items():
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
        self.edges = np.array(list(edges), dtype=np.uint32)

    def _extract_tetra_faces(self, tetrahedra):
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
    def help_reshape(self, faces_old):
        result = []
        for arr in faces_old:
            if len(arr) == 3:
                result.append(arr)
            elif len(arr) == 4:
                result.append([arr[0], arr[1], arr[2]])
                result.append([arr[0], arr[2], arr[3]])
        return result

    def _extract_hexa_faces(self, hexahedra):
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
        faces = self.help_reshape(faces)
        return np.array(faces, dtype=np.uint32)

    def _extract_wedge_faces(self, wedges):
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
        faces = self.help_reshape(faces)
        return np.array(faces, dtype=np.uint32)

    def _extract_pyramid_faces(self, pyramids):
        """
        提取金字塔体的面

        参数:
        pyramids: 金字塔体的顶点索引数组

        返回:
        faces: 金字塔体的面顶点索引数组
        """
        faces = []
        for pyramid in pyramids:
            faces.extend([
                [pyramid[0], pyramid[1], pyramid[2], pyramid[3]],  # 四边形面
                [pyramid[0], pyramid[1], pyramid[4]],  # 三角形面
                [pyramid[1], pyramid[2], pyramid[4]],
                [pyramid[2], pyramid[3], pyramid[4]],
                [pyramid[3], pyramid[0], pyramid[4]],
            ])
        faces = self.help_reshape(faces)
        return np.array(faces, dtype=np.uint32)