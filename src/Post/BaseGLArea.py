import ctypes
import gi
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from gi.repository import Gtk, Gdk
gi.require_version('Gtk', '3.0')

from Utils.OpenGL.GLTransformUtils import set_perspective_matrix
from Utils.OpenGL.GLTransformUtils import set_view_matrix

from Utils.OpenGL.GLShader import vertex_src
from Utils.OpenGL.GLShader import fragment_src
from Utils.OpenGL.GLShader import axes_vertex_src
from Utils.OpenGL.GLShader import axes_fragment_src


class base_glarea:

    def __init__(self):

        # GTK的openGL渲染引擎
        self.glarea = Gtk.GLArea()

        # 多网格渲染数据 {mesh_index: bundle_dict}
        self.mesh_bundles = {}

        # 用于变量着色模式的全局选项
        self.var_opt = 'Neutral Mode'

        # 着色器程序
        self.program = None

        # 旋转角度和点击坐标
        self.angle_x = 0
        self.angle_y = 0
        self.click_x = 0
        self.click_y = 0

        # 控制平移
        self.translate_x = 0
        self.translate_y = 0

        # 初始化网格时显示的大小
        self.change_size = 1

        # 记录相较于初始化大小的比例
        self.size = 1

        # 滑轮移动时缩放的比例
        self.scale = 1.0  # 缩放因子

        self.zoom_sensitivity = 0.03  # 缩放灵敏度
        self.rotation_sensitivity = 0.5  # 旋转灵敏度
        self.translation_sensitivity = 0.01  # 平移敏感度

        # 中心点 (4阶向量) — 所有网格的合并包围盒中心
        self.center = np.array([0, 0, 0, 1])

        # 旋转矩阵 (4阶方阵)
        self.rotation_matrix = np.eye(4, dtype=np.float32)

        # 平移矩阵 (4阶方阵)
        self.translation_matrix = np.eye(4, dtype=np.float32)

        # 观察矩阵 (4阶方阵)
        self.view_matrix = np.eye(4, dtype=np.float32)

        # 透视投影矩阵 (4阶方阵)
        self.projection_matrix = None

        # 设定面的颜色和边的颜色 (默认)
        self.face_color = [0.5, 0.5, 0.5, 1]
        self.edge_color = [0.1, 0.0, 0.5, 0.3]  # 暗紫色，透明度为0.3
        self.point_color = [0.1, 0.0, 0.5, 0.3]

        # 是否画边和面和点 (默认直接绘制面)
        self.face_draw = True
        self.edge_draw = False
        self.points_draw = False
        self.gmsh_draw = False
        self.var_draw = False
        self.is_show_smallAxes = True

        # 背景颜色（默认）
        self.back_red = 0.35
        self.back_green = 0.35
        self.back_blue = 0.4655
        self.back_alpha = 1.0

        # 获取Uniform变量的位置
        self.faceColor_location = 0
        self.edgeColor_location = 0
        self.pointColor_location = 0
        self.center_location = 0
        self.isEdge_location = 0
        self.isPoint_location = 0
        self.isGmsh_location = 0
        self.isVar_location = 0
        self.rotation_loc = 0
        self.translation_loc = 0
        self.projection_loc = 0
        self.view_loc = 0
        self.light_position_eye_location = 0
        self.gmsh_light_position_eye_location = 0
        self.ambientStrengthLoc = 0
        self.specularStrengthLoc = 0
        self.shininessLoc = 0
        self.lightColorLoc = 0

        # 光照位置
        self.light_position_eye = np.array([0, 0, 0], dtype=np.float32)
        self.gmsh_light_position_eye = np.array([0, 0, 0], dtype=np.float32)

        # 光照参数
        self.ambient_strength = 0.18      # 环境光强度 [0, 1]
        self.specular_strength = 0.45     # 镜面反射强度 [0, 1]
        self.shininess = 48.0             # 高光锐度 (越大高光越集中)
        self.light_color = np.array([1.0, 0.98, 0.95], dtype=np.float32)  # 暖白色光源

        self.glarea.set_auto_render(True)
        self.glarea.set_has_depth_buffer(True)

        # 鼠标按压
        self.glarea.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.glarea.connect('button-press-event', self.on_button_press)
        # 鼠标移动
        self.glarea.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        self.glarea.connect('motion-notify-event', self.on_mouse_move)
        # 滚轮滑动
        self.glarea.add_events(Gdk.EventMask.SCROLL_MASK)
        self.glarea.connect('scroll-event', self.on_scroll)

    # --- 多网格管理 ---

    def _prepare_var_data(self, mesh):
        """从 mesh.gl_var 中提取当前 color_opt 对应的变量数据，做归一化处理。"""
        vars_dict = mesh.gl_var if hasattr(mesh, 'gl_var') else {}
        if self.var_opt == 'Neutral Mode' or self.var_opt not in vars_dict:
            return np.array([], dtype=np.float32)

        raw = np.array(vars_dict[self.var_opt], dtype=np.float32)
        last_col = raw[:, -1].reshape(-1, 1)
        v_min, v_max = np.min(last_col), np.max(last_col)
        if v_max - v_min > 1e-9:
            last_col = (last_col - v_min) / (v_max - v_min)
        raw[:, -1] = last_col.reshape(-1)
        return raw

    def add_mesh(self, index, mesh):
        """为一个网格创建 OpenGL 资源并加入渲染列表。"""
        vertices = mesh.gl_points
        edges = mesh.gl_edges

        if mesh.cell_type in ('tetrahedron', 'hexahedron'):
            surface_mesh = mesh.surface_mesh
        else:
            surface_mesh = mesh

        faces = surface_mesh.gl_cells
        normals = surface_mesh.gl_normal
        var_data = self._prepare_var_data(surface_mesh)

        try:
            gl = self.glarea.get_context()
            gl.make_current()

            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)

            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)

            if len(var_data) == 0:
                con_data = np.concatenate((vertices, normals))
            else:
                con_data = np.concatenate((vertices, normals, var_data))
            glBufferData(GL_ARRAY_BUFFER, con_data.nbytes, con_data, GL_STATIC_DRAW)

            ibo_edges = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo_edges)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, edges.nbytes, edges, GL_STATIC_DRAW)

            ibo_faces = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo_faces)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL_STATIC_DRAW)

            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(vertices.nbytes))
            glEnableVertexAttribArray(1)
            if len(var_data) != 0:
                glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0,
                                      ctypes.c_void_p(vertices.nbytes + normals.nbytes))
                glEnableVertexAttribArray(2)

            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            glBindVertexArray(0)
        except Exception as _e:
            import sys; print(f'[GL-WARN] add_mesh: {_e}', file=sys.stderr)
            return

        self.mesh_bundles[index] = {
            'mesh': mesh,
            'vao': vao,
            'vbo': vbo,
            'ibo_edges': ibo_edges,
            'ibo_faces': ibo_faces,
            'face_count': len(faces),
            'edge_count': len(edges),
        }

    def remove_mesh(self, index):
        """从渲染列表中移除一个网格。"""
        if index in self.mesh_bundles:
            del self.mesh_bundles[index]

    def rebuild_all_bundles(self, mesh_list):
        """清空所有网格资源并用新列表重建（用于 color_opt 切换时）。"""
        self.mesh_bundles.clear()
        for i, mesh in enumerate(mesh_list):
            self.add_mesh(i, mesh)

    # --- 共享初始化 ---

    def _compute_combined_center(self, all_vertices_list):
        """根据所有网格顶点计算合并包围盒中心。"""
        if not all_vertices_list:
            return np.array([0, 0, 0, 1])
        all_v = np.concatenate(all_vertices_list, axis=0)
        center_tem = np.max(all_v, axis=0) / 2 + np.min(all_v, axis=0) / 2
        return np.append(center_tem, 1).astype(np.float32)

    def _compute_init_size(self, all_vertices_list):
        """根据所有网格的联合包围盒计算初始缩放因子。"""
        if not all_vertices_list:
            return 1.0
        all_v = np.concatenate(all_vertices_list, axis=0)
        changeSize = abs(np.max(all_v, axis=0) - np.min(all_v, axis=0))
        changeSize = max(np.max(changeSize), 1e-6) * 1 / 8
        return 1.0 / changeSize

    def initialize_shared(self, mesh_list, rotation_matrix=None):
        """
        首次调用时初始化所有共享 GL 资源（着色器 / 投影矩阵 / 观察矩阵 / 光照），
        然后为每个网格创建各自的 VBO/IBO/VAO。
        后续切换 color_opt 时也可调用，mesh_list 中的网格会被重建。
        """
        if not mesh_list:
            return

        vertices_list = []
        for mesh in mesh_list:
            vertices_list.append(mesh.gl_points)
            if mesh.cell_type in ('tetrahedron', 'hexahedron'):
                vertices_list.append(mesh.surface_mesh.gl_points)

        self.change_size = self._compute_init_size(vertices_list)
        self.size = self.change_size

        tap_matrix = np.array([
            [self.change_size, 0, 0, 0],
            [0, self.change_size, 0, 0],
            [0, 0, self.change_size, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        if rotation_matrix is None or np.allclose(rotation_matrix, np.eye(4)):
            self.rotation_matrix = np.dot(np.eye(4), tap_matrix).astype(np.float32)
        else:
            self.rotation_matrix = rotation_matrix.astype(np.float32)

        self.center = self._compute_combined_center(vertices_list)

        glarea_width = self.glarea.get_allocated_width()
        glarea_height = self.glarea.get_allocated_height()
        fov = np.radians(45.0)
        aspect_ratio = glarea_width / glarea_height if glarea_height > 0 else 1.0
        near_plane = 0.5
        far_plane = 500
        self.projection_matrix = set_perspective_matrix(fov, aspect_ratio, near_plane, far_plane)

        camera_position = np.append(self.center[:2], self.center[2] - 16)
        target_position = self.center[:3]
        up_vector = np.array([0, 1, 0])
        self.view_matrix = set_view_matrix(camera_position, target_position, up_vector)

        # 将光源放在物体中心的上方-前方（视空间），产生立体感
        all_v = np.concatenate(vertices_list, axis=0)
        bbox_size = np.max(all_v, axis=0) - np.min(all_v, axis=0)
        obj_center = self.center[:3]

        # 主光源：物体右上方偏前
        light_world = obj_center + np.array([bbox_size[0] * 0.8,
                                              bbox_size[1] * 1.2,
                                              bbox_size[2] * 1.5], dtype=np.float32)
        light_view = (self.view_matrix @ np.append(light_world, 1.0))[:3]
        self.light_position_eye = light_view.astype(np.float32)

        # Gmsh 光源：物体左下方，产生特征性的明暗对比
        gmsh_light_world = obj_center + np.array([-bbox_size[0] * 0.6,
                                                   -bbox_size[1] * 1.0,
                                                    bbox_size[2] * 0.8], dtype=np.float32)
        gmsh_light_view = (self.view_matrix @ np.append(gmsh_light_world, 1.0))[:3]
        self.gmsh_light_position_eye = gmsh_light_view.astype(np.float32)

        gl = self.glarea.get_context()
        gl.make_current()

        try:
            if self.program is None:
                self.program = compileProgram(
                    compileShader(vertex_src, GL_VERTEX_SHADER),
                    compileShader(fragment_src, GL_FRAGMENT_SHADER)
                )

            # 缓存 uniform location
            self.faceColor_location = glGetUniformLocation(self.program, "faceColor")
            self.edgeColor_location = glGetUniformLocation(self.program, "edgeColor")
            self.pointColor_location = glGetUniformLocation(self.program, "pointColor")
            self.isEdge_location = glGetUniformLocation(self.program, "isEdge")
            self.isPoint_location = glGetUniformLocation(self.program, "isPoint")
            self.isGmsh_location = glGetUniformLocation(self.program, "isGmsh")
            self.isVar_location = glGetUniformLocation(self.program, "isVar")
            self.rotation_loc = glGetUniformLocation(self.program, "rotation")
            self.translation_loc = glGetUniformLocation(self.program, "translation")
            self.projection_loc = glGetUniformLocation(self.program, 'projection')
            self.view_loc = glGetUniformLocation(self.program, 'view')
            self.center_location = glGetUniformLocation(self.program, 'center')
            self.light_position_eye_location = glGetUniformLocation(self.program, 'light_position_eye')
            self.gmsh_light_position_eye_location = glGetUniformLocation(self.program, 'gmsh_light_position_eye')
            self.ambientStrengthLoc = glGetUniformLocation(self.program, 'ambientStrength')
            self.specularStrengthLoc = glGetUniformLocation(self.program, 'specularStrength')
            self.shininessLoc = glGetUniformLocation(self.program, 'shininess')
            self.lightColorLoc = glGetUniformLocation(self.program, 'lightColor')
        except Exception as _e:
            import sys; print(f'[GL-WARN] init_shared: {_e}', file=sys.stderr)
            return

        # 清空旧的 bundle 并重建（GL 已确认可用）
        self.mesh_bundles.clear()
        for i, mesh in enumerate(mesh_list):
            self.add_mesh(i, mesh)

    # --- 坐标轴 ---

    def _compute_axes_rotation(self):
        """从模型矩阵中提取纯旋转 + 固定缩放，使小坐标轴只跟随旋转，不同步缩放。"""
        R = self.rotation_matrix[:3, :3].copy()
        # 按列归一化去除缩放成分，保留纯旋转
        col_norms = np.linalg.norm(R, axis=0)
        col_norms = np.where(col_norms > 1e-10, col_norms, 1.0)
        R /= col_norms
        # 应用固定缩放（不受用户滚轮缩放影响）
        fixed_scale = 0.75
        R *= fixed_scale
        result = np.eye(4, dtype=np.float32)
        result[:3, :3] = R
        return result

    def init_axes(self):
        """创建坐标轴、箭头和字母标签的几何体与着色器（仅首次调用）。"""
        if hasattr(self, 'axes_program') and self.axes_program is not None:
            return  # 已经完全初始化过，避免每帧重复创建

        try:
            self.glarea.make_current()

            tip = 1.00          # 轴尖端位置
            head_len = 0.07     # 箭头锥体长度
            spread = 0.035      # 箭头锥体垂直扩散

            # ---- 轴线（3 条，每轴 2 个顶点）----
            axes_vertices = np.array([
                [0.0, 0.0, 0.0], [tip, 0.0, 0.0],   # X 轴
                [0.0, 0.0, 0.0], [0.0, tip, 0.0],   # Y 轴
                [0.0, 0.0, 0.0], [0.0, 0.0, tip],   # Z 轴
            ], dtype=np.float32)

            self.axes_vao = glGenVertexArrays(1)
            self.axes_vbo = glGenBuffers(1)
            glBindVertexArray(self.axes_vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.axes_vbo)
            glBufferData(GL_ARRAY_BUFFER, axes_vertices.nbytes, axes_vertices, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

            # ---- 箭头锥体（每轴 4 条短线，共 24 个顶点）----
            t, hl, sp = tip, head_len, spread

            arrow_x = np.array([
                [t, 0, 0], [t - hl,  sp, 0],
                [t, 0, 0], [t - hl, -sp, 0],
                [t, 0, 0], [t - hl, 0,  sp],
                [t, 0, 0], [t - hl, 0, -sp],
            ], dtype=np.float32)

            arrow_y = np.array([
                [0, t, 0], [ sp, t - hl, 0],
                [0, t, 0], [-sp, t - hl, 0],
                [0, t, 0], [0, t - hl,  sp],
                [0, t, 0], [0, t - hl, -sp],
            ], dtype=np.float32)

            arrow_z = np.array([
                [0, 0, t], [ sp, 0, t - hl],
                [0, 0, t], [-sp, 0, t - hl],
                [0, 0, t], [0,  sp, t - hl],
                [0, 0, t], [0, -sp, t - hl],
            ], dtype=np.float32)

            arrowhead_vertices = np.concatenate([arrow_x, arrow_y, arrow_z])

            self.arrowhead_vao = glGenVertexArrays(1)
            self.arrowhead_vbo = glGenBuffers(1)
            glBindVertexArray(self.arrowhead_vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.arrowhead_vbo)
            glBufferData(GL_ARRAY_BUFFER, arrowhead_vertices.nbytes, arrowhead_vertices, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

            # ---- 字母标签（简单的线段字形，全部在 XY 平面）----
            lo = tip + 0.20   # 字母中心离原点的距离
            ls = 0.055        # 字母半尺寸

            # X: 两条交叉对角线
            lx = lo
            letter_x = np.array([
                [lx - ls, -ls, 0.0], [lx + ls,  ls, 0.0],
                [lx + ls, -ls, 0.0], [lx - ls,  ls, 0.0],
            ], dtype=np.float32)

            # Y: V 形在上 + 竖线在下
            ly = lo
            letter_y = np.array([
                [-ls, ly + ls, 0.0], [0.0, ly, 0.0],   # 左上斜线
                [ ls, ly + ls, 0.0], [0.0, ly, 0.0],   # 右上斜线
                [0.0, ly, 0.0],      [0.0, ly - ls, 0.0],  # 竖线
            ], dtype=np.float32)

            # Z: 顶横线 + 对角线 + 底横线
            lz = lo
            letter_z = np.array([
                [-ls,  ls, lz], [ ls,  ls, lz],
                [ ls,  ls, lz], [-ls, -ls, lz],
                [-ls, -ls, lz], [ ls, -ls, lz],
            ], dtype=np.float32)

            letter_vertices = np.concatenate([letter_x, letter_y, letter_z])

            self.letter_vao = glGenVertexArrays(1)
            self.letter_vbo = glGenBuffers(1)
            glBindVertexArray(self.letter_vao)
            glBindBuffer(GL_ARRAY_BUFFER, self.letter_vbo)
            glBufferData(GL_ARRAY_BUFFER, letter_vertices.nbytes, letter_vertices, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindVertexArray(0)

            # ---- 编译着色器 ----
            self.axes_program = compileProgram(
                compileShader(axes_vertex_src, GL_VERTEX_SHADER),
                compileShader(axes_fragment_src, GL_FRAGMENT_SHADER)
            )
        except Exception as _e:
            import sys; print(f'[GL-WARN] init_axes: {_e}', file=sys.stderr)
            self.axes_program = None
            return

    def draw_small_axes(self):
        """绘制带箭头和 X/Y/Z 标签的小坐标轴（左下角）。"""
        if not hasattr(self, 'axes_program') or self.axes_program is None:
            return
        original_viewport = glGetIntegerv(GL_VIEWPORT)
        glViewport(5, 5, 165, 165)

        glUseProgram(self.axes_program)

        rot_loc = glGetUniformLocation(self.axes_program, "rotation")
        fixed_rot_loc = glGetUniformLocation(self.axes_program, "fixedRotation")
        color_loc = glGetUniformLocation(self.axes_program, "color")
        is_letter_loc = glGetUniformLocation(self.axes_program, "isLetter")

        axes_rotation = self._compute_axes_rotation()
        glUniformMatrix4fv(rot_loc, 1, GL_FALSE, axes_rotation)
        glUniformMatrix4fv(fixed_rot_loc, 1, GL_FALSE, np.eye(4, dtype=np.float32))

        red   = [1.0, 0.2, 0.2]
        green = [0.2, 1.0, 0.2]
        blue  = [0.2, 0.4, 1.0]

        # ---- 轴线 ----
        glBindVertexArray(self.axes_vao)
        glUniform1i(is_letter_loc, False)

        glUniform3fv(color_loc, 1, red)
        glDrawArrays(GL_LINES, 0, 2)
        glUniform3fv(color_loc, 1, green)
        glDrawArrays(GL_LINES, 2, 2)
        glUniform3fv(color_loc, 1, blue)
        glDrawArrays(GL_LINES, 4, 2)

        # ---- 箭头锥体（每轴 8 个顶点 = 4 条线）----
        glBindVertexArray(self.arrowhead_vao)
        glUniform1i(is_letter_loc, False)
        glLineWidth(2.5)

        glUniform3fv(color_loc, 1, red)
        glDrawArrays(GL_LINES, 0, 8)
        glUniform3fv(color_loc, 1, green)
        glDrawArrays(GL_LINES, 8, 8)
        glUniform3fv(color_loc, 1, blue)
        glDrawArrays(GL_LINES, 16, 8)

        # ---- 字母标签（跟随模型旋转）----
        glBindVertexArray(self.letter_vao)
        glUniform1i(is_letter_loc, False)
        glLineWidth(2.5)

        glUniform3fv(color_loc, 1, red)
        glDrawArrays(GL_LINES, 0, 4)      # X 字母 (2 条线)
        glUniform3fv(color_loc, 1, green)
        glDrawArrays(GL_LINES, 4, 6)      # Y 字母 (3 条线)
        glUniform3fv(color_loc, 1, blue)
        glDrawArrays(GL_LINES, 10, 6)     # Z 字母 (3 条线)

        glLineWidth(1.0)
        glBindVertexArray(0)
        glUseProgram(0)
        glViewport(*original_viewport)

    # --- 背景 ---

    def set_background_color(self, red, green, blue, alpha):
        glClearColor(red, green, blue, alpha)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # --- 旋转 / 平移 ---

    def update_rotation_matrix(self):
        self.angle_y = -self.angle_y
        cos_x = np.cos(self.angle_x)
        sin_x = np.sin(self.angle_x)
        cos_y = np.cos(self.angle_y)
        sin_y = np.sin(self.angle_y)

        rotation_x = np.array([
            [1, 0, 0, 0],
            [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        rotation_y = np.array([
            [cos_y, 0, sin_y, 0],
            [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.rotation_matrix = np.dot(self.rotation_matrix, np.dot(rotation_y, rotation_x))

    def update_translation_matrix(self):
        self.translation_matrix = np.array([
            [1, 0, 0, self.translate_x],
            [0, 1, 0, self.translate_y],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

    # --- 渲染入口 ---

    def on_render(self, area, contex):
        self.init_axes()
        self.set_background_color(self.back_red, self.back_green, self.back_blue, self.back_alpha)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glDepthFunc(GL_LESS)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)

        glUseProgram(self.program)

        glUniform4fv(self.center_location, 1, self.center)
        glUniformMatrix4fv(self.rotation_loc, 1, GL_FALSE, self.rotation_matrix)
        glUniformMatrix4fv(self.translation_loc, 1, GL_TRUE, self.translation_matrix)
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, self.projection_matrix)
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.view_matrix)
        glUniform3fv(self.light_position_eye_location, 1, self.light_position_eye)
        glUniform3fv(self.gmsh_light_position_eye_location, 1, self.gmsh_light_position_eye)
        glUniform1f(self.ambientStrengthLoc, self.ambient_strength)
        glUniform1f(self.specularStrengthLoc, self.specular_strength)
        glUniform1f(self.shininessLoc, self.shininess)
        glUniform3fv(self.lightColorLoc, 1, self.light_color)

        for bundle in self.mesh_bundles.values():
            glBindVertexArray(bundle['vao'])

            if self.face_draw:
                glUniform4fv(self.faceColor_location, 1, self.face_color)
                glUniform1i(self.isEdge_location, False)
                glUniform1i(self.isGmsh_location, False)
                glUniform1i(self.isPoint_location, False)
                glUniform1i(self.isVar_location, False)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bundle['ibo_faces'])
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glDrawElements(GL_TRIANGLES, bundle['face_count'], GL_UNSIGNED_INT, None)

            if self.edge_draw:
                glUniform4fv(self.edgeColor_location, 1, self.edge_color)
                glUniform1i(self.isGmsh_location, False)
                glUniform1i(self.isEdge_location, True)
                glUniform1i(self.isPoint_location, False)
                glUniform1i(self.isVar_location, False)
                glLineWidth(1.0)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bundle['ibo_edges'])
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                glDrawElements(GL_LINES, bundle['edge_count'], GL_UNSIGNED_INT, None)

            if self.points_draw:
                glUniform4fv(self.pointColor_location, 1, self.point_color)
                glUniform1i(self.isGmsh_location, False)
                glUniform1i(self.isPoint_location, True)
                glUniform1i(self.isEdge_location, False)
                glUniform1i(self.isVar_location, False)
                glPointSize(2.0)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bundle['ibo_edges'])
                glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
                glDrawElements(GL_POINTS, bundle['edge_count'], GL_UNSIGNED_INT, None)

            if self.gmsh_draw:
                glUniform1i(self.isGmsh_location, True)
                glUniform1i(self.isPoint_location, False)
                glUniform1i(self.isEdge_location, False)
                glUniform1i(self.isVar_location, False)
                glLineWidth(1.0)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bundle['ibo_edges'])
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                glDrawElements(GL_LINES, bundle['edge_count'], GL_UNSIGNED_INT, None)

            if self.var_draw:
                glUniform1i(self.isEdge_location, False)
                glUniform1i(self.isGmsh_location, False)
                glUniform1i(self.isPoint_location, False)
                glUniform1i(self.isVar_location, True)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bundle['ibo_faces'])
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glDrawElements(GL_TRIANGLES, bundle['face_count'], GL_UNSIGNED_INT, None)

            glBindVertexArray(0)

        if self.is_show_smallAxes:
            self.draw_small_axes()

        return True

    def on_render_background(self, area, contex):
        self.set_background_color(self.back_red, self.back_green, self.back_blue, self.back_alpha)
        self.init_axes()
        if self.is_show_smallAxes:
            self.draw_small_axes()

    # --- 鼠标操作 ---

    def on_button_press(self, area, event):
        self.click_x = event.x
        self.click_y = event.y

    def on_mouse_move(self, area, event):
        if event.state & Gdk.ModifierType.BUTTON3_MASK:
            dx = event.x - self.click_x
            dy = event.y - self.click_y
            self.translate_x += dx * self.translation_sensitivity
            self.translate_y += dy * self.translation_sensitivity
            self.update_translation_matrix()
            self.click_x = event.x
            self.click_y = event.y

        elif event.state & Gdk.ModifierType.BUTTON1_MASK:
            dx = event.x - self.click_x
            dy = event.y - self.click_y
            self.angle_x = dy * np.pi / 180 * self.rotation_sensitivity
            self.angle_y = dx * np.pi / 180 * self.rotation_sensitivity
            self.update_rotation_matrix()
            self.click_x = event.x
            self.click_y = event.y

        area.queue_draw()

    def on_scroll(self, area, event):
        if event.direction == Gdk.ScrollDirection.UP:
            self.scale = 1.0 + self.zoom_sensitivity
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.scale = 1.0 - self.zoom_sensitivity

        s = self.scale
        self.size *= s

        scale_matrix = np.array([
            [s, 0, 0, 0],
            [0, s, 0, 0],
            [0, 0, s, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        self.rotation_matrix = np.dot(self.rotation_matrix, scale_matrix).astype(np.float32)

        self.gmsh_light_position_eye = np.append(self.gmsh_light_position_eye[:2],
                                                 self.gmsh_light_position_eye[2] * s * s)

        area.queue_draw()
