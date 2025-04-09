import numpy as np

import Utils.Mesh.GeometryUtils as GeometryUtils

# 面网格
class FaceMesh():

    def __init__(self, points, cells, cell_type, var={}, file_path=None):

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
        # 文件地址 (None表示由软件内生成)
        self.file_path = file_path

        """ 用于计算所需数据成员 """
        # 计算所需数据
        self.vertexs = points
        self.cells = cells

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
        self.gl_var = {k: np.column_stack((np.zeros(len(v)), np.zeros(len(v)), v)) for k, v in var.items()}



# 体网格
class BodyMesh:

    def __init__(self, points, cells, cell_type=None, var={}, file_path=None):

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
        # 文件地址 (None表示由软件内生成)
        self.file_path = file_path


        """ 用于计算所需数据成员 """
        # 计算所需数据
        self.vertexs = points
        self.cells = cells

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
        self.gl_var = {k: np.column_stack((np.zeros(len(v)), np.zeros(len(v)), v)) for k, v in var.items()}

        surface_cells = GeometryUtils.get_faces_from_volume_mesh(self.gl_cells, self.gl_points)
        self.surface_mesh = FaceMesh(points, surface_cells, 'triangle', var)

