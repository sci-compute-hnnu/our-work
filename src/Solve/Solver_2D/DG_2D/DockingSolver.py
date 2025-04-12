from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_2D.DG_2D import PY_DG_2D


class DockingSolver(SolverWrapper):

    def __init__(self):
        super().__init__()

        self.name = 'LinearDGSolver2D'

        self.cell_type = 'triangle'

        self.data_location = 'vertex'

        self.var = ['rho', 'vx', 'vy', 'E', 'p']


    def Solve(self, *args, **kwargs):

        mesh_file = kwargs['mesh_path']

        triangleMesh = PY_DG_2D.TriangleMesh()
        triangleMesh.read_off(mesh_file)
        triangleMesh.collect_edges()
        all_time = 2
        self.solver = PY_DG_2D.LinearDGSolver_2D_CycleBoundary(triangleMesh)
        self.solver.computeTimeDiscretization(all_time)
