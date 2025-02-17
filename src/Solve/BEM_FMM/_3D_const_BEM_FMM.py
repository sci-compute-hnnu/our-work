import CE_3D

class BEM_3DCESolver_FMM():

    def __init__(self, meshClass):  # 用于绘制OpenGL和计算

        self.meshClass = meshClass

        mesh_cpp = CE_3D.TriangleMesh()
        mesh_cpp.read_off("demo.off")

        self.solver = CE_3D.BEM_3DCESolver(mesh_cpp)

    def Solve(self):
        self.solver.ComputeSingularIntegral()
        self.solver.computeRHS()
        self.solver.preconditionsolve()


if __name__ == "__main__":

    bemsolver = BEM_3DCESolver_FMM(None)
    bemsolver.Solve()


