#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <functional>
#include <memory>
#include "mesh_structure/TriangleMesh.h"


namespace py = pybind11;


// 参数是二维数组
void setTriangle(TriangleMesh& self, py::array_t<double> array) {
    py::buffer_info buf = array.request();

    if (buf.ndim != 2) {
        throw std::runtime_error("setVar 需要一个二维 NumPy 数组");
    }

    size_t rows = buf.shape[0];
    size_t cols = buf.shape[1];

    if (rows != 3) {
        throw std::runtime_error("输入数组的行数必须是 3");
    }

    // 获取数据指针，并将数据复制到一个 std::vector<unsigned long> 中
    double* ptr = static_cast<double*>(buf.ptr);
    std::vector<unsigned long> tri_data(rows * cols);

    for (size_t i = 0; i < rows * cols; ++i) {
        tri_data[i] = static_cast<unsigned long>(ptr[i]);  // 将 double 转换为 unsigned long
    }

    // 将数据传递给 tri_
    unsigned long* tri_[3];
    for (size_t i = 0; i < 3; ++i) {
        tri_[i] = &tri_data[i * cols];  // 获取每一行的起始指针
    }

    // 调用 setTriangle 方法
    self.setTriangle(tri_);
}

py::array_t<unsigned long> getTriangle(TriangleMesh& self) {
    // 获取指向 unsigned long 类型二维数组的指针（unsigned long**）
    unsigned long** arrayPtr = self.triangle();

    // 获取数组的行和列数
    size_t rows = 3; // 获取行数
    size_t cols = self.getNTriangle(); // 获取列数

    // 创建一个平面化的一维指针来存储所有的数组元素
    std::vector<unsigned long> flatArray(rows * cols);

    // 将二维数组的数据复制到平面化的一维数组
    for (size_t i = 0; i < rows; ++i) {
        for (size_t j = 0; j < cols; ++j) {
            flatArray[i * cols + j] = arrayPtr[i][j];
        }
    }

    // 创建 NumPy 数组，使用 buffer_info 来管理内存
    auto array = py::array(py::buffer_info(
        flatArray.data(),           // 指向平面化数组的指针
        sizeof(unsigned long),      // 每个元素的大小
        py::format_descriptor<unsigned long>::format(), // Python struct-style format descriptor
        2,                          // 维度数为 2
        { rows, cols },             // 数组的形状
        { sizeof(unsigned long) * cols, sizeof(unsigned long) } // 步幅
    ));

    // 返回 NumPy 数组
    return array;
}

// set x y z
void setX(TriangleMesh& self, py::array_t<double> array) {
    // 请求 NumPy 数组的 buffer_info
    py::buffer_info buf = array.request();

    // 获取数组的指针
    double* ptr = static_cast<double*>(buf.ptr);

    // 调用原始的 setVar 函数
    self.setX(ptr);
}
void setY(TriangleMesh& self, py::array_t<double> array) {
    // 请求 NumPy 数组的 buffer_info
    py::buffer_info buf = array.request();

    // 获取数组的指针
    double* ptr = static_cast<double*>(buf.ptr);

    // 调用原始的 setVar 函数
    self.setY(ptr);
}
void setZ(TriangleMesh& self, py::array_t<double> array) {
    // 请求 NumPy 数组的 buffer_info
    py::buffer_info buf = array.request();

    // 获取数组的指针
    double* ptr = static_cast<double*>(buf.ptr);

    // 调用原始的 setVar 函数
    self.setZ(ptr);
}

// 返回值是一维数组
py::array_t<double> getX(TriangleMesh& self) {
    // 获取 density_ 数组的指针
    double* arrayPtr = self.x_coord();

    // 获取数组的大小
    size_t size = self.getNVertex();

    // 创建 NumPy 数组，使用 buffer_info 来管理内存
    auto array = py::array(py::buffer_info(
        arrayPtr,             // 指向数据的指针
        sizeof(double),       // Size of one scalar
        py::format_descriptor<double>::format(), // Python struct-style format descriptor
        1,                    // Number of dimensions
        { size },             // Shape of the array
        { sizeof(double) }    // Strides (in bytes) for each axis
    ));

    // 返回 NumPy 数组
    return array;
}




PYBIND11_MODULE(MeshStructure, m)
{
    py::class_<TriangleMesh>(m, "TriangleMesh")
        .def(py::init<>())
        .def("read_off", &TriangleMesh::read_off)
        .def("getX", &getX);
}
