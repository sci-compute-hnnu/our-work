import gi
gi.require_version('Gtk', '3.0')
from GUI.one_layer.Solver.main import SolverWindow
from Utils.Config.path import ui_dir


class Solver2DWindow(SolverWindow):
    def __init__(self, box1, notebook, two_layer, three_layer):

        super().__init__(ui_dir+'solver.glade', box1, notebook, two_layer, three_layer)

        self.dim = 2

        _2d_solver_folder, _ = self.get_solvers_folder_name()
        # 加载求解器选项
        self.populate_combobox_and_bind(_2d_solver_folder)