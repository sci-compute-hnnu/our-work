import pygmsh


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

