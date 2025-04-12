import numpy as np
from collections import Counter
from Utils.Compute.Interpolation import tetrahedral_lagrange_interpolation
from Utils.Mesh.MeshClass import FaceMesh, BodyMesh


# 网格切割器
class MeshSplitter:


    def __init__(self, body_mesh, cutting_plane):

        self.originalMesh = body_mesh   # 待切割网格

        self.cuttingPlane = cutting_plane  # 切平面方程

        pass

    def is_point_on_edge(self, point, edge):
        """
        判断点是否在棱上
        :param point: 待判断的点，三维坐标，如 [x, y, z]
        :param edge: 棱的两个端点，如 [[x1, y1, z1], [x2, y2, z2]]
        :return: 如果点在棱上返回 True，否则返回 False
        """
        point = np.array(point)
        start, end = np.array(edge)
        line_vector = end - start
        point_vector = point - start
        if np.linalg.norm(np.cross(line_vector, point_vector)) < 1e-9:
            t = np.dot(point_vector, line_vector) / np.dot(line_vector, line_vector)
            return 0 <= t <= 1
        return False

    def is_point_on_face(slef, point, face):
        """
        判断点是否在面上
        :param point: 待判断的点，三维坐标，如 [x, y, z]
        :param face: 面的三个顶点，如 [[x1, y1, z1], [x2, y2, z2], [x3, y3, z3]]
        :return: 如果点在面上返回 True，否则返回 False
        """
        point = np.array(point)
        v0 = np.array(face[1]) - np.array(face[0])
        v1 = np.array(face[2]) - np.array(face[0])
        normal = np.cross(v0, v1)

        # 检查点是否在面所在的平面上
        if np.abs(np.dot(point - np.array(face[0]), normal)) < 1e-9:
            # 检查点是否在面的三角形内
            v2 = point - np.array(face[0])
            dot00 = np.dot(v0, v0)
            dot01 = np.dot(v0, v1)
            dot02 = np.dot(v0, v2)
            dot11 = np.dot(v1, v1)
            dot12 = np.dot(v1, v2)
            inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
            u = (dot11 * dot02 - dot01 * dot12) * inv_denom
            v = (dot00 * dot12 - dot01 * dot02) * inv_denom
            return 0 <= u <= 1 and 0 <= v <= 1 and u + v <= 1
        return False

    def check_points(self, points, tetrahedron):
        """
        检查一系列点是否都位于四面体的同一条边或者同一个面上
        :param points: 一系列点，如 [[x1, y1, z1], [x2, y2, z2], ...]
        :param tetrahedron: 四面体的四个顶点，如 [[x1, y1, z1], [x2, y2, z2], [x3, y3, z3], [x4, y4, z4]]
        :return: 如果所有点都位于同一条边或者同一个面上返回 True，否则返回 False
        """
        # 定义四面体的六条棱
        edges = [
            [tetrahedron[0], tetrahedron[1]],
            [tetrahedron[0], tetrahedron[2]],
            [tetrahedron[0], tetrahedron[3]],
            [tetrahedron[1], tetrahedron[2]],
            [tetrahedron[1], tetrahedron[3]],
            [tetrahedron[2], tetrahedron[3]]
        ]

        # 检查是否所有点都在某条棱上
        for edge in edges:
            if all(self.is_point_on_edge(point, edge) for point in points):
                return True

        # 定义四面体的四个面
        faces = [
            [tetrahedron[0], tetrahedron[1], tetrahedron[2]],
            [tetrahedron[0], tetrahedron[1], tetrahedron[3]],
            [tetrahedron[0], tetrahedron[2], tetrahedron[3]],
            [tetrahedron[1], tetrahedron[2], tetrahedron[3]]
        ]

        # 检查是否所有点都在某个面上
        for face in faces:
            if all(self.is_point_on_face(point, face) for point in points):
                return True

        return False

    def is_tetrahedron(self, vertices):
        # 判断四个顶点是否共面
        a = np.ones((4, 4), dtype=np.float32)
        a[:, :-1] = vertices
        det = np.linalg.det(a)
        return not abs(det) < 10e-5

    # 创建一个函数来判断两个顶点是否相等
    def is_close(self, vertex1, vertex2, tolerance=1e-6):
        return all(abs(v1 - v2) < tolerance for v1, v2 in zip(vertex1, vertex2))

    # 创建一个函数来查找顶点的索引
    def find_vertex_index(self, vertex, vertices, tolerance=1e-6):
        for idx, v in enumerate(vertices):
            if self.is_close(vertex, v, tolerance):
                return idx
        return None

    def computer_intersection_point(self, vertices, plane):
        edges = [
            (0, 1), (0, 2), (0, 3),  # 四面体的边
            (1, 2), (1, 3), (2, 3)
        ]

        a, b, c, d = plane
        intersection_points = []

        for edge in edges:
            p1 = np.array(vertices[edge[0]])
            p2 = np.array(vertices[edge[1]])

            # 边的参数方程：P = p1 + t * (p2 - p1)
            direction = p2 - p1
            denominator = a * direction[0] + b * direction[1] + c * direction[2]

            if denominator != 0:  # 判断直线与平面是否平行
                t = -(a * p1[0] + b * p1[1] + c * p1[2] + d) / denominator
                if 0 <= t <= 1:  # 检查交点是否在线段内部
                    intersection_point = p1 + t * direction
                    intersection_points.append(intersection_point)

        return intersection_points

    def is_line_segments_intersecting_3d(self, segment1, segment2):
        """
        判断三维空间中两条线段是否相交（交点在线段内部，不包括端点）
        :param segment1: 第一条线段的两个端点，格式为 [point1, point2]
        :param segment2: 第二条线段的两个端点，格式为 [point1, point2]
        :return: 如果相交返回 True，否则返回 False
        """
        # 把输入的端点转换为 numpy 数组
        p1, p2 = np.array(segment1, dtype=np.float64)
        p3, p4 = np.array(segment2, dtype=np.float64)

        # 计算两条线段的方向向量
        d1 = p2 - p1
        d2 = p4 - p3
        # 计算从 p1 到 p3 的向量
        r = p3 - p1

        # 计算混合积的分母，用于后续计算参数 t 和 u
        denominator = np.dot(np.cross(d1, d2), np.cross(d1, d2))

        # 处理分母接近零的情况，此时两条线段平行或共线，认为不相交
        if np.abs(denominator) < 1e-9:
            return False

        # 计算参数 t 和 u
        t = np.dot(np.cross(r, d2), np.cross(d1, d2)) / denominator
        u = np.dot(np.cross(r, d1), np.cross(d1, d2)) / denominator

        # 判断参数 t 和 u 是否都在开区间 (0, 1) 内
        # 如果是，则说明交点在线段内部，两条线段相交
        return 0 < t < 1 and 0 < u < 1

    def sort_points_counterclockwise(self, points):

        # 计算质心
        centroid = np.mean(points, axis=0)

        # 计算每个点相对于质心的极角
        def polar_angle(point):
            vector = point - centroid
            return np.arctan2(vector[1], vector[0])

        # 根据极角对四个点进行排序
        sorted_points = sorted(points, key=polar_angle)

        return sorted_points

    def decide_tetrahedron(self, vertices, plane):
        # 判断四面体与平面的关系
        a, b, c, d = plane
        distances = np.array([a * x + b * y + c * z + d for x, y, z in vertices])

        # 如果四个顶点都在平面同一侧
        if all(distances <= 0):
            status = "negative"
            vertex = [vertices[i] for i in range(4) if distances[i] <= 0]
        elif all(distances >= 0):
            status = "positive"
            vertex = [vertices[i] for i in range(4) if distances[i] >= 0]
        else:
            # 处理四面体跨越平面的情况
            status = "crossing"
            vertex = vertices.tolist()  # 返回所有顶点

        return status, vertex

    def is_point_on_line_segment(self, P, line_segment):
        P = np.array(P)
        line_segment = np.array(line_segment)
        P1, P2 = line_segment
        return np.linalg.norm(np.cross(P - P1, P - P2)) < 1e-6

    def split_tetrahedron_three(self, intersection_points, vertices, plane, negative_or_positive):
        """
        将被平面分割的四面体进一步细分为多个四面体，当平面与四面体有三个交点时。

        :param vertices: 四面体的顶点坐标，列表形式 [[x1, y1, z1], [x2, y2, z2], ...] (4个顶点)
        :param plane: 平面方程的系数 [a, b, c, d], 对应 ax + by + cz + d = 0
        :return: 四个新四面体的顶点
        """
        a, b, c, d = plane
        if len(intersection_points) != 3:
            raise ValueError("平面与四面体的交点不是三个")

        # 计算每个顶点到平面的距离
        distances = np.array([a * x + b * y + c * z + d for x, y, z in vertices])

        # 根据 negative_or_positive 确定单侧顶点
        if negative_or_positive == "positive":
            single_vertex_side = [vertices[i] for i in range(4) if distances[i] > 0]
        else:
            single_vertex_side = [vertices[i] for i in range(4) if distances[i] < 0]

        P1, P2, P3 = intersection_points

        # 如果单侧只有一个顶点
        if len(single_vertex_side) == 1:
            single_vertex = single_vertex_side[0].tolist()
            tetrahedral = [[single_vertex, P1, P2, P3]]
            tetrahedral_vertex = tetrahedral[0]

        elif len(single_vertex_side) == 0:
            tetrahedral = None
            tetrahedral_vertex = None

        else:
            # 重新确定单侧顶点
            if negative_or_positive == "positive":
                single_vertex_side = [vertices[i] for i in range(4) if distances[i] < 0]
            else:
                single_vertex_side = [vertices[i] for i in range(4) if distances[i] > 0]

            single_vertex = single_vertex_side[0].tolist()
            triple_vertices = [list(v) for v in vertices if list(v) != single_vertex]

            # 检查交点是否在 triple_vertices 中
            index = next(
                (i for i, v in enumerate(triple_vertices) if any(np.array_equal(v, P) for P in intersection_points)),
                None)

            if index != None:
                # 调整 triple_vertices 的顺序（可以简化）
                triple_vertices = [triple_vertices[index]] + triple_vertices[:index] + triple_vertices[index + 1:]

                # 取出三个顶点中的两个顶点不等于triple_vertices[0]的顶点
                P1, P2 = [v for v in intersection_points if not np.array_equal(v, triple_vertices[0])]

                tetrahedron1 = [triple_vertices[0], triple_vertices[1], P1, P2]

                # 判断P1与P2谁在single_vertex与triple_vertices[2]构成的线段上

                if self.is_point_on_line_segment(P1, [single_vertex, triple_vertices[2]]):
                    tetrahedron2 = [triple_vertices[1], triple_vertices[2], P1, triple_vertices[0]]
                else:
                    tetrahedron2 = [triple_vertices[1], triple_vertices[2], P2, triple_vertices[0]]

                tetrahedral = [tetrahedron1, tetrahedron2]

            else:
                # 对 triple_vertices 进行排序
                triple_vertices = self.sort_points_counterclockwise(triple_vertices)
                for i in range(3):
                    if self.is_point_on_line_segment(P3, [single_vertex, triple_vertices[i]]):
                        index_P3 = i
                    if self.is_point_on_line_segment(P2, [single_vertex, triple_vertices[i]]):
                        index_P2 = i

                tetrahedral = [
                    [triple_vertices[index_P3], P1, P2, P3],
                    [triple_vertices[1], P1, triple_vertices[0], triple_vertices[2]],
                    [triple_vertices[index_P3], P1, P2, triple_vertices[index_P2]]
                ]

            tetrahedral_vertex = triple_vertices

        return tetrahedral, tetrahedral_vertex

    def split_tetrahedron_four(self,intersection_points, vertices, plane, negative_or_positive):
        """
            将被平面分割的四面体进一步细分为多个四面体。

            :param vertices: 四面体的顶点坐标，列表形式 [[x1, y1, z1], [x2, y2, z2], ...] (4个顶点)
            :param plane: 平面方程的系数 [a, b, c, d], 对应 ax + by + cz + d = 0
            :return: 两部分（每部分2个四面体），共4个新四面体的顶点
            """
        a, b, c, d = plane

        if len(intersection_points) != 4:
            raise ValueError("平面与四面体的交点未形成四边形")
        # 划分顶点为两组
        distances = np.array([a * x + b * y + c * z + d for x, y, z in vertices])

        if negative_or_positive == "positive":
            side_right = [vertices[i] for i in range(4) if distances[i] > 0]
            side_wrong = [vertices[i] for i in range(4) if distances[i] < 0]
        else:
            side_right = [vertices[i] for i in range(4) if distances[i] < 0]
            side_wrong = [vertices[i] for i in range(4) if distances[i] > 0]

        if len(side_right) == 0:
            tetrahedral = None
            tetrahedral_vertex = None

        # 注意这里还有一种平面经过一个面的情况。将这种情况放到最后的那个split中处理

        else:
            side_right = [list(v) for v in side_right]
            side_wrong = [list(v) for v in side_wrong]
            # 得到位于side_right[0]与side_wrong[0]这条线段上的交点
            for i in range(4):
                if self.is_point_on_line_segment(intersection_points[i], [side_right[0], side_wrong[0]]):
                    index = i
                elif self.is_point_on_line_segment(intersection_points[i], [side_right[0], side_wrong[1]]):
                    index1 = i
                elif self.is_point_on_line_segment(intersection_points[i], [side_right[1], side_wrong[0]]):
                    index2 = i
                else:
                    index3 = i

            tetrahedral = [
                [side_right[0], intersection_points[index], intersection_points[index1], intersection_points[index2]],
                [side_right[1], intersection_points[index], intersection_points[index2], intersection_points[index3]],
                [side_right[0], side_right[1], intersection_points[index], intersection_points[index2]]]

            # 判断intersection_points[index1]与intersection_points[index2]构成的线段是否intersection_points[index]与intersection_points[index3]构成的线段相交
            segment1 = [intersection_points[index1], intersection_points[index2]]
            segment2 = [intersection_points[index], intersection_points[index3]]
            if self.is_line_segments_intersecting_3d(segment1, segment2):
                tetrahedral[1][1] = intersection_points[index1]
                tetrahedral[2][2] = intersection_points[index1]

            tetrahedral_vertex = side_right

        return tetrahedral, tetrahedral_vertex

    def split_tetrahedron(self, vertices, cells, plane, var={}):
        """
        根据平面将网格划分为两部分

        参数:
        vertices: 顶点数组 shape: (n_vertices, 3)，每个顶点是一个三维坐标 (x, y, z)
        cells: 体网格面单元  shape: (n_cells, 3)
        edges: 网格边  shape: (n_edges, 2)，每个边由两个顶点的索引定义
        plane: 平面方程的参数 (a, b, c, d)，表示平面方程 ax + by + cz = d

        """

        tetrahedrons_after_split_negative = []
        tetrahedrons_after_split_positive = []
        split_face_cells = []

        intersection_points_total = []

        intersection_points_with_var = {}
        var_final = {}

        if var != {}:
            intersection_points_with_var = {k: [] for k in var.keys()}
            var_final = {k: [] for k in var.keys()}

        # 遍历每个四面体
        for cell in cells:
            tet = vertices[cell]
            # 计算四面体的交点个数
            intersection_points = self.computer_intersection_point(tet, plane)
            intersection_points = np.unique(intersection_points, axis=0).tolist()
            # 将intersection_points中的元素转换为列表
            intersection_points = [list(v) for v in intersection_points]

            if len(intersection_points) != 0 and var != {}:

                # 循环计算交点的var，这里的var是一个字典,包含‘rho’,‘x’,‘y’,‘z’,以及对应的v各个顶点的四个值
                for i in var.keys():
                    for point in intersection_points:
                        var_value = tetrahedral_lagrange_interpolation(point, tet[0], tet[1], tet[2], tet[3],
                                                                       var[i][cell[0]], var[i][cell[1]],
                                                                       var[i][cell[2]], var[i][cell[3]])

                        intersection_points_with_var[i].append([point, var_value])
            intersection_points_total.extend(intersection_points)

            # 当平面与四面体只有一个交点时
            if len(intersection_points) == 1:
                new_tet = [v for v in tet if not any(np.array_equal(v, ip) for ip in intersection_points)]

                # 判断此时如果所有的顶点都在negative_or_positive所要求的一侧，则直接将此四面体加入到tetrahedrons_after_split中
                distances = np.array([plane[0] * x + plane[1] * y + plane[2] * z + plane[3] for x, y, z in new_tet])
                if all(distances >= 0):
                    tetrahedrons_after_split_positive.append(tet)
                elif all(distances <= 0):
                    tetrahedrons_after_split_negative.append(tet)
                else:
                    continue

            # 当平面与四面体有三个交点时
            elif len(intersection_points) == 3 and not self.check_points(intersection_points, tet):
                intersection_points = self.sort_points_counterclockwise(intersection_points)
                # 将上面三个交点放入到split_cells中
                split_face_cells.append(intersection_points)
                tetrahedra_negative, tetrahedra_vertex_negative = self.split_tetrahedron_three(intersection_points, tet,
                                                                                               plane,
                                                                                               "negative")
                tetrahedra_positive, tetrahedra_vertex_positive = self.split_tetrahedron_three(intersection_points, tet,
                                                                                               plane,
                                                                                               "positive")
                if tetrahedra_positive is not None:
                    tetrahedrons_after_split_positive.extend(tetrahedra_positive)
                if tetrahedra_negative is not None:
                    tetrahedrons_after_split_negative.extend(tetrahedra_negative)

            # 当平面与四面体有四个交点时
            elif len(intersection_points) == 4 and not self.check_points(intersection_points, tet):

                intersection_points = self.sort_points_counterclockwise(intersection_points)

                # 判断intersection_points[0]与intersection_points[1]构成的线段是否与intersection_points[2]与intersection_points[3]构成的线段相交
                segment1 = [intersection_points[1], intersection_points[2]]
                segment2 = [intersection_points[0], intersection_points[3]]

                segment3 = [intersection_points[0], intersection_points[2]]
                segment4 = [intersection_points[1], intersection_points[3]]
                if self.is_line_segments_intersecting_3d(segment1, segment2):
                    split_face_cells.append([intersection_points[0], intersection_points[1], intersection_points[3]])
                    split_face_cells.append([intersection_points[0], intersection_points[2], intersection_points[3]])
                elif self.is_line_segments_intersecting_3d(segment3, segment4):
                    split_face_cells.append([intersection_points[0], intersection_points[1], intersection_points[2]])
                    split_face_cells.append([intersection_points[0], intersection_points[2], intersection_points[3]])
                else:
                    split_face_cells.append([intersection_points[0], intersection_points[1], intersection_points[3]])
                    split_face_cells.append([intersection_points[0], intersection_points[1], intersection_points[2]])

                negative_tetrahedra, negative_side = self.split_tetrahedron_four(intersection_points, tet, plane,
                                                                                 "negative")
                positive_tetrahedra, positive_side = self.split_tetrahedron_four(intersection_points, tet, plane,
                                                                                 "positive")
                if negative_tetrahedra is not None:
                    tetrahedrons_after_split_negative.extend(negative_tetrahedra)
                if positive_tetrahedra is not None:
                    tetrahedrons_after_split_positive.extend(positive_tetrahedra)

            # 平面与四面体没有相交点或者交点均位于四面体的同一条边或者同一个面上
            else:
                status, vertex = self.decide_tetrahedron(tet, plane)
                if status == "negative":
                    tetrahedrons_after_split_negative.append(tet)
                elif status == "positive":
                    tetrahedrons_after_split_positive.append(tet)
                else:
                    print("Error: tetrahedron is not valid")
                    continue

        # 注意：这里可能存在一个问题，就是原来顶点的var与交点之后的var可能会出现问题
        # intersection_points_with_var中一样的点的var值取平均值
        if len(intersection_points_with_var) != 0:
            intersection_points_with_var[i] = np.array(intersection_points_with_var[i])
            intersection_points = intersection_points_with_var[i][:, 0]
            intersection_points_var = intersection_points_with_var[i][:, 1]
            unique_intersection_points = np.unique(intersection_points, axis=0)
            intersection_points_with_var[i] = []
            for point in unique_intersection_points:
                index = np.where(np.all(intersection_points == point, axis=1))[0]
                var_value = np.max(intersection_points_var[index])
                intersection_points_with_var[i].append([point, var_value])
        tetrahedrons_after_split_negative = np.array(tetrahedrons_after_split_negative, dtype=np.float32)
        tetrahedrons_after_split_positive = np.array(tetrahedrons_after_split_positive, dtype=np.float32)

        new_tetrahedrons_negative = np.zeros(
            (tetrahedrons_after_split_negative.shape[0], tetrahedrons_after_split_negative.shape[1]), dtype=int)
        new_tetrahedrons_positive = np.zeros(
            (tetrahedrons_after_split_positive.shape[0], tetrahedrons_after_split_positive.shape[1]), dtype=int)
        # 对vertices_after_split去重
        intersection_points_total = np.array(intersection_points_total)
        intersection_points_total = np.unique(intersection_points_total, axis=0)

        # 对于vertices_after_split中的每个顶点，只是重新计算了非顶点的交点的var值
        for i in var_final.keys():
            var_final[i].extend(var[i])
            for vertex in intersection_points_total:
                # 直接在 intersection_points_with_var 中查找顶点
                index = self.find_vertex_index(vertex, [item[0] for item in intersection_points_with_var[i]])
                if index is not None:
                    var_final[i].append(intersection_points_with_var[i][index][1])
                else:
                    var_final[i].append(np.mean(var))

            for j, value in enumerate(var_final[i]):
                if isinstance(value, (int, float)):
                    var_final[i][j] = value
                else:
                    var_final[i][j] = value[2]
            var_final[i] = np.array(var_final[i], dtype=np.float32)

        # intersection_points_total
        vertices_after_split = np.vstack((vertices, intersection_points_total))

        # 重新映射顶点索引
        for i, tet in enumerate(tetrahedrons_after_split_negative):
            new_tetrahedrons_negative[i] = [self.find_vertex_index(vertex, vertices_after_split) for vertex in tet]

        for i, tet in enumerate(tetrahedrons_after_split_positive):
            new_tetrahedrons_positive[i] = [self.find_vertex_index(vertex, vertices_after_split) for vertex in tet]

        for i, split_face_cell in enumerate(split_face_cells):
            split_face_cells[i] = [self.find_vertex_index(vertex, vertices_after_split) for vertex in split_face_cell]

        tetrahedrons_after_split_negative = new_tetrahedrons_negative
        tetrahedrons_after_split_positive = new_tetrahedrons_positive
        vertices_after_split = np.array(vertices_after_split, dtype=np.float32)

        tetrahedrons_after_split_negative = np.array(tetrahedrons_after_split_negative, dtype=int)
        tetrahedrons_after_split_positive = np.array(tetrahedrons_after_split_positive, dtype=int)

        split_face_cells = np.array(split_face_cells, dtype=int)

        return tetrahedrons_after_split_negative, tetrahedrons_after_split_positive, vertices_after_split, split_face_cells, var_final

    def split(self):

        """
        return  two section of cutting Mesh
        """
        points = self.originalMesh.gl_points
        cells = self.originalMesh.cells.reshape(-1, 4)
        var = self.originalMesh.gl_var


        negative, positive, vertices, face_cells, var = self.split_tetrahedron(points, cells, self.cuttingPlane, var)

        A = BodyMesh(vertices, positive, self.originalMesh.cell_type, var, None, self.cuttingPlane)
        B = BodyMesh(vertices, negative, self.originalMesh.cell_type, var, None, self.cuttingPlane)
        C = FaceMesh(vertices, face_cells, 'triangle', var, None, self.cuttingPlane)

        return A, B, C


