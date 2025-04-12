import numpy as np
import gi
from gi.repository import GLib
import threading
gi.require_version('Gtk', '3.0')
import time

from Utils.Connector.OutputTracker import OutputTracker

class SolverViewBoxConn:

    def __init__(self):

        # (稍后加载)
        self.docking_solver = None
        self.showbox = None
        self.timer = None
        self.box1 = None
        self.freq = None
        self.all_time = None
        self.meshClass = None
        self.old_value = None


        # 内容捕捉器
        self.tracker = OutputTracker()

        # 渲染单元选择
        self.data_location_list = ['vertex', 'cell']

        # 记录旋转矩阵
        self.old_rotation_matrix = None

        # 渲染次数
        self.render_step = 0
        # 变量名字
        self.var_names = None
        # 变量个数
        self.var_num = 0
        # 渲染位置
        self.render_loc = None

        # point_var_list
        self.point_var_list = []


    # 加载配件
    def load_fit(self, showbox, mesh, timer, box1, freq, all_time):

        self.showbox = showbox  # 加载绘制窗口
        self.meshClass = mesh  # 加载绘制网格 (该网格不一定等于showbox当前网格)
        self.timer = timer  # 计时器
        self.box1 = box1  # box1
        self.freq = freq   # 频率
        self.all_time = all_time  # 总时间


    # 加载求解器
    def load_solver(self, docking_solver):

        self.docking_solver = docking_solver

        # 加载相关变量
        self.render_loc = self.docking_solver.data_location
        self.var_names = self.docking_solver.var
        self.var_num = len(self.var_names)

        if self.render_loc == self.data_location_list[0]:  # 点数据
            mesh_cell_len = len(self.meshClass.vertexs)
        elif self.render_loc == self.data_location_list[1]:  # 面数据
            mesh_cell_len = len(self.meshClass.cells)
        else:
            raise ValueError('error, data_location must be vertex, cell')

        self.old_value = np.zeros(self.var_num * mesh_cell_len)


    def load_var(self):

        """
        self.docking_solver.point_var: ndarray 1 or 2 dimension
        self.varnames: list
        e.g. var=[1, 1, 1, 2, ...], varname=['rho']
             var=[[1, 1, ..], [2, 2, ...], ...], varname=['rho', 'v', ...]
        """

        render_data = self.docking_solver.solver.getRenderingData()  # 待渲染数据

        # 将待渲染数据转化为点值
        if self.render_loc == self.data_location_list[0]:  # 点数据
            point_var = render_data.reshape((self.var_num, -1))
        elif self.render_loc == self.data_location_list[1]:  # 面数据
            cell_var = render_data.reshape((self.var_num, -1))
            point_var = self.cell_to_vertex_values(cell_var)
        else:
            raise ValueError('error, data_location must be vertex, cell')

        # 构造变量字典
        tem_var = {name: point_var if point_var.ndim == 1 else value for name, value in zip(self.var_names, point_var)}

        if self.meshClass.cell_type == 'triangle' or self.meshClass.cell_type == 'quadrilateral':
            self.meshClass.gl_var = {k: np.column_stack((np.zeros(len(v)), np.zeros(len(v)), v)) for k, v in
                                     tem_var.items()}
        else:
            self.meshClass.surface_mesh.gl_var = {k: np.column_stack((np.zeros(len(v)), np.zeros(len(v)), v)) for k, v
                                                  in tem_var.items()}


    def cell_to_vertex_values(self, cellsData):
        def _process_single(data1D):
            vertex_num = len(self.meshClass.vertexs)  # 顶点数量
            VN = np.zeros(vertex_num, dtype=np.float32)
            faces = np.array(self.meshClass.cells).reshape(-1, 3)

            for i in range(vertex_num):
                num = 0
                faces_using = np.where(faces == i)[0]

                for j in faces_using:
                    VN[i] += data1D[j]
                    num += 1

                if num > 0:
                    VN[i] = VN[i] / num
                else:
                    VN[i] = 0
                    print(f"Warning: Node {i} has no associated elements.")

            return VN

        # 判断输入维度
        cellsData = np.array(cellsData)
        if cellsData.ndim == 1 or (cellsData.ndim == 2 and cellsData.shape[0] == 1):
            # 处理一维数据或 shape[0] == 1 的二维数据
            return _process_single(cellsData.flatten())
        elif cellsData.ndim == 2:
            # 处理多行二维数据
            return np.array([_process_single(row) for row in cellsData])
        else:
            raise ValueError("cellsData must be either 1D or 2D (with shape[0] >= 1)")


    # 检查是否更新以及绘制
    def check_for_changes_and_draw(self, all_time, start_time):

        current_time = time.time()
        elapsed_time = (current_time - start_time)

        # 设置计时器计时
        self.timer.set_text(str(round(elapsed_time, 2)) + 's/' + str(all_time) + 's')

        if elapsed_time >= all_time:
            self.timer.set_text(str(all_time) + 's/' + str(all_time) + 's')
            self.box1.info_print('time over!\n\n')

            return False

        # 将命令行的输出内容捕捉并在information上打印 (如果有)
        self.tracker.start_tracking()
        content = self.tracker.get_new_output()
        if content:
            self.box1.info_print(str(content))

        self.old_rotation_matrix = self.showbox.glareaClass.rotation_matrix.copy()

        now_value = self.docking_solver.solver.getRenderingData()  # 更新渲染值

        if not (np.allclose(self.old_value, now_value, rtol=1e-08, atol=1e-08)):

            self.render_step += 1
            self.load_var()  # 加载变量的值

            self.showbox.on_realize(mesh=self.meshClass, rotation_matrix=self.old_rotation_matrix)
            self.showbox.queue_draw()
            self.old_value = now_value.copy()  # 更新前一步值
            # 记录每一步的值
            self.point_var_list.append(self.old_value)

        return True


    # 实时更新检测
    def detectorWithRealTime(self, *args, **kwargs):

        def execute_solve():

            self.docking_solver.Solve(*args, **kwargs)

        thread = threading.Thread(target=execute_solve)
        thread.start()

        self.freq *= 1000  # 单位转换 s -> ms
        start_time = time.time()
        GLib.timeout_add(self.freq, self.check_for_changes_and_draw, self.all_time, start_time)
