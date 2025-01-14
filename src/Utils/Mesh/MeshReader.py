import meshio
import numpy as np
import os

from Utils.Mesh.MeshClass import FaceMesh, BodyMesh
from Utils.Mesh.GeometryUtils import change_to_triangle, determine_tetra_or_quad

"""
meshio 支持一系列的网格单元类型"""
"""
points: 点
line: 线段
triangle: 三角形
quad: 四边形
tetra: 四面体
hexahedron: 六面体
wedge: 楔形
pyramid: 金字塔形
line3: 二次线（3点）
triangle6: 二次三角形（6点）
quad9: 二次四边形（9点）
tetra10: 二次四面体（10点）
hexahedron20: 二次六面体（20点）
wedge15: 二次楔形（15点）
pyramid14: 二次金字塔形（14点）
"""

# off文件阅读器  (meshio默认off只能是三角网格, 对于四边形网格或四面体网格无法读取)
def read_off(filepath):

    with open(filepath, 'r') as f:
        # 读取第一行并分割成列表
        header_parts = f.readline().strip().split()
        # 检查是否以 "OFF" 开头
        if header_parts[0] != 'OFF':
            raise ValueError('Not a valid OFF file')

        # off 文件有两种可能：
        if len(header_parts) == 4:
            # 第一种：第一行的 OFF 后紧跟着三个整数，表示顶点数、面数和边数，故长度为 4。
            n_verts, n_faces, _ = map(int, header_parts[1:])
        else:
            # 第二种：只有 OFF，顶点数、面数和边数在第二行。
            n_verts, n_faces, _ = map(int, f.readline().strip().split())

        # 读取点数据
        points = np.array([list(map(float, f.readline().strip().split())) for _ in range(n_verts)])

        # 读取单元数据
        cells = []
        cell_num = 0
        for _ in range(n_faces):
            line = list(map(int, f.readline().strip().split()))
            # 每行的第一个数字表示单元包含的顶点数，后续是顶点索引
            cells.append(line[1:])
            cell_num = line[0]
        cells = np.array(cells, dtype=int)

        # 判断类型
        cell_type = None
        if cell_num == 3:  # 3 只能是三角形
            cell_type = "triangle"
        elif cell_num == 4:   # 可能是四边形或四面体
            cell_type = determine_tetra_or_quad(points, cells)
        elif cell_num == 8:   # 只能是六面体
            cell_type = "hexahedron"

    return points, cells, cell_type


# tecplot文件阅读器
def read_dat(file):
    vertices = []
    triangle = []
    quadrilateral = []
    var = []

    with open(file) as f:
        # 读取并忽略前两行（TITLE 和 VARIABLES）
        f.readline()
        f.readline()

        # 读取第三行并获取点的数量和面的数量
        zone_line = f.readline().strip().split(',')
        n_verts = int(zone_line[1].split('=')[1])
        n_faces = int(zone_line[2].split('=')[1])

        # 读取顶点和 var 值
        for _ in range(n_verts):
            line = f.readline().strip().split()
            vertices.append([float(line[0]), float(line[1]), float(line[2])])
            var.append([0,0,float(line[3])])

        vertices = np.array(vertices, dtype=np.float32)
        var = np.array(var, dtype=np.float32)

        # 读取三角形面和边的信息
        for _ in range(n_faces):
            face = [int(idx) - 1 for idx in f.readline().strip().split()]  # 索引从1开始，减1以适应Python的0索引
            if len(face) == 3:
                triangle.append(face)

            elif len(face) == 4:
                quadrilateral.append(face)


        triangle = np.array(triangle).flatten()
        triangle = np.array(triangle, dtype=np.uint32)

        quadrilateral = np.array(quadrilateral).flatten()
        quadrilateral = np.array(quadrilateral, dtype=np.uint32)

        triangle = triangle.tolist()
        quadrilateral = quadrilateral.tolist()
        cell = change_to_triangle(4, quadrilateral, triangle)  # 用一个变量来表示面绘制信息
        cell = np.array(cell, dtype=np.uint32)

    return vertices, cell, var



def MeshReader(path):
    # 获取文件扩展名（不包含点）
    ext = os.path.splitext(path)[1].lower()[1:]

    if ext == 'off':
        # 如果是 off 文件，按面网格读取
        vertices, cell, cell_type = read_off(path)
        return FaceMesh(vertices, cell, cell_type)

    elif ext == 'dat':
        # 如果是 dat 文件，按体网格读取
        vertices, cell, var = read_dat(path)

        return FaceMesh(vertices, cell, 'triangle', var)

    else:
        # 使用 meshio 读取其他类型的文件
        mesh = meshio.read(path)
        '''mesh对象的属性
            1. points：numpy.ndarray，是一个二维数组，形状为 (n, 3)，其中 n 是顶点的数量，每个顶点有三个坐标值
            2. cells_dict：dict，键是单元类型的字符串（例如 'triangle'、'quad' 等），值是一个包含对应单元连接信息的二维 NumPy 数组。
                每个数组的形状为 (m, k)，其中 m 是该类型单元的数量，k 是每个单元的顶点数。例如，对于一个四边形网格，k 为 4。
            例如：
            cells_dict={
                'triangle': np.array([
                    [0, 1, 2],
                    [0, 2, 3]
                ]),
                'quad': np.array([
                    [0, 1, 2, 3]
                ])
            }       因此下面的循环也就是在每一个列表里面进行循环，从而记录边的信息。
            '''
        # meshio 读取的对象有 points 和 cells_dict 属性
        points = np.array(mesh.points, dtype=np.float32)
        cells_dict = mesh.cells_dict

        # 创建包含所有支持类型的 cells 字典
        cells = {}
        for cell_type in ['tetra', 'hexahedron', 'wedge', 'pyramid']:
            if cell_type in cells_dict:
                cells[cell_type] = np.array(cells_dict[cell_type], dtype=np.uint32)

        # 如果包含体网格单元，返回 BodyMesh 对象
        if cells:
            return BodyMesh(points, cells)

        # 如果没有体网格单元，继续处理面网格
        else:
            # 仍然返回 FaceMesh 对象
            triangles = []
            quad = []
            if 'triangle' in mesh.cells_dict:
                triangles = mesh.cells_dict['triangle']

            if 'quad' in mesh.cells_dict:
                quad = mesh.cells_dict['quad']

            # 这里还可以继续增加 if 语句，将更多种类的多边形都读取进来，只需对应地去扩充三角化函数即可。

            # 下面就是把不管几边形都变成三角形来绘制了。
            triangles = np.array(triangles).flatten()
            quad = np.array(quad).flatten()

            triangles = triangles.tolist()
            quad = quad.tolist()
            cell = change_to_triangle(4, quad, triangles)  # 用一个变量来表示面绘制信息
            cell = np.array(cell, dtype=np.uint32)

            return FaceMesh(points, cell, 'triangle')
