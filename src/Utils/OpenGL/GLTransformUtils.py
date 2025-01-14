import numpy as np

# 计算透视投影矩阵
def set_perspective_matrix(fov, aspect_ratio, near_plane, far_plane):
    f = 1.0 / np.tan(fov / 2.0)
    z_range = near_plane - far_plane

    # 构建透视投影矩阵
    projection_matrix = np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far_plane + near_plane) / z_range, (2 * far_plane * near_plane) / z_range],
        [0, 0, -1, 0]
    ], dtype=np.float32)

    return projection_matrix


# 计算观察矩阵
def set_view_matrix(camera_position, target_position, up_vector):
    forward = target_position - camera_position
    forward = forward / np.linalg.norm(forward)

    right = np.cross(forward, up_vector)
    right = right / np.linalg.norm(right)

    up = np.cross(right, forward)

    view_matrix = np.array([
        [right[0], up[0], -forward[0], 0],
        [right[1], up[1], -forward[1], 0],
        [right[2], up[2], -forward[2], 0],
        [-np.dot(right, camera_position), -np.dot(up, camera_position), np.dot(forward, camera_position), 1]
    ], dtype=np.float32)

    return view_matrix
