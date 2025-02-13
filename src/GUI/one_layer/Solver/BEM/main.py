import numpy as np

from Solve.BEM._3D_const_BEM_Laplace import BEM_3DCESolver
from GUI.one_layer.Solver.SolverWindow import SolverWindow


class BEMSolverWindow(SolverWindow):
    def __init__(self, box1, notebook, two_layer, three_layer):
        super().__init__('../../ui/solver.glade', box1, notebook, two_layer, three_layer)

        # 边值条件输入框
        self.bc_entry = self.builder.get_object("entry")

    def start_(self, button):
        super().start_(button)

        # 获取边值条件
        g_str = self.bc_entry.get_text()
        local_dict = {}
        # 将字符串转化为函数
        exec(f"def g(x): return {g_str}", globals(), local_dict)  # local_dict['g'] 函数对象
        g = local_dict['g']
        args = [g]

        """关闭窗口"""""
        self.window.destroy()

        # 加载求解器
        self.Connector.load_solver(BEM_3DCESolver(self.selectedMeshClass))

        self.Connector.DetectorWithRealTime(args)
