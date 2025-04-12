from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_3D.BEM._3D_const_BEM_Laplace import BEM_3DCESolver

class DockingSolver(SolverWrapper):

    def __init__(self):

        super().__init__()

        self.name = 'BEM_3DCESolver'

        self.cell_type = 'triangle'

        self.data_location = 'cell'

        self.bc_input_type = 'pyfunc'

        self.bc_pyfunc_default = ["1/np.sqrt((x[:,0]-1)**2+(x[:,1]-1)**2+(x[:,2]-1)**2)",
                                  "1/np.sqrt(x[:,0]**2 + x[:,1]**2 + x[:,2]**2)"]

        self.var = ['var']


    def Solve(self, *args, **kwargs):

        mesh_file = kwargs['mesh_path']
        g = kwargs['bc']  # 获取边值条件

        self.solver = BEM_3DCESolver(mesh_file)  # 求解器
        self.solver.ComputeSingularIntegral()
        self.solver.computeRHS(g)
        self.solver.solve()
