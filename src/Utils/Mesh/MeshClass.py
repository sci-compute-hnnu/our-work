import numpy as np

import Utils.Mesh.GeometryUtils as GeometryUtils

# 面网格
class FaceMesh():

    def __init__(self, points, cells, cell_type, var={}):

        """
        初始化 FaceMesh 对象

        参数:
        points: 顶点数据，形状为 (n_points, 3)，表示所有顶点的坐标。
        cells: 单元数据，形状为 (n_cells, vector_cell)，表示所有单元的索引  vector_cell e.g. triangle:3 quadrilateral:4
        cell_type: 用于指定网格类型（triangle 或 quadrilateral）
        var: 可选的变量数据，形状与顶点数相同。
        """

        # 单元类型
        self.cell_type = cell_type

        """ 用于openGL渲染的数据成员 """
        # 点 ：包含网格中所有顶点的坐标。 二维数组，形状为 (顶点数, 3)，每行包含一个顶点的三维坐标（x, y, z）。
        self.gl_points = points.astype(np.float32)
        # 单元  一维数组，每三个连续的元素表示一个三角形的三个顶点索引。
        self.gl_cells = cells.flatten().astype(np.uint32)
        # 边  一维数组，每两个连续的元素表示一条边的两个顶点索引。
        self.gl_edges = GeometryUtils.extract_edges(cells, self.cell_type).flatten().astype(np.uint32)
        # 计算每个点的法向量
        self.gl_normal = GeometryUtils.calculate_vertex_normals(points, cells)
        # 用于渲染的数据
        self.gl_var = var


        """ 用于计算所需数据成员 """
        # 计算所需数据
        self.solve_vertexs = points
        self.solve_faces = cells


# 体网格
class BodyMesh:
    def __init__(self, points, cells, cell_type=None, var={}):

        """
        初始化 BodyMesh 对象

        参数:
        points: 顶点数据，形状为 (n_points, 3)，表示所有顶点的坐标。
        cells: 单元数据，形状为 (n_cells, vector_cell)，表示所有单元的索引  vector_cell e.g. tetrahedron:4 hexahedron:8
        cell_type: 用于指定网格类型（tetrahedron 或 hexahedron）
        var: 可选的变量数据，形状与顶点数相同。
        """

        # 单元类型
        self.cell_type = cell_type  # 单元类型，可以为空或指定具体类型

        """ 用于openGL渲染的数据成员 """
        # 点 ：包含网格中所有顶点的坐标。 二维数组，形状为 (顶点数, 3)，每行包含一个顶点的三维坐标（x, y, z）。
        self.gl_points = points.astype(np.float32)
        # 单元  一维数组，每三个连续的元素表示一个三角形的三个顶点索引。
        self.gl_cells = GeometryUtils.extract_faces(cells, self.cell_type).flatten().astype(np.uint32)
        # 边  一维数组，每两个连续的元素表示一条边的两个顶点索引。
        self.gl_edges = GeometryUtils.extract_edges(cells, self.cell_type).flatten().astype(np.uint32)
        # 计算顶点法向量
        self.gl_normal = GeometryUtils.calculate_vertex_normals(points,  self.gl_cells.reshape(-1, 3))
        # 用于渲染的数据
        self.gl_var = var


        """ 用于计算所需数据成员 """
        # 计算所需数据
        self.solve_vertexs = points
        self.solve_cells = cells
