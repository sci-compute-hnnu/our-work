from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_3D.BEM_FMM import CE_3D

class DockingSolver(SolverWrapper):

    def __init__(self):

        super().__init__()

        self.name = 'BEM_3DCESolver_FMM'

        self.cell_type = 'triangle'

        self.data_location = 'cell'

        self.bc_input_type = 'file'

        self.var = ['var']


    def Solve(self, *args, **kwargs):

        mesh_file = kwargs['mesh_path']
        g = kwargs['bc']  # 获取边值条件

        triangleMesh = CE_3D.TriangleMesh()
        triangleMesh.read_off(mesh_file)
        self.solver = CE_3D.BEM_3DCESolver(triangleMesh)
        self.solver.ComputeSingularIntegral()
        self.solver.computeRHS(g)
        self.solver.preconditionsolve()
