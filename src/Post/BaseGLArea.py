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

        #

        # 待绘制的边面信息
        self.vertices = []
        self.faces = []
        self.edges = []
        self.faces_normal = []
        self.normal = []
        self.var = []
        self.var_opt = 'Neutral Mode'
        self.face_shape = None

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

        # 中心点 (4阶向量)
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
        self.center_location = 0
        self.isEdge_location = 0
        self.isPoint_location = 0
        self.isGmsh_location = 0
        self.rotation_loc = 0
        self.translation_loc = 0
        self.projection_loc = 0
        self.view_loc = 0
        self.lightDirLocation = 0

        # 光照位置
        self.light_position_eye = np.array([0, 0, 0], dtype=np.float32)
        self.gmsh_light_position_eye = np.array([0, 0, 0], dtype=np.float32)
        # 缓冲区
        self.vao = None  # 顶点数组对象
        self.vbo = None  # 顶点缓冲对象
        self.ibo1 = None  # 边索引缓冲对象
        self.ibo2 = None  # 面索引缓冲对象

        self.axes_vao = None  # 小坐标轴的顶点数组对象
        self.axes_vbo = None  # 小坐标轴的顶点缓冲对象

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


    def init_axes(self):
        self.glarea.make_current()

        # 小坐标轴的顶点数据，表示X, Y, Z轴的方向和箭头
        axes_vertices = np.array([
            [0.0, 0.0, 0.0], [0.8, 0.0, 0.0],  # X轴
            [0.0, 0.0, 0.0], [0.0, 0.8, 0.0],  # Y轴
            [0.0, 0.0, 0.0], [0.0, 0.0, 0.8],  # Z轴

            # # X轴箭头
            # [1.1, 0.0, 0.0], [0.9, 0.1, 0.0],  # X轴箭头
            # [1.1, 0.0, 0.0], [0.9, -0.1, 0.0],  # X轴箭头
            #
            # # Y轴箭头
            # [0.0, 1.1, 0.0], [0.1, 0.9, 0.0],  # Y轴箭头
            # [0.0, 1.1, 0.0], [-0.1, 0.9, 0.0],  # Y轴箭头
            #
            # # Z轴箭头
            # [0.0, 0.0, 1.1], [0.0, 0.9, 0.1],  # Z轴箭头
            # [0.0, 0.0, 1.1], [0.0, 0.9, -0.1],  # Z轴箭头
            #
            # # X字母
            # [1.05, -0.35, 0.0], [1.75, 0.35, 0.0],  # X 的对角线
            # [1.05, 0.35, 0.0], [1.75, -0.35, 0.0],  # X 的另一对角线
            #
            # # Y字母
            # [0.0, 1.05, 0.0], [0.0, 1.75, 0.0],  # Y 的竖线
            # [-0.35, 1.05, 0.0], [0.0, 1.45, 0.0],  # Y 的左侧线
            # [0.35, 1.05, 0.0], [0.0, 1.45, 0.0],  # Y 的右侧线
            #
            # # Z字母
            # [0.0, 0.0, 1.05], [0.0, 0.0, 1.75],  # Z 的上横线
            # [0.0, 0.0, 1.75], [0.7, 0.0, 1.05],  # Z 的斜线
            # [0.7, 0.0, 1.05], [0.7, 0.0, 1.0]  # Z 的下横线
        ], dtype=np.float32)

        # 创建VAO和VBO
        self.axes_vao = glGenVertexArrays(1)
        self.axes_vbo = glGenBuffers(1)
        glBindVertexArray(self.axes_vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.axes_vbo)
        glBufferData(GL_ARRAY_BUFFER, axes_vertices.nbytes, axes_vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # 编译小坐标轴的着色器
        self.axes_program = compileProgram(
            compileShader(axes_vertex_src, GL_VERTEX_SHADER),
            compileShader(axes_fragment_src, GL_FRAGMENT_SHADER)
        )

    def draw_small_axes(self):
        # 保存当前视口
        original_viewport = glGetIntegerv(GL_VIEWPORT)

        # 设置新的视口，用于绘制小坐标轴，调整视口的大小
        glViewport(10, 10, 100, 100)  # 调整视口大小为更大的范围

        # 使用小坐标轴的着色器程序
        glUseProgram(self.axes_program)

        # 传递旋转矩阵，用于坐标轴旋转
        glUniformMatrix4fv(glGetUniformLocation(self.axes_program, "rotation"), 1, GL_FALSE, self.rotation_matrix)

        # 传递固定方向的旋转矩阵，用于字母保持正面
        fixed_rotation_matrix = np.eye(4, dtype=np.float32)  # 单位矩阵，不旋转
        glUniformMatrix4fv(glGetUniformLocation(self.axes_program, "fixedRotation"), 1, GL_FALSE, fixed_rotation_matrix)

        glBindVertexArray(self.axes_vao)

        glUniform1i(glGetUniformLocation(self.axes_program, "isLetter"), False)  # 标识非字母

        # 绘制X轴及其箭头
        glUniform3fv(glGetUniformLocation(self.axes_program, "color"), 1, [1.0, 0.0, 0.0])  # 红色
        glDrawArrays(GL_LINES, 0, 2)  # X轴

        # 绘制Y轴及其箭头
        glUniform3fv(glGetUniformLocation(self.axes_program, "color"), 1, [1.0, 1.0, 0.0])  # 黄色
        glDrawArrays(GL_LINES, 2, 2)  # Y轴

        # 绘制Z轴及其箭头
        glUniform3fv(glGetUniformLocation(self.axes_program, "color"), 1, [0.0, 1.0, 0.0])  # 绿色
        glDrawArrays(GL_LINES, 4, 2)  # Z轴

        # 绘制字母X
        glUniform3fv(glGetUniformLocation(self.axes_program, "color"), 1, [1.0, 1.0, 1.0])  # 白色
        glUniform1i(glGetUniformLocation(self.axes_program, "isLetter"), True)  # 标识字母
        glDrawArrays(GL_LINES, 6, 4)  # X箭头

        # 绘制字母Y
        glDrawArrays(GL_LINES, 10, 4)  # Y 字母

        # 绘制字母Z
        glDrawArrays(GL_LINES, 14, 4)  # Z 字母


        glBindVertexArray(0)
        glUseProgram(0)

        # 恢复原来的视口
        glViewport(*original_viewport)

    # 设置背景颜色
    def set_background_color(self, red, green, blue, alpha):

        glClearColor(red, green, blue, alpha)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # 更新旋转矩阵
    def update_rotation_matrix(self):
        self.angle_y = -self.angle_y  # 在函数首部添加这行代码来反转 Y 轴旋转方向
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

    # 更新平移矩阵，用于鼠标控制平移
    def update_translation_matrix(self):
        # 直接设置平移矩阵，而不是累积乘法
        self.translation_matrix = np.array([
            [1, 0, 0, self.translate_x],
            [0, 1, 0, self.translate_y],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)


    # 加载网格
    def load_mesh(self, mesh):

        """ 获取边面信息 """
        self.mesh = mesh
        self.vertices = mesh.gl_points
        self.edges = mesh.gl_edges
        self.faces = mesh.gl_cells
        self.normal = mesh.gl_normal


    # 网格显示的初始化
    def on_realize(self, rotation_matrix=None, draw_step=-1, color_opt='Neutral Mode'):  # object 可能是box1 也可能是网格类


        self.var_opt = color_opt  # 当为 Neutral Mode时, 相等于没有var
        self.var = np.array([]) if self.var_opt == "Neutral Mode" else np.array(self.mesh.gl_var[self.var_opt], dtype=np.float32)

        if len(self.var) != 0:
            # 取出var的最后一列
            self.var_last = self.var[:, -1].reshape(-1, 1)
            # 对var的最后一列归一化
            self.var_last = (self.var_last - np.min(self.var_last)) / (np.max(self.var_last) - np.min(self.var_last))
            # 再将var的最后一列替换掉
            self.var[:, -1] = self.var_last.reshape(-1)

        """ 更新初始网格大小 """

        # 初始化旋转矩阵
        self.rotation_matrix = np.eye(4, dtype=np.float32)

        # 计算放大/缩小尺寸
        changeSize = abs(np.max(self.vertices, axis=0) - np.min(self.vertices, axis=0))
        changeSize = np.max(changeSize, axis=0) * 1 / 8
        self.change_size = 1 / changeSize

        # 更新Size
        self.size = self.change_size

        tap_matrix = np.array([
            [self.change_size, 0, 0, 0],
            [0, self.change_size, 0, 0],
            [0, 0, self.change_size, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        if draw_step == -1:
            self.rotation_matrix = np.dot(self.rotation_matrix, tap_matrix).astype(np.float32)
        else:
            self.rotation_matrix = rotation_matrix.astype(np.float32)


        """ 更新透视投影矩阵 """

        # 获取glarea的宽度和高度
        glarea_width = self.glarea.get_allocated_width()
        glarea_height = self.glarea.get_allocated_height()

        # 计算透视投影矩阵
        fov = np.radians(45.0)  # 视野角度
        aspect_ratio = glarea_width / glarea_height  # 宽高比
        near_plane = 0.5  # 近平面距离
        far_plane = 500  # 远平面距离
        self.projection_matrix = set_perspective_matrix(fov, aspect_ratio, near_plane, far_plane)

        """"更新观察矩阵"""

        # 计算中心点
        center_tem = np.max(self.vertices, axis=0) / 2 + np.min(self.vertices, axis=0) / 2
        self.center = np.append(center_tem, 1)

        # 计算观察矩阵
        camera_position = np.append(self.center[:2], self.center[2] - 16)  # 相机位置
        target_position = self.center[:3]  # 相机的注视点位置
        up_vector = np.array([0, 1, 0])  # 相机的 "up" 向量
        self.view_matrix = set_view_matrix(camera_position, target_position, up_vector)

        self.light_position_eye = np.append(self.center[:2], self.center[3])
        distance = np.max(self.vertices, axis=0) - np.min(self.vertices, axis=0)
        initial_array = np.array([(np.min(self.vertices, axis=0) - distance * 0.3)[0],
                                  (np.min(self.vertices, axis=0) - distance * 0.55)[1]])

        self.gmsh_light_position_eye = np.append(initial_array,
                                                 (np.max(self.vertices, axis=0)[2] + distance[2] * 2))

        """openGL的预处理"""

        # 获取openGL渲染区域的上下文, 以便接下来执行openGL操作
        gl = self.glarea.get_context()
        gl.make_current()

        # 编译着色器
        self.program = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        # 顶点(包含法向量)缓冲对象  1 作为参数传递给 glGenBuffers，表示只生成一个缓冲对象
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        if len(self.var) == 0:
            # 计算顶点数据和法向量数据总字节数
            total_bytes = self.vertices.nbytes + self.normal.nbytes  # 假设 self.normals 是法向量数据
            # 创建一个包含顶点数据和法向量数据的大缓冲区
            con_data = np.concatenate((self.vertices, self.normal))
        else:

            total_bytes = self.vertices.nbytes + self.normal.nbytes + self.var.nbytes
            con_data = np.concatenate((self.vertices, self.normal, self.var))

        glBufferData(GL_ARRAY_BUFFER, total_bytes, con_data, GL_STATIC_DRAW)

        # 边索引缓冲对象
        self.ibo1 = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo1)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.edges.nbytes, self.edges, GL_STATIC_DRAW)

        # 面索引缓冲对象
        self.ibo2 = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo2)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.faces.nbytes, self.faces, GL_STATIC_DRAW)

        # # 小坐标轴索引缓冲对象
        # self.ibo3 = glGenBuffers(1)
        # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo3)

        """
        这四行代码是在使用 OpenGL 进行顶点数据处理和设置顶点属性时的典型用法，
        用于创建顶点数组对象（VAO）、绑定 VAO、设置顶点属性指针和启用顶点属性。
        """
        # VAO 是一种保存了配置顶点数据格式和绑定缓冲对象状态的对象
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # 设置顶点位置属性指针
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))  # 顶点坐标是 3 个浮点数
        glEnableVertexAttribArray(0)

        # 设置法向量数据的属性指针
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(self.vertices.nbytes))  # 法向量是 3 个浮点数
        glEnableVertexAttribArray(1)

        # 设置变量数据的属性指针
        if len(self.var) != 0:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0,
                                  ctypes.c_void_p(self.vertices.nbytes + self.normal.nbytes))
            glEnableVertexAttribArray(2)

        # 解除绑定 vbo ibo
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # 获取Uniform变量的位置 (数字索引)
        self.faceColor_location = glGetUniformLocation(self.program, "faceColor")  # 面颜色
        self.edgeColor_location = glGetUniformLocation(self.program, "edgeColor")  # 边颜色
        self.pointColor_location = glGetUniformLocation(self.program, "pointColor")  # 点颜色
        self.isEdge_location = glGetUniformLocation(self.program, "isEdge")  # 是否绘制边
        self.isPoint_location = glGetUniformLocation(self.program, "isPoint")  # 是否绘制点
        self.isGmsh_location = glGetUniformLocation(self.program, "isGmsh")  # 是否绘制gmsh
        self.isVar_location = glGetUniformLocation(self.program, "isVar")  # 是否绘制变量
        self.rotation_loc = glGetUniformLocation(self.program, "rotation")  # 旋转矩阵
        self.translation_loc = glGetUniformLocation(self.program, "translation")  # 平移矩阵
        self.projection_loc = glGetUniformLocation(self.program, 'projection')  # 透视投影矩阵
        self.view_loc = glGetUniformLocation(self.program, 'view')  # 观察矩阵
        self.center_location = glGetUniformLocation(self.program, 'center')  # 中心点
        self.light_position_eye_location = glGetUniformLocation(self.program, 'light_position_eye')
        self.gmsh_light_position_eye_location = glGetUniformLocation(self.program, 'gmsh_light_position_eye')


    # 持续渲染
    def on_render(self, area, contex):
        self.init_axes()

        # 设置背景色
        self.set_background_color(self.back_red, self.back_green, self.back_blue, self.back_alpha)

        glEnable(GL_DEPTH_TEST)  # 深度测试
        glEnable(GL_PROGRAM_POINT_SIZE)  # 开启点的大小
        glBindVertexArray(self.vao)

        # glEnable(GL_BLEND)  # 开启混合

        glDepthFunc(GL_LESS)
        glEnable(GL_LINE_SMOOTH)  # 开启线平滑

        """解决面渲染深度冲突而导致线渲染出现问题"""
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)  # 参数可以调整

        """ 将变量传至着色器程序 """

        # 设置活动的着色器程序
        glUseProgram(self.program)

        glUniform4fv(self.center_location, 1, self.center)
        glUniformMatrix4fv(self.rotation_loc, 1, GL_FALSE, self.rotation_matrix)
        glUniformMatrix4fv(self.translation_loc, 1, GL_TRUE, self.translation_matrix)
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, self.projection_matrix)
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.view_matrix)
        glUniform3fv(self.light_position_eye_location, 1, self.light_position_eye)
        glUniform3fv(self.gmsh_light_position_eye_location, 1, self.gmsh_light_position_eye)

        if self.face_draw:  # 绘制物体的面

            """ 将变量传至着色器 """
            glUniform4fv(self.faceColor_location, 1, self.face_color)
            glUniform1i(self.isEdge_location, False)
            glUniform1i(self.isGmsh_location, False)
            glUniform1i(self.isPoint_location, False)
            glUniform1i(self.isVar_location, False)

            """ 启用面的IBO对象 """
            # 将索引缓冲区对象绑定到GL_ELEMENT_ARRAY_BUFFER目标上
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo2)

            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            glDrawElements(GL_TRIANGLES, len(self.faces), GL_UNSIGNED_INT, None)

        if self.edge_draw:  # 绘制物体的边

            """ 将变量传至着色器 """
            glUniform4fv(self.edgeColor_location, 1, self.edge_color)
            glUniform1i(self.isGmsh_location, False)
            glUniform1i(self.isEdge_location, True)
            glUniform1i(self.isPoint_location, False)
            glUniform1i(self.isVar_location, False)

            glLineWidth(1.0)

            """ 启用边的IBO对象 """
            # 将索引缓冲区对象绑定到GL_ELEMENT_ARRAY_BUFFER目标上
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo1)

            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glDrawElements(GL_LINES, len(self.edges), GL_UNSIGNED_INT, None)

        if self.points_draw:  # 绘制物体的点

            """ 将变量传至着色器 """
            glUniform4fv(self.pointColor_location, 1, self.point_color)
            glUniform1i(self.isGmsh_location, False)
            glUniform1i(self.isPoint_location, True)
            glUniform1i(self.isEdge_location, False)
            glUniform1i(self.isVar_location, False)

            glPointSize(2.0)

            """ 启用边的IBO对象 """
            # 将索引缓冲区对象绑定到GL_ELEMENT_ARRAY_BUFFER目标上
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo1)

            glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
            glDrawElements(GL_POINTS, len(self.edges), GL_UNSIGNED_INT, None)

        if self.gmsh_draw:  # 绘制物体的gmsh
            """ 将变量传至着色器 """
            glUniform1i(self.isGmsh_location, True)
            glUniform1i(self.isPoint_location, False)
            glUniform1i(self.isEdge_location, False)
            glUniform1i(self.isVar_location, False)

            glLineWidth(1.0)

            """ 启用边的IBO对象 """
            # 将索引缓冲区对象绑定到GL_ELEMENT_ARRAY_BUFFER目标上
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo1)

            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glDrawElements(GL_LINES, len(self.edges), GL_UNSIGNED_INT, None)

        if self.var_draw:  # 绘制物体的变量
            """ 将变量传至着色器 """
            glUniform1i(self.isEdge_location, False)
            glUniform1i(self.isGmsh_location, False)
            glUniform1i(self.isPoint_location, False)
            glUniform1i(self.isVar_location, True)

            # """ 启用面的IBO对象 """
            # # 将索引缓冲区对象绑定到GL_ELEMENT_ARRAY_BUFFER目标上
            # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo1)
            #
            # glPolygonMode(GL_FRONT_AND_BACK, GL_POINT)
            # glDrawElements(GL_POINTS, len(self.edges), GL_UNSIGNED_INT, None)

            """ 启用面的IBO对象 """
            # 将索引缓冲区对象绑定到GL_ELEMENT_ARRAY_BUFFER目标上
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo2)

            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            glDrawElements(GL_TRIANGLES, len(self.faces), GL_UNSIGNED_INT, None)

        if self.is_show_smallAxes:
            self.draw_small_axes()

        return True

    def on_render_background(self, area, contex):

        # 只渲染背景颜色
        self.set_background_color(self.back_red, self.back_green, self.back_blue, self.back_alpha)

        self.init_axes()

        if self.is_show_smallAxes:
            self.draw_small_axes()


    '''鼠标操作'''

    # 鼠标按压操作
    def on_button_press(self, area, event):
        self.click_x = event.x
        self.click_y = event.y

    # 鼠标控制旋转和平移
    def on_mouse_move(self, area, event):
        if event.state & Gdk.ModifierType.BUTTON3_MASK:
            # 如果按下右键，进行平移操作
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

    # 滑轮控制缩放
    def on_scroll(self, area, event):

        # 向上滚动放大，向下滚动缩小
        if event.direction == Gdk.ScrollDirection.UP:
            self.scale = 1.0 + self.zoom_sensitivity
        elif event.direction == Gdk.ScrollDirection.DOWN:
            self.scale = 1.0 - self.zoom_sensitivity

        # 更新缩放因子
        s = self.scale

        # 更新size
        self.size *= s

        # 创建一个缩放矩阵
        scale_matrix = np.array([
            [s, 0, 0, 0],
            [0, s, 0, 0],
            [0, 0, s, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        self.rotation_matrix = np.dot(self.rotation_matrix, scale_matrix).astype(np.float32)

        # 更新光源位置,随着缩放因子的变化，光源位置也要相应的变化
        self.gmsh_light_position_eye = np.append(self.gmsh_light_position_eye[:2],
                                                 self.gmsh_light_position_eye[2] * s * s)

        # 更新渲染
        area.queue_draw()


