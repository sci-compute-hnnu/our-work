import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres, lgmres
import time

import meshio

class BEM_3DCESolver():

    def __init__(self, path):  # 用于绘制OpenGL和计算

        mesh = meshio.read(path)
        vertexs = mesh.points
        faces = mesh.cells_dict['triangle']

        self.vertexs = vertexs  # 所有结点值
        self.faces = faces   # 每个单元对应的节点编号

        self.nodes = (self.vertexs[self.faces[:, 0], :] + self.vertexs[self.faces[:, 1], :] +
                      self.vertexs[self.faces[:, 2], :]) / 3  # 配置点


        self.gDof = np.shape(self.faces)[0]  # 单元个数, 整体自由度
        self.Jac = np.zeros(self.gDof)
        self.rhs = np.zeros(self.gDof)  # 用来储存右端向量
        self.density = np.zeros(self.gDof)  # 存储密度函数的值
        self.step = 0
        self.diag_ele = np.zeros(self.gDof)  # 存储对角线元素
        self.density_list = []

        self.point_var = np.zeros(len(self.vertexs))
        self.cell_var = np.zeros(len(self.faces))

    def ComputeSingularIntegral(self):
        E = np.sum((self.vertexs[self.faces[:, 0], :] - self.vertexs[self.faces[:, 2], :]) ** 2, 1)
        F = np.sum((self.vertexs[self.faces[:, 0], :] - self.vertexs[self.faces[:, 2], :]) * (
                self.vertexs[self.faces[:, 1], :] - self.vertexs[self.faces[:, 2], :]), 1)
        G = np.sum((self.vertexs[self.faces[:, 1], :] - self.vertexs[self.faces[:, 2], :]) ** 2, 1)
        self.Jac = np.sqrt(E * G - F ** 2)  # 变换的雅可比行列式
        a = np.sqrt(E)
        b = np.sqrt(G)
        c = np.sqrt(E + G - 2 * F)
        d = np.sqrt(4 * E + G - 4 * F)
        e = np.sqrt(E + G + 2 * F)
        f = np.sqrt(E + 4 * G - 4 * F)
        # 计算系数矩阵主对角线上的元素
        self.diag_ele = self.Jac / 3 * (np.log((4 * E - 2 * F + 2 * a * d) / (-2 * E - 2 * F + 2 * a * e)) / a + np.log(
            (4 * G - 2 * F + 2 * b * f) * (2 * G + 2 * F + 2 * b * e) / (G - 2 * F + b * d) / (
                    -G + 2 * F + b * d)) / b + np.log(
            (4 * E + 2 * G - 6 * F + 2 * d * c) / (-2 * E - 4 * G + 6 * F + 2 * f * c)) / c) / (4 * np.pi)

    def ComputePotential(self, charge):
        psi = np.zeros(self.gDof)
        for i in range(self.gDof):  # 按配置点循环
            G_value = np.sqrt(np.sum((self.nodes[:, :] - self.nodes[i, :]) ** 2, 1))
            G_value[i] = 1
            G_value = 1 / G_value / (4 * np.pi)
            G_value[i] = 0
            psi[i] = charge.dot(G_value)
        return psi


    # 迭代法所需的全局矩阵乘向量运算
    def globalMatrixProdVector(self, gx):
        t1 = time.time()
        gAx = np.zeros(self.gDof)
        charge = self.Jac / 2 * gx
        psi = self.ComputePotential(charge)
        for i in range(self.gDof):  # 按配置点循环
            B_i = self.diag_ele[i] * gx[i]
            gAx[i] = psi[i] + B_i
        self.step += 1

        # 计算每个面的权值
        self.cell_var = gAx

        t2 = time.time()
        print(self.step)
        print(str(t2 - t1) + 's')

        return gAx


    def getRenderingData(self):

        return self.cell_var



    def computeRHS(self, bdry_fun):
        self.rhs = bdry_fun(self.nodes)  # 右端向量, 即边界值
        return

    def gmres_callback(self, density):
        self.density_list.append(density)

    # 迭代法求解线性代数方程组
    def solve(self):

        AA = LinearOperator((self.gDof, self.gDof), self.globalMatrixProdVector)
        self.density, exitCode = gmres(AA, self.rhs, tol=1e-8, callback=self.gmres_callback)  # 应用GMRES迭代法

        # print('看看密度函数节点处的数值解', self.density)
        return

    # 通过密度函数的数值近似计算函数u的数值解
    def computeNumericalSolution(self, x, y, z):
        # 用一点公式近似
        A_e = 1 / np.sqrt((x - self.nodes[:, 0]) ** 2 + (y - self.nodes[:, 1]) ** 2 + (z - self.nodes[:, 2]) ** 2)
        I = self.Jac * A_e / (8 * np.pi)
        uh = np.dot(I, self.density)
        return uh

    # 误差估计
    def LinfError(self):
        # 取点
        radius = np.linspace(1.1, 5, 10)
        theta = np.linspace(0, 2 * np.pi, 10)
        phi = np.linspace(0, np.pi, 10)
        radius, theta, phi = np.meshgrid(radius, theta, phi)  # 生成网格
        x = radius * np.cos(theta) * np.sin(phi)
        y = radius * np.sin(theta) * np.sin(phi)
        z = radius * np.cos(phi)
        vec_x = x.reshape((np.size(x), 1))
        vec_y = y.reshape((np.size(y), 1))
        vec_z = z.reshape((np.size(z), 1))
        uh = self.computeNumericalSolution(vec_x, vec_y, vec_z)
        uh = uh.reshape(x.shape)
        # print('看看数值解', uh)

        # exact_u = 1 / np.sqrt((x - 1) ** 2 + (y - 1) ** 2 + (z - 1) ** 2)  # 存内问题的精确解
        exact_u = 1 / np.sqrt(x ** 2 + y ** 2 + z ** 2)  # 存外问题的精确解
        # print('精确解',exact_u)
        err = uh - exact_u
        InfErr = np.linalg.norm(err.reshape(np.size(err)), ord=np.inf)
        print('节点数为{}时,精确解和数值解的无穷范数为'.format(self.gDof), InfErr)
        L2Err = np.linalg.norm(err.reshape(np.size(err)) / np.size(err), ord=2)
        print('节点数为{}时,精确解和数值解的L2范数为'.format(self.gDof), L2Err)
        return L2Err


if __name__ == "__main__":
    # g = lambda x: 1 / np.sqrt((x[:, 0] - 1) ** 2 + (x[:, 1] - 1) ** 2 + (x[:, 2] - 1) ** 2)  # 内问题的边值条件
    g = lambda x: 1 / np.sqrt(x[:, 0] ** 2 + x[:, 1] ** 2 + x[:, 2] ** 2)  # 外问题的边值条件

    # 读取网格信息
    path = '../../../../data/ball_triangleMesh.off'

    bemsolver = BEM_3DCESolver(path)








