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
        self.solver = None
        self.showbox = None
        self.should_draw = None
        self.timer = None
        self.box1 = None
        self.freq = None
        self.all_time = None
        self.meshClass = None
        self.old_point_var = None


        # 内容捕捉器
        self.tracker = OutputTracker()

        self.old_rotation_matrix = None

        # 渲染次数
        self.draw_step=0



    # 加载配件
    def load_fit(self, showbox, should_draw, timer, box1, freq, all_time):

        self.showbox = showbox # 加载绘制窗口
        self.should_draw = should_draw  # 网格绘制编号
        self.timer = timer # 计时器
        self.box1 = box1  # box1
        self.freq = freq   # 频率
        self.all_time = all_time  # 总时间


    # 加载求解器
    def load_solver(self, solver):

        self.solver = solver
        # 加载绘制网格
        self.meshClass = self.solver.meshClass
        # 加载点值
        self.old_point_var = self.solver.point_var

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

        rtol = 1e-08
        atol = 1e-08

        if not (np.allclose(self.old_point_var, self.solver.point_var, rtol=rtol, atol=atol)):
            self.draw_step += 1

            # 设置网格不断更新渲染
            tem_var = np.array([[0, 0, value] for value in self.solver.point_var]).astype(np.float32)
            self.meshClass.gl_var = tem_var

            self.showbox.on_realize(self.meshClass, self.old_rotation_matrix, self.draw_step)
            self.showbox.should_draw = self.should_draw
            self.showbox.glarea.queue_draw()
            self.old_point_var = self.solver.point_var.copy()


        self.old_rotation_matrix = self.showbox.rotation_matrix
        # print(self.old_projection_matrix)

        return True


    # 实时更新检测
    def DetectorWithRealTime(self, args=[]):

        def execute_code():
            if args:
                # 如果 args 不为空，将 args 里的内容作为位置参数传入 Solve 方法
                self.solver.Solve(*args)
            else:
                # 如果 args 为空，直接调用 Solve 方法
                self.solver.Solve()

        thread = threading.Thread(target=execute_code)
        thread.start()

        self.freq *= 1000  # 单位转换 s -> ms
        start_time = time.time()
        GLib.timeout_add(self.freq, self.check_for_changes_and_draw, self.all_time, start_time)


