set(Python EXECUTABLE "E:/msys2/mingw64/bin/python.exe")

Pybind11_add_module(MeshStructure bindings.cpp)
target_link_libraries(MeshStructure PRIVATE triangle_mesh)