from abc import ABC, abstractmethod

class SolverWrapper(ABC):

    def __init__(self):

        """
        初始化 SolverWrapper 对象

        成员:
        name:  求解器名字
        docking_solver: 求解器
        cell_type: 用于指定网格类型 2维包括: triangle, quadrilateral 3维包括: tetrahedron, hexahedron
        data_location: 渲染的单元(根据给定的渲染数据来定), 包括 point, edge, cell
        bc_input_type: 边值条件输入方式  e.g. file（输入文件）, pyfunc（python函数）, None（无需输入边值条件）
        var: 变量名数据 e.g. ['rho', 'vx', 'vy', 'E', 'p']

        # 可选变量
        args(可选): 可能传入Solver的变量
        bc_pyfunc_default(可选):  提前设置python函数的边值条件 （当bc_input_method为pyfunc时）
        """

        self.name = None  # 求解器名字

        self.cell_type = None  # 网格类型

        self.data_location = None  # 渲染单元

        self.bc_input_type = None  # 边值条件输入方式

        self.var = []  # 变量名

        self.bc_pyfunc_default = ["1/np.sqrt((x[:,0]-1)**2+(x[:,1]-1)**2+(x[:,2]-1)**2)",
                                  "1/np.sqrt(x[:,0]**2 + x[:,1]**2 + x[:,2]**2)"]   # 默认设置的边值条件函数


    @abstractmethod
    def initializeSolver(self, file):
        pass

    @abstractmethod
    def Solve(self, *args, **kwargs):
        pass
