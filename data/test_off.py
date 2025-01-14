import numpy as np

from Utils.Mesh.GeometryUtils import change_to_triangle, determine_tetra_or_quad

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


points, cells, type_ = read_off('./ball_quadrilateralMesh.off')
print(type_)
