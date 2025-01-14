import numpy as np
import gi
from gi.repository import GLib
import threading
gi.require_version('Gtk', '3.0')
import time

from Utils.Connector.OutputTracker import OutputTracker

class ConnectorWithViewBox:

    def __init__(self, solver, showbox, should_draw, timer, box1):

        # 加载求解器
        self.solver = solver

        # 加载绘制窗口
        self.showbox = showbox

        # 网格绘制编号
        self.should_draw = should_draw

        # 计时器
        self.timer = timer

        # box1
        self.box1 = box1

        # 内容捕捉器
        self.tracker = OutputTracker()

        # 开始时间
        self.start_time = time.time()

        # 加载绘制网格
        self.meshClass = self.solver.meshClass

        self.old_point_var = self.solver.point_var

        self.old_projection_matrix = None


    # 检查是否更新以及绘制
    def check_for_changes_and_draw(self, all_time):

        current_time = time.time()
        elapsed_time = (current_time - self.start_time)

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

        rtol = 1e-08
        atol = 1e-08

        if not (np.allclose(self.old_point_var, self.solver.point_var, rtol=rtol, atol=atol)):

            # 设置网格不断更新渲染
            tem_var = np.array([[0, 0, value] for value in self.solver.point_var]).astype(np.float32)
            self.meshClass.var = tem_var

            self.showbox.on_realize(self.meshClass, self.old_projection_matrix)
            self.showbox.should_draw = self.should_draw
            self.showbox.glarea.queue_draw()

            self.old_point_var = self.solver.point_var.copy()

        self.old_projection_matrix = self.showbox.projection_matrix

        return True


    # 求解
    def Solve(self, g):

        # g = lambda x: 1 / np.sqrt(x[:, 0] ** 2 + x[:, 1] ** 2 + x[:, 2] ** 2)    # 外问题的边值条件
        # g = lambda x: 1 / np.sqrt((x[:, 0] - 1) ** 2 + (x[:, 1] - 1) ** 2 + (x[:, 2] - 1) ** 2)  # 内问题的边值条件
        self.solver.ComputeSingularIntegral()
        self.solver.computeRHS(g)
        self.solver.solve()


    # 实时更新检测
    def DetectorWithRealTime(self, freq, all_time, g):

        def execute_code():
            self.Solve(g)

        thread = threading.Thread(target=execute_code)
        thread.start()

        freq *= 1000  # 单位转换 s -> ms
        GLib.timeout_add(freq, self.check_for_changes_and_draw, all_time)


