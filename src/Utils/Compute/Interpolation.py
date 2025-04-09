import numpy as np

def barycentric_coordinates(p, p0, p1, p2, p3):
    """
    计算点 p 相对于四面体顶点 p0, p1, p2, p3 的重心坐标
    """
    # 构建系数矩阵
    A = np.vstack([p0, p1, p2, p3]).T
    A = np.vstack([A, np.ones((1, 4))])
    # 构建常数向量
    b = np.append(p, 1)
    # 求解线性方程组
    lambdas = np.linalg.solve(A, b)
    return lambdas

def tetrahedral_lagrange_interpolation(p, p0, p1, p2, p3, var0, var1, var2, var3):
    """
    四面体拉格朗日插值计算交点的 var 值
    """
    # 计算重心坐标
    lambdas = barycentric_coordinates(p, p0, p1, p2, p3)
    # 进行加权求和
    var = lambdas[0] * var0 + lambdas[1] * var1 + lambdas[2] * var2 + lambdas[3] * var3
    return var
