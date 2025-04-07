from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_3D.BEM._3D_const_BEM_Laplace import BEM_3DCESolver

class DockingSolver(SolverWrapper):

    def __init__(self):

        super().__init__()

        self.name = 'BEM_3DCESolver'

        self.cell_type = 'triangle'

        self.data_location = 'cell'

        self.bc_input_type = 'pyfunc'

        self.var = ['var']



    def initializeSolver(self, file):

        self.solver = BEM_3DCESolver(file)  # 求解器



    def Solve(self, *args, **kwargs):

        g = kwargs['bc']  # 获取边值条件

        self.solver.ComputeSingularIntegral()
        self.solver.computeRHS(g)
        self.solver.solve()
