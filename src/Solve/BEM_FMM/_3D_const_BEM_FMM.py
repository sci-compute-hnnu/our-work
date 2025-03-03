from Solve.BEM_FMM import CE_3D
import numpy as np

class BEM_3DCESolver_FMM():

    def __init__(self, meshClass):  # 用于绘制OpenGL和计算

        self.meshClass = meshClass

        self.mesh_cpp = CE_3D.TriangleMesh()
        self.mesh_cpp.read_off("demo.off")

        self.solver = CE_3D.BEM_3DCESolver(self.mesh_cpp)

        self.point_var = self.per_vertex_var(self.solver.getVar())

    def Solve(self):
        self.solver.ComputeSingularIntegral()
        self.solver.computeRHS()
        self.solver.preconditionsolve()


    def per_vertex_var(self, cellsData):
        VN = np.zeros(1596, dtype=np.float32)

        facess = np.array(1596).reshape(-1, 3)

        for i in range(len(1596)):

            num = 0
            faces_using = np.where(facess == i)[0]

            for j in faces_using:
                VN[i] += cellsData[j]
                num += 1
            VN[i] = VN[i] / num

        return VN


if __name__ == "__main__":

    bemsolver = BEM_3DCESolver_FMM(None)
    bemsolver.Solve()


