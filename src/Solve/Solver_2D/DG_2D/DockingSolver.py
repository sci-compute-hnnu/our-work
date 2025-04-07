from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_2D.DG_2D import DG_2D


class DockingSolver(SolverWrapper):

    def __init__(self):
        super().__init__()

        self.name = 'LinearDGSolver2D'

        self.cell_type = 'triangle'

        self.data_location = 'vertex'

        self.var = ['rho', 'vx', 'vy', 'E', 'p']

    def initializeSolver(self, file):
        triangleMesh = DG_2D.TriangleMesh()
        triangleMesh.read_off(file)
        triangleMesh.collect_edges()
        self.solver = DG_2D.LinearDGSolver_2D(triangleMesh)

    def Solve(self, *args, **kwargs):

        all_time = 2
        self.solver.computeTimeDiscretization(all_time)
