from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_3D.DG_3D import DG_3D


class DockingSolver(SolverWrapper):

    def __init__(self):
        super().__init__()

        self.name = 'LinearDGSolver3D'

        self.cell_type = 'triangle'

        self.data_location = 'vertex'

        self.var = ['rho', 'vx', 'vy', 'vz', 'E', 'p']


    def Solve(self, *args, **kwargs):

        mesh_file = kwargs['mesh_path']

        triangleMesh = DG_3D.TriangleMesh()
        triangleMesh.read_off(mesh_file)
        triangleMesh.collect_faces()
        all_time = 2
        self.solver = DG_3D.LinearDGSolver_3D(triangleMesh)
        self.solver.computeTimeDiscretization(all_time)
