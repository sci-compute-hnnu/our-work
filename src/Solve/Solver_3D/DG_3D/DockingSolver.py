from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_3D.DG_3D import PY_DG_3D


class DockingSolver(SolverWrapper):

    def __init__(self):
        super().__init__()

        self.name = 'LinearDGSolver3D'

        self.cell_type = 'tetrahedron'

        self.data_location = 'vertex'

        self.var = ['rho', 'vx', 'vy', 'vz', 'E', 'p']


    def Solve(self, *args, **kwargs):

        mesh_file = kwargs['mesh_path']

        tetrahedronMesh = PY_DG_3D.TetrahedronMesh()
        tetrahedronMesh.read_off(mesh_file)
        tetrahedronMesh.collect_faces()
        all_time = 2
        self.solver = PY_DG_3D.LinearDGSolver_3D_CycleBoundary(tetrahedronMesh)
        self.solver.computeTimeDiscretization(all_time)
