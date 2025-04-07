import gi
gi.require_version('Gtk', '3.0')
from GUI.one_layer.Solver.main import SolverWindow



class Solver3DWindow(SolverWindow):
    def __init__(self, box1, notebook, two_layer, three_layer):

        super().__init__('../../ui/solver.glade', box1, notebook, two_layer, three_layer)

        self.dim = 3

        _, _3d_solver_folder = self.get_solvers_folder_name()
        # 加载求解器选项
        self.populate_combobox_and_bind(_3d_solver_folder)


