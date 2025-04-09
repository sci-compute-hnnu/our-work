import numpy as np

# 假设 n 和 num 的值
n = 3
num = 4

# 创建一个长度为 n * num 的 ndarray
arr = np.arange(n * num)

# 使用 reshape 方法将数组转换为所需的形状
reshaped_arr = arr.reshape(n, -1)

print("原始数组：")
print(arr)
print("重塑后的数组：")
print(reshaped_arr)
