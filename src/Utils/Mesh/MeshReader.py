import meshio
import numpy as np
import os

from Utils.Mesh.MeshClass import FaceMesh, BodyMesh
from Utils.Mesh.GeometryUtils import determine_tetra_or_quad

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


def read_dat(file):
    vertices = []
    triangle = []
    quadrilateral = []
    var = {}

    with open(file) as f:
        # 读取并忽略前两行（TITLE 和 VARIABLES）
        f.readline()

        # 读取第二行（VARIABLES）
        variables_line = f.readline().strip()
        variables_list = variables_line.split('=')[1].replace('"', '').split()

        # 检查是否存在除坐标点外的变量
        if 'z' in variables_list:
            variable_names = variables_list[3:]  # 从第四个变量开始（三维）
        else:
            variable_names = variables_list[2:]  # 从第三个变量开始（二维）

        # 若存在除坐标点外的变量，初始化字典
        if variable_names:
            for name in variable_names:
                var[name] = []

        # 读取第三行并获取点的数量和面的数量
        zone_line = f.readline().strip().split(',')
        n_verts = int(zone_line[1].split('=')[1])
        n_faces = int(zone_line[2].split('=')[1])

        # 读取顶点和 var 值
        for _ in range(n_verts):
            line = f.readline().strip().split()
            if 'z' in variables_list:
                vertices.append([float(line[0]), float(line[1]), float(line[2])])
            else:
                vertices.append([float(line[0]), float(line[1]), float(0)])

            # 若存在除坐标点外的变量，读取 var 值
            if variable_names:
                for i, name in enumerate(variable_names):
                    if 'z' in variables_list:
                        var[name].append([0, 0, float(line[i + 3])])
                    else:
                        var[name].append([0, 0, float(line[i + 2])])

        vertices = np.array(vertices, dtype=np.float32)

        # 读取三角形面和边的信息
        for _ in range(n_faces):
            face = [int(idx) - 1 for idx in f.readline().strip().split()]  # 索引从1开始，减1以适应Python的0索引
            if len(face) == 3:
                triangle.append(face)
            elif len(face) == 4:
                quadrilateral.append(face)

        cell = np.array(triangle)

    return vertices, cell, var


# 网格读取器
def MeshReader(path):

    # 该读取器支持的网格类型 (该写法为meshio的写法)
    supported_cells = ['triangle', 'quad', 'tetra', 'hexahedron']

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
        # meshio 读取的对象有 points 和 cells_dict 属性
        points = np.array(mesh.points, dtype=np.float32)
        cells_dict = mesh.cells_dict

        """当前版本体网格只支持读取单一单元类型的网格"""

        if all(item not in cells_dict for item in supported_cells):
            print("Error: This type of mesh is not supported for display.")
            return None

        if 'tetra' in cells_dict or 'hexahedron' in cells_dict: # 处理体网格

            if 'tetra' in cells_dict and 'hexahedron' in cells_dict:  # 同时含有两种类型的体网格则都不支持
                print("Error: This type of mesh is not supported for display.")
                return None
            elif 'tetra' in cells_dict:  # 四面体网格
                cells = cells_dict['tetra'].astype(np.uint32)
                return BodyMesh(points, cells, "tetrahedron")
            elif 'hexahedron' in cells_dict:   # 六面体网格
                cells = cells_dict['hexahedron'].astype(np.uint32)
                return BodyMesh(points, cells, 'hexahedron')

        else:  # 处理面网格

            if 'triangle' in cells_dict and 'quad' in cells_dict:  # 同时含有两种类型的面网格则都不支持
                print("Error: This type of mesh is not supported for display.")
                return None
            elif 'triangle' in cells_dict:  # 三角形网格
                cells = cells_dict['triangle'].astype(np.uint32)
                return FaceMesh(points, cells, 'triangle')
            elif 'quad' in cells_dict:   # 四边形网格
                cells = cells_dict['quad'].astype(np.uint32)
                return FaceMesh(points, cells, 'quadrilateral')

