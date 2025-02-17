import gmsh
import pygmsh
import numpy as np


def _2D_generate_mesh(shape, mesh_size, algorithm, selection):
    with pygmsh.geo.Geometry() as geom:
        if shape[0] == "circle":
            geom.add_circle([shape[1], shape[2]], shape[4], mesh_size=mesh_size)
        elif shape[0] == "rectangle":
            rectangle = geom.add_rectangle(shape[1], shape[1] + shape[4], shape[2], shape[2] + shape[5], 0,
                               mesh_size=mesh_size)
        elif shape[0] == "other":
            points = shape[1]
            poly = geom.add_polygon(points, mesh_size=mesh_size)
            geom.add_physical(poly, "Polygon")

        # 设置算法
        mesh = geom.generate_mesh(int(algorithm))

    return mesh

def _2D_generate_stru_mesh(shape, mesh_size, selection):
    with pygmsh.geo.Geometry() as geom:
        if shape[0] == "circle":
            center = [shape[1], shape[2], 0]
            radius = shape[4]
            node_density_factor = 1  # 可调整的节点密度因子

            circumference = 2 * np.pi * radius
            total_nodes_along_circle = int(circumference / mesh_size * node_density_factor) + 1

            num_sectors = min(range(5, total_nodes_along_circle),
                                   key=lambda num_sectors: abs((total_nodes_along_circle // num_sectors) * num_sectors - total_nodes_along_circle))

            num_nodes_per_arc = total_nodes_along_circle // num_sectors + 1

            # 添加圆心点
            center_point = geom.add_point(center, mesh_size=mesh_size)

            # 定义每个扇形的角度点
            angles = np.linspace(0, 2 * np.pi, num_sectors + 1)[:-1]
            points = []
            for angle in angles:
                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)
                point = geom.add_point([x, y, center[2]], mesh_size=mesh_size)
                points.append(point)

            # 创建半径线和圆弧
            lines = []
            arcs = []
            for i in range(num_sectors):
                line = geom.add_line(center_point, points[i])
                lines.append(line)
                arc = geom.add_circle_arc(points[i], center_point, points[(i + 1) % num_sectors])
                arcs.append(arc)

            num_nodes_per_radius = int(radius / mesh_size * node_density_factor) + 1

            # 创建曲线环和平面表面
            surfaces = []
            for i in range(num_sectors):
                # 使用负号表示反向的线
                curve_loop = geom.add_curve_loop([lines[i], arcs[i], -lines[(i + 1) % num_sectors]])
                surface = geom.add_plane_surface(curve_loop)
                surfaces.append(surface)

                # 获取当前扇形的三条边
                sector_lines = [lines[i], arcs[i], -lines[(i + 1) % num_sectors]]
                for line in sector_lines:
                    if line in arcs:
                        num_nodes = num_nodes_per_arc
                    else:
                        num_nodes = num_nodes_per_radius
                    # 设置每条边上的节点数量、节点分布类型和系数
                    geom.set_transfinite_curve(line, num_nodes=num_nodes, mesh_type='Progression', coeff=1.0)

                # 设置当前扇形面的超限属性，使其生成结构化网格
                geom.set_transfinite_surface(surface, selection, corner_pts=[center_point, points[i],
                                                                          points[(i + 1) % num_sectors]])
        elif shape[0] == "rectangle":
            rectangle = geom.add_rectangle(shape[1], shape[1] + shape[4], shape[2], shape[2] + shape[5], 0,
                                           mesh_size=mesh_size)
            # 获取矩形的四条边
            lines = rectangle.lines
            # 设置每条边超限属性
            for line in lines:
                # 计算直线的长度
                p1 = line.points[0].x
                p2 = line.points[1].x
                length = np.linalg.norm(np.array(p2) - np.array(p1))

                # 根据长度和网格尺寸计算点数
                num_nodes = int(np.ceil(length / mesh_size))

                # 设置每条边上的节点数量、节点分布类型和系数
                geom.set_transfinite_curve(line, num_nodes=num_nodes + 1, mesh_type='Progression', coeff=1.0)

            # 设置矩形面的超限属性，使其生成结构化网格
            geom.set_transfinite_surface(rectangle.surface, selection, corner_pts=[])

        # 设置算法
        mesh = geom.generate_mesh()

    return mesh

def _3D_generate_mesh(shape, mesh_size, algorithm, mesh_type):
    gmsh.initialize()
    gmsh.model.add("model")
    if shape[0] == "box":
        gmsh.model.occ.addBox(shape[1], shape[2], shape[3], shape[4], shape[5], shape[6])
    elif shape[0] == "sphere":
        gmsh.model.occ.addSphere(shape[1], shape[2], shape[3], shape[4])
    elif shape[0] == "other":
        # 定义点和面
        point = shape[1]
        face = shape[2]

        # 添加点
        points = [gmsh.model.occ.addPoint(*pt, mesh_size) for pt in point]

        # 创建一个存储线段的字典
        lines_dict = {}
        lines = []

        # 添加线段
        def add_line(p1, p2):
            if (p1, p2) not in lines_dict and (p2, p1) not in lines_dict:
                line_id = gmsh.model.occ.addLine(p1, p2)
                lines_dict[(p1, p2)] = line_id
                lines_dict[(p2, p1)] = line_id
                return line_id
            return lines_dict.get((p1, p2)) or lines_dict.get((p2, p1))

        for f in face:
            for i in range(len(f)):
                p1 = f[i]
                p2 = f[(i + 1) % len(f)]
                add_line(p1, p2)

        # 根据存储的线段定义线环
        def get_curve_loop(vertex_ids):
            loop_lines = []
            for i in range(len(vertex_ids)):
                p1 = vertex_ids[i]
                p2 = vertex_ids[(i + 1) % len(vertex_ids)]
                line_id = lines_dict.get((p1, p2)) or lines_dict.get((p2, p1))
                if line_id is not None:
                    loop_lines.append(line_id)
                else:
                    raise ValueError(f"Line segment ({p1}, {p2}) not found in lines_dict.")
            return gmsh.model.occ.addCurveLoop(loop_lines)

        # 生成面环（face loops）
        def generate_face_loops(faces):
            face_loops = []
            for face in faces:
                face_loop = get_curve_loop(face)
                face_loops.append(face_loop)
            return face_loops

        # 计算面环
        face_loops = generate_face_loops(face)

        # 添加面
        faces = [gmsh.model.occ.addPlaneSurface([loop]) for loop in face_loops]

        # 创建体
        surface_loop = gmsh.model.occ.addSurfaceLoop(faces)
        gmsh.model.occ.addVolume([surface_loop])

    # 同步几何模型
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.setSize(gmsh.model.getEntities(0), mesh_size)
    gmsh.option.setNumber("Mesh.Algorithm3D", int(algorithm))

    gmsh.model.mesh.generate(mesh_type)
    node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
    element_tags, element_types, element_nodes = gmsh.model.mesh.getElements(-1, -1)

    elementTypes, elementTags, nodeTags = gmsh.model.mesh.getElements(mesh_type, -1)

    # 整理单元数据
    cells = []
    for elem_node_tags in nodeTags:
        # 将节点标签减去 1 以使索引从 0 开始
        cells.append([tag - 1 for tag in elem_node_tags])

    cells_array = np.array(cells[0])
    n_elements = cells_array.shape[0]  # 获取总元素数量

    new_shape = (len(nodeTags), n_elements // (mesh_type + 1), mesh_type + 1)  # 新形状
    cells = cells_array.reshape(new_shape)

    # 如果需要只保留二维数组
    cells = cells.reshape(-1, mesh_type + 1)  # 将三维数组转换为二维数组

    gmsh.finalize()

    return node_coords, element_nodes, cells



