import numpy as np
from Utils.Compute.Interpolation import tetrahedral_lagrange_interpolation
from Utils.Mesh.MeshClass import FaceMesh, BodyMesh


# 网格切割器
class MeshSplitter:

    def __init__(self, body_mesh, cutting_plane):

        self.originalMesh = body_mesh   # 待切割网格
        self.cuttingPlane = cutting_plane  # 切平面方程

    # ---- 工具函数 ----

    def is_close(self, vertex1, vertex2, tolerance=1e-8):
        """判断两个顶点是否近似相等。"""
        return all(abs(v1 - v2) < tolerance for v1, v2 in zip(vertex1, vertex2))

    def find_vertex_index(self, vertex, vertices, tolerance=1e-8):
        """在顶点列表中查找顶点的索引，找不到返回 None。"""
        for idx, v in enumerate(vertices):
            if self.is_close(vertex, v, tolerance):
                return idx
        return None

    def is_tetrahedron(self, vertices):
        """判断四个顶点是否构成非退化的四面体（不共面）。"""
        a = np.ones((4, 4), dtype=np.float32)
        a[:, :-1] = vertices
        det = np.linalg.det(a)
        return abs(det) > 1e-5

    def _is_triangle_degenerate(self, vertices):
        """判断三角形是否退化（面积接近零）。"""
        v0, v1, v2 = vertices
        cross = np.cross(v1 - v0, v2 - v0)
        return np.linalg.norm(cross) < 1e-12

    def _plane_point(self, p1, p2, dist1, dist2):
        """计算线段 p1-p2 与平面的交点。
        dist1 = f(p1), dist2 = f(p2)，交点在 dist 从 dist1 到 dist2 过零处。
        """
        t = dist1 / (dist1 - dist2)  # dist1 - dist2 != 0 因为符号不同
        return (p1 + t * (p2 - p1)).astype(np.float32)

    # ---- 四面体拆分核心 ----

    def _split_one_tetrahedron(self, tet_vertices, plane):
        """用平面对单个四面体进行拆分。

        Returns:
            neg_tets:  负侧的四面体列表
            pos_tets:  正侧的四面体列表
            face_tris: 切面上的三角形列表
        """
        a, b, c, d_plane = plane
        tet = np.array(tet_vertices, dtype=np.float64)

        # 1. 计算有符号距离并分类
        dists = np.array([a * x + b * y + c * z + d_plane for x, y, z in tet])
        eps = 1e-10

        pos_idx = [i for i in range(4) if dists[i] > eps]
        neg_idx = [i for i in range(4) if dists[i] < -eps]
        zero_idx = [i for i in range(4) if abs(dists[i]) <= eps]

        n_pos, n_neg, n_zero = len(pos_idx), len(neg_idx), len(zero_idx)

        neg_tets = []
        pos_tets = []
        face_tris = []

        # ---- Case A: 四面体完全在单侧 ----
        if n_neg == 0:
            pos_tets.append(tet.tolist())
            return neg_tets, pos_tets, face_tris
        if n_pos == 0:
            neg_tets.append(tet.tolist())
            return neg_tets, pos_tets, face_tris

        # ---- Case B: 有顶点在平面上 ----
        if n_zero > 0:
            return self._split_with_on_plane(tet, dists, eps)

        # ---- Case C: 3-1 分割（1 vs 3）----
        if (n_pos == 1 and n_neg == 3) or (n_pos == 3 and n_neg == 1):
            single_idx = pos_idx[0] if n_pos == 1 else neg_idx[0]
            triple_idx = neg_idx if n_pos == 1 else pos_idx
            to_pos = (n_pos == 1)

            V_single = tet[single_idx]
            V0, V1, V2 = [tet[i] for i in triple_idx]

            # 三条棱上的交点
            P0 = self._plane_point(V_single, V0, dists[single_idx], dists[triple_idx[0]])
            P1 = self._plane_point(V_single, V1, dists[single_idx], dists[triple_idx[1]])
            P2 = self._plane_point(V_single, V2, dists[single_idx], dists[triple_idx[2]])

            # single 侧：1 个小四面体
            single_tet = [V_single.tolist(), P0.tolist(), P1.tolist(), P2.tolist()]

            # triple 侧：三角棱柱 → 3 个四面体
            triple_tets = [
                [V0.tolist(), V1.tolist(), V2.tolist(), P2.tolist()],
                [V0.tolist(), V1.tolist(), P2.tolist(), P1.tolist()],
                [V0.tolist(), P1.tolist(), P2.tolist(), P0.tolist()],
            ]

            # 切面三角形
            face_tris.append([P0.tolist(), P1.tolist(), P2.tolist()])

            if to_pos:
                pos_tets.append(single_tet)
                neg_tets.extend(triple_tets)
            else:
                neg_tets.append(single_tet)
                pos_tets.extend(triple_tets)

        # ---- Case D: 2-2 分割 ----
        elif n_pos == 2 and n_neg == 2:
            A, B = pos_idx
            C, D = neg_idx

            Va, Vb = tet[A], tet[B]
            Vc, Vd = tet[C], tet[D]

            # 四条棱上的交点
            Pac = self._plane_point(Va, Vc, dists[A], dists[C])
            Pad = self._plane_point(Va, Vd, dists[A], dists[D])
            Pbc = self._plane_point(Vb, Vc, dists[B], dists[C])
            Pbd = self._plane_point(Vb, Vd, dists[B], dists[D])

            # 切面四边形 Pac-Pad-Pbd-Pbc 拆为两个三角形
            face_tris.append([Pac.tolist(), Pad.tolist(), Pbd.tolist()])
            face_tris.append([Pac.tolist(), Pbd.tolist(), Pbc.tolist()])

            # 正侧 (Va, Vb) 的三角棱柱 → 3 个四面体
            pos_tets.extend([
                [Va.tolist(), Pac.tolist(), Pad.tolist(), Pbd.tolist()],
                [Va.tolist(), Pac.tolist(), Pbd.tolist(), Pbc.tolist()],
                [Va.tolist(), Pbc.tolist(), Pbd.tolist(), Vb.tolist()],
            ])

            # 负侧 (Vc, Vd) 的三角棱柱 → 3 个四面体
            neg_tets.extend([
                [Vc.tolist(), Pac.tolist(), Pbc.tolist(), Pbd.tolist()],
                [Vc.tolist(), Pac.tolist(), Pbd.tolist(), Pad.tolist()],
                [Vc.tolist(), Pad.tolist(), Pbd.tolist(), Vd.tolist()],
            ])

        else:
            # 回退：不应到达这里
            if all(d <= eps for d in dists):
                neg_tets.append(tet.tolist())
            else:
                pos_tets.append(tet.tolist())

        return neg_tets, pos_tets, face_tris

    def _split_with_on_plane(self, tet, dists, eps):
        """处理有顶点在平面上的情况。

        不走通用的 3-1/2-2 分支，而是直接根据具体情况构造合法的拆分，
        避免产生退化的切面三角形。
        """
        neg_tets = []
        pos_tets = []
        face_tris = []

        pos_idx = [i for i in range(4) if dists[i] > eps]
        neg_idx = [i for i in range(4) if dists[i] < -eps]
        zero_idx = [i for i in range(4) if abs(dists[i]) <= eps]

        n_pos, n_neg = len(pos_idx), len(neg_idx)

        # ---- B0: 所有非零距离顶点在同侧（平面仅擦过一个顶点）----
        if n_pos == 0 or n_neg == 0:
            if n_pos == 0:
                neg_tets.append(tet.tolist())
            else:
                pos_tets.append(tet.tolist())
            return neg_tets, pos_tets, face_tris

        # ---- B1: 1 个顶点在平面上，其余分属两侧 ----
        if n_zero == 1:
            on_idx = zero_idx[0]
            V_on = tet[on_idx]

            # 从平面另一侧的每个顶点到 V_on 的线段上计算交点（= V_on 自身）
            # 真正的切面交点在两侧顶点之间的棱上

            if n_pos == 1 and n_neg == 2:
                # 正侧 1 个，负侧 2 个，平面上 1 个 → 实际构成 (1+1) vs 2
                A_pos = pos_idx[0]
                B_neg, C_neg = neg_idx
                Va, Vb, Vc = tet[A_pos], tet[B_neg], tet[C_neg]

                # V_on 归入正侧：正侧 = {Va, V_on}，负侧 = {Vb, Vc} → 2-2
                # 交点：Va-Vb, Va-Vc, V_on-Vb, V_on-Vc
                Pab = self._plane_point(Va, Vb, dists[A_pos], dists[B_neg])
                Pac = self._plane_point(Va, Vc, dists[A_pos], dists[C_neg])
                Pon_b = self._plane_point(V_on, Vb, dists[on_idx], dists[B_neg])
                Pon_c = self._plane_point(V_on, Vc, dists[on_idx], dists[C_neg])

                # 切面四边形 → 两个三角形
                face_tris.append([Pab.tolist(), Pon_b.tolist(), Pon_c.tolist()])
                face_tris.append([Pab.tolist(), Pon_c.tolist(), Pac.tolist()])

                # 正侧 (Va, V_on)
                pos_tets.extend([
                    [Va.tolist(), Pab.tolist(), Pac.tolist(), Pon_c.tolist()],
                    [Va.tolist(), Pab.tolist(), Pon_c.tolist(), Pon_b.tolist()],
                    [Va.tolist(), Pon_b.tolist(), Pon_c.tolist(), V_on.tolist()],
                ])
                # 负侧 (Vb, Vc)
                neg_tets.extend([
                    [Vb.tolist(), Pab.tolist(), Pon_b.tolist(), Pon_c.tolist()],
                    [Vb.tolist(), Pab.tolist(), Pon_c.tolist(), Pac.tolist()],
                    [Vb.tolist(), Pac.tolist(), Pon_c.tolist(), Vc.tolist()],
                ])

            elif n_pos == 2 and n_neg == 1:
                # 正侧 2 个，负侧 1 个，平面上 1 个 → 实际构成 (2) vs (1+1)
                A_pos, B_pos = pos_idx
                C_neg = neg_idx[0]
                Va, Vb, Vc = tet[A_pos], tet[B_pos], tet[C_neg]

                # V_on 归入负侧：正侧 = {Va, Vb}，负侧 = {Vc, V_on} → 2-2
                Pac = self._plane_point(Va, Vc, dists[A_pos], dists[C_neg])
                Pbc = self._plane_point(Vb, Vc, dists[B_pos], dists[C_neg])
                Pa_on = self._plane_point(Va, V_on, dists[A_pos], dists[on_idx])
                Pb_on = self._plane_point(Vb, V_on, dists[B_pos], dists[on_idx])

                face_tris.append([Pac.tolist(), Pa_on.tolist(), Pb_on.tolist()])
                face_tris.append([Pac.tolist(), Pb_on.tolist(), Pbc.tolist()])

                # 正侧 (Va, Vb)
                pos_tets.extend([
                    [Va.tolist(), Pac.tolist(), Pa_on.tolist(), Pb_on.tolist()],
                    [Va.tolist(), Pac.tolist(), Pb_on.tolist(), Pbc.tolist()],
                    [Va.tolist(), Pbc.tolist(), Pb_on.tolist(), Vb.tolist()],
                ])
                # 负侧 (Vc, V_on)
                neg_tets.extend([
                    [Vc.tolist(), Pac.tolist(), Pbc.tolist(), Pb_on.tolist()],
                    [Vc.tolist(), Pac.tolist(), Pb_on.tolist(), Pa_on.tolist()],
                    [Vc.tolist(), Pa_on.tolist(), Pb_on.tolist(), V_on.tolist()],
                ])

            elif n_pos == 1 and n_neg == 1:
                # 平面经过两个顶点（on + pos 一侧，on + neg 一侧）→ 实际 (1+1) vs (1+1)
                A_pos = pos_idx[0]
                C_neg = neg_idx[0]
                Va, Vc = tet[A_pos], tet[C_neg]

                Pac = self._plane_point(Va, Vc, dists[A_pos], dists[C_neg])

                # 平面上只有两个点 V_on 和 Pac → 切面是一条线，不是面
                # V_on 归入正侧，正侧 = {Va, V_on}，负侧 = {Vc}
                Pon_c = self._plane_point(V_on, Vc, dists[on_idx], dists[C_neg])
                Pa_on = self._plane_point(Va, V_on, dists[A_pos], dists[on_idx])

                # 切面三角形：V_on-Pac-Pon_c（三点共线退化 → 跳过）
                # 直接构造 2-2 拆分
                pos_tets.extend([
                    [Va.tolist(), Pac.tolist(), Pa_on.tolist(), Pon_c.tolist()],
                    [Va.tolist(), Pon_c.tolist(), Pa_on.tolist(), V_on.tolist()],
                ])
                neg_tets.append([Vc.tolist(), Pac.tolist(), Pon_c.tolist(), Pon_c.tolist()])
                # 这种退化情况下只保一侧
                neg_tets.pop()  # 丢弃退化
                neg_tets.append([Vc.tolist(), Pac.tolist(), Pon_c.tolist(), Pa_on.tolist()])
                neg_tets.append([Vc.tolist(), Pa_on.tolist(), Pon_c.tolist(), V_on.tolist()])

                # 不添加切面（退化情况）

        # ---- B2: 2 个顶点在平面上 ----
        elif n_zero == 2:
            # 每侧各放一个 on-plane 顶点
            on0, on1 = zero_idx

            if n_pos == 1 and n_neg == 1:
                A_pos, C_neg = pos_idx
                Va, Vc = tet[A_pos], tet[C_neg]
                V_on0, V_on1 = tet[on0], tet[on1]

                # 平面经过 V_on0 和 V_on1，另两个顶点在两侧
                # 这是标准的 2-2 分割，on-plane 顶点分配到两侧
                Pa_on0 = self._plane_point(Va, V_on0, dists[A_pos], dists[on0])
                Pa_on1 = self._plane_point(Va, V_on1, dists[A_pos], dists[on1])
                Pc_on0 = self._plane_point(Vc, V_on0, dists[C_neg], dists[on0])
                Pc_on1 = self._plane_point(Vc, V_on1, dists[C_neg], dists[on1])

                face_tris.append([Pa_on0.tolist(), Pc_on0.tolist(), Pc_on1.tolist()])
                face_tris.append([Pa_on0.tolist(), Pc_on1.tolist(), Pa_on1.tolist()])

                pos_tets.extend([
                    [Va.tolist(), Pa_on0.tolist(), Pa_on1.tolist(), V_on0.tolist()],
                    [Va.tolist(), Pa_on0.tolist(), V_on0.tolist(), V_on1.tolist()],
                    [Va.tolist(), Pa_on1.tolist(), Pa_on0.tolist(), V_on1.tolist()],
                ])
                neg_tets.extend([
                    [Vc.tolist(), Pc_on0.tolist(), Pc_on1.tolist(), V_on0.tolist()],
                    [Vc.tolist(), Pc_on0.tolist(), V_on0.tolist(), V_on1.tolist()],
                    [Vc.tolist(), Pc_on1.tolist(), Pc_on0.tolist(), V_on1.tolist()],
                ])

            elif n_pos == 2 and n_neg == 0:
                pos_tets.append(tet.tolist())
            elif n_pos == 0 and n_neg == 2:
                neg_tets.append(tet.tolist())

        # ---- B3: 3 个顶点在平面上 ----
        elif n_zero == 3:
            # 几乎整个四面体在平面上 → 归入另一侧
            if n_pos == 1:
                pos_tets.append(tet.tolist())
            elif n_neg == 1:
                neg_tets.append(tet.tolist())

        return neg_tets, pos_tets, face_tris

    def _filter_degenerate_tets(self, tet_list):
        """过滤掉退化（共面/零体积）的四面体。"""
        valid = []
        for tet in tet_list:
            verts = np.array(tet, dtype=np.float32)
            if len(tet) == 4 and self.is_tetrahedron(verts):
                valid.append(tet)
        return valid

    def _filter_degenerate_faces(self, face_list, vertices):
        """过滤掉退化（零面积）的切面三角形。"""
        valid = []
        for tri in face_list:
            if len(tri) < 3:
                continue
            try:
                v0 = np.array(vertices[tri[0]] if isinstance(tri[0], (int, np.integer))
                              else tri[0], dtype=np.float64)
                v1 = np.array(vertices[tri[1]] if isinstance(tri[1], (int, np.integer))
                              else tri[1], dtype=np.float64)
                v2 = np.array(vertices[tri[2]] if isinstance(tri[2], (int, np.integer))
                              else tri[2], dtype=np.float64)
                if not self._is_triangle_degenerate([v0, v1, v2]):
                    valid.append(tri)
            except (IndexError, TypeError):
                continue
        return valid

    # ---- 主拆分函数 ----

    def split_tetrahedron(self, vertices, cells, plane, var=None):
        """根据平面将四面体网格拆分为负侧和正侧两部分。"""
        if var is None:
            var = {}

        tetrahedrons_neg = []
        tetrahedrons_pos = []
        split_face_tris = []

        all_new_points = []
        new_point_vars = {k: [] for k in var.keys()}

        # 遍历每个四面体
        for cell_idx, cell in enumerate(cells):
            tet = vertices[cell]

            neg_tets, pos_tets, face_tris = self._split_one_tetrahedron(tet, plane)

            # 收集拆分结果（过滤退化四面体）
            tetrahedrons_neg.extend(self._filter_degenerate_tets(neg_tets))
            tetrahedrons_pos.extend(self._filter_degenerate_tets(pos_tets))
            split_face_tris.extend(face_tris)

            # 收集新增交点并计算其变量值
            for t in neg_tets + pos_tets:
                for v in t:
                    if self.find_vertex_index(v, tet) is None and \
                       self.find_vertex_index(v, all_new_points) is None:
                        all_new_points.append(v)
                        if var:
                            for k in var.keys():
                                # var 已统一为 1D 标量格式，直接插值
                                val = tetrahedral_lagrange_interpolation(
                                    v, tet[0], tet[1], tet[2], tet[3],
                                    var[k][cell[0]], var[k][cell[1]],
                                    var[k][cell[2]], var[k][cell[3]])
                                new_point_vars[k].append(val)

        # ---- 顶点去重与索引重建 ----
        all_new_points = np.array(all_new_points, dtype=np.float32) \
            if all_new_points else np.empty((0, 3), dtype=np.float32)

        vertices_after = np.vstack((vertices, all_new_points)) \
            if len(all_new_points) > 0 else vertices.copy()

        # ---- 变量合并 ----
        var_final = {}
        if var:
            for k in var.keys():
                existing = np.asarray(var[k], dtype=np.float32).ravel()
                new_vals = np.asarray(new_point_vars.get(k, []), dtype=np.float32)
                var_final[k] = np.concatenate([existing, new_vals])

        # ---- 重建顶点索引 ----
        def rebuild_indices(tet_list):
            result = np.zeros((len(tet_list), 4), dtype=int)
            for i, tet in enumerate(tet_list):
                for j, v in enumerate(tet):
                    idx = self.find_vertex_index(v, vertices_after)
                    if idx is None:
                        idx = 0
                    result[i, j] = idx
            return result

        neg_cells = rebuild_indices(tetrahedrons_neg)
        pos_cells = rebuild_indices(tetrahedrons_pos)

        # 切面三角形重建索引（4列截断为3列）
        if split_face_tris:
            face_raw = []
            for tri in split_face_tris:
                idx_tri = []
                for v in tri[:3]:
                    idx = self.find_vertex_index(v, vertices_after)
                    if idx is None:
                        idx = 0
                    idx_tri.append(idx)
                face_raw.append(idx_tri)
            face_cells = np.array(face_raw, dtype=int)
        else:
            face_cells = np.empty((0, 3), dtype=int)

        # 过滤退化的切面三角形
        face_cells = self._filter_degenerate_faces(face_cells.tolist(), vertices_after)
        face_cells = np.array(face_cells, dtype=int) if face_cells else np.empty((0, 3), dtype=int)

        return neg_cells, pos_cells, vertices_after.astype(np.float32), face_cells, var_final

    def split(self):
        """执行切割，返回 (负侧 BodyMesh, 正侧 BodyMesh, 切面 FaceMesh)。"""
        points = self.originalMesh.gl_points
        cells = self.originalMesh.cells.reshape(-1, 4)

        # 将 gl_var 从 OpenGL 3列格式 (N,3) 转换为 1D 标量格式 (N,)
        # gl_var = {name: column_stack((zeros, zeros, values))}
        # -> var_1d = {name: values}  (纯标量，供插值使用)
        gl_var = self.originalMesh.gl_var
        var_1d = {}
        for k, v in gl_var.items():
            v_arr = np.asarray(v, dtype=np.float32)
            if v_arr.ndim == 2 and v_arr.shape[1] == 3:
                var_1d[k] = v_arr[:, 2].copy()  # 提取 Z 列（实际标量值）
            else:
                var_1d[k] = v_arr

        negative, positive, vertices, face_cells, var_out = \
            self.split_tetrahedron(points, cells, self.cuttingPlane, var_1d)

        # ---- 修正切面的法线，消除凹凸不平的阴影 ----
        a, b, c, d_plane = self.cuttingPlane
        plane_normal = np.array([a, b, c], dtype=np.float32)
        nrm = np.linalg.norm(plane_normal)
        if nrm > 1e-10:
            plane_normal /= nrm

        # 修正三角形绕序：确保所有面的法线指向平面法线方向
        if face_cells.size > 0:
            fixed_face_cells = []
            for tri in face_cells:
                v0, v1, v2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
                face_normal = np.cross(v1 - v0, v2 - v0)
                if np.dot(face_normal, plane_normal) < 0:
                    tri = [tri[0], tri[2], tri[1]]  # 翻转绕序
                fixed_face_cells.append(tri)
            face_cells = np.array(fixed_face_cells, dtype=int)

        if face_cells.size > 0:
            C = FaceMesh(vertices, face_cells, 'triangle', var_out if var_out else {})
            # 用统一的平面法线覆盖计算出的法线，确保均匀平坦的光照
            C.gl_normal[:] = plane_normal
        else:
            C = FaceMesh(np.empty((0, 3), dtype=np.float32),
                         np.empty((0, 3), dtype=np.uint32), 'triangle', {})

        A = BodyMesh(vertices, positive, self.originalMesh.cell_type, var_out)
        B = BodyMesh(vertices, negative, self.originalMesh.cell_type, var_out)

        return A, B, C
