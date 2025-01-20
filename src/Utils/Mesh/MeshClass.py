import numpy as np

import Utils.Mesh.GeometryUtils as GeometryUtils

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
        self.edges = GeometryUtils.face_to_line(self.cell).astype(np.uint32)  # numpy.ndarray 是一个一维数组，每两个连续的元素表示一条边的两个顶点索引。

        self.var = var.astype(np.float32)   # 可选的变量数据，形状与顶点数相同。

        # 点数
        self.nPoints = len(points)  # points因为是二维数组，所以直接调len得到的就是顶点数
        # 三角形个数
        self.ntriangle = len(cell) // 3

        """计算面的法向量和顶点的法向量(相邻面的平均法向量)"""
        self.faces_normal = GeometryUtils.calculate_face_normals(self.points, self.cell)

        # 每个点的法线
        self.normal = GeometryUtils.per_vertex_normals(self.points, self.cell, self.faces_normal)

        # 计算所需数据
        self.solve_vertexs = self.points
        self.solve_faces = self.cell.reshape(-1, 3)



class BodyMesh:
    def __init__(self, points, cells, cell_type=None, var=np.array([])):
        """
        初始化 BodyMesh 对象

        参数:
        points: 顶点数据，形状为 (n_points, 3)，表示所有顶点的坐标。
        cells: 一个字典，键为单元类型（如 'tetra', 'hexahedron'），值为对应单元的顶点索引数组。
        cell_type: 单元类型（默认为 None),用于指定网格类型。
        var: 可选的变量数据，形状与顶点数相同。
        """
        self.cell_type = cell_type  # 单元类型，可以为空或指定具体类型

        # 存储顶点数据
        self.points = points.astype(np.float32)

        # 存储单元格数据 (这里假设 cells 已经是字典格式)
        self.cells = cells  # cells 是一个字典，每种单元类型包含一组单元的顶点索引
        self.nPoints = len(points)  # 顶点数量
        self.nCells = {cell_type: len(cells[cell_type]) for cell_type in self.cells}  # 每种单元类型的单元数量

        # 可选的变量数据，形状与顶点数相同。
        self.var = var.astype(np.float32) if var.size else np.array([])

        # 提取所有边
        self.edges = GeometryUtils.extract_edges(self.cells)
        self.edges = np.array(self.edges).flatten().astype(np.uint32)

        # 提取所有面的索引
        self.cell_faces = GeometryUtils.extract_faces(self.cells)
        result_faces = []
        for barrays in self.cell_faces.values():
            for arr in barrays:
                if len(arr) == 3:
                    # 如果是三角形，直接添加
                    result_faces.append(arr)
                elif len(arr) == 4:
                    # 如果是四边形，拆分为两个三角形
                    result_faces.append([arr[0], arr[1], arr[2]])
                    result_faces.append([arr[0], arr[2], arr[3]])
        self.cell = np.array(result_faces, dtype=np.uint32).flatten()

        # 计算法向量（面法向量）
        self.faces_normal = GeometryUtils.calculate_v_face_normals(self.points, self.cell)

        # 计算顶点法向量
        self.normal = GeometryUtils.per_v_vertex_normals(self.points, self.faces_normal, self.cell)

        # 体元数据
        self.nTetrahedra = len(self.cells.get('tetra', []))
        self.nHexahedra = len(self.cells.get('hexahedron', []))
        self.solve_vertexs = self.points
        self.solve_cells = self.cells