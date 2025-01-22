import gmsh
import pygmsh
import numpy as np


def _2D_generate_mesh(shape, mesh_size, algorithm):
    with pygmsh.geo.Geometry() as geom:
        if shape[0] == "circle":
            geom.add_circle([shape[1], shape[2]], shape[4], mesh_size=mesh_size)
        elif shape[0] == "rectangle":
            geom.add_rectangle(shape[1], shape[1] + shape[4], shape[2], shape[2] + shape[5], 0,
                               mesh_size=mesh_size)
        elif shape[0] == "other":
            points = shape[1]
            poly = geom.add_polygon(points, mesh_size=mesh_size)
            geom.add_physical(poly, "Polygon")

        # 设置算法
        mesh = geom.generate_mesh(int(algorithm))

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



