
# 📦 SolverWrapper 使用文档

## 🧩 简介

`SolverWrapper` 是一个抽象基类，用于封装不同求解器（如有限元/差分/DG 方法等）的通用接口规范，方便在可视化、数值模拟平台中对接不同的求解器。

开发者通过继承该类来实现自己的求解器，并统一变量定义、网格类型、边界条件输入方式等信息。

---

## 🛠️ 类结构

```python
class SolverWrapper(ABC):
    def __init__(self):
        self.name = None
        self.cell_type = None
        self.data_location = None
        self.bc_input_type = None
        self.var = []

    @abstractmethod
    def Solve(self, *args, **kwargs):
        pass
```

### 成员变量说明

| 属性名            | 类型       | 说明 |
|------------------|------------|------|
| `name`           | `str`      | 求解器名称 |
| `cell_type`      | `str`      | 网格类型，2D支持：`triangle`、`quadrilateral`；3D支持：`tetrahedron`、`hexahedron` |
| `data_location`  | `str`      | 渲染数据位置：`point` 或 `cell` |
| `bc_input_type`  | `str` or `None` | 边界条件输入类型：如 `file`（文件）、`pyfunc`（Python 函数）或 `None`（无需边界条件） |
| `var`            | `List[str]`| 求解变量名称，例如 `['rho', 'vx', 'vy', 'E', 'p']` |

---

## 🔧 方法说明

### `Solve(*args, **kwargs)`

> 抽象方法，子类必须实现，用于初始化 `self.solver` 并执行求解器配置。

#### 常见参数约定（通过 `kwargs` 传递）：

| 参数名         | 类型       | 说明 |
|----------------|------------|------|
| `mesh_path`    | `str`      | 网格文件路径 |
| `bc`           | `str` or `Callable` | 边界条件，可以是文件路径或 Python 函数，取决于 `bc_input_type` |

---

## 🧪 使用示例

```python
from Utils.Connector.SolverWrapper import SolverWrapper
from Solve.Solver_3D.DG_3D import PY_DG_3D

class DockingSolver(SolverWrapper):
    def __init__(self):
        super().__init__()
        self.name = 'LinearDGSolver3D'
        self.cell_type = 'tetrahedron'
        self.data_location = 'vertex'
        self.var = ['rho', 'vx', 'vy', 'vz', 'E', 'p']

    def Solve(self, *args, **kwargs):
        mesh_file = kwargs['mesh_path']
        tetrahedronMesh = PY_DG_3D.TetrahedronMesh()
        tetrahedronMesh.read_off(mesh_file)
        tetrahedronMesh.collect_faces()

        all_time = 2
        self.solver = PY_DG_3D.LinearDGSolver_3D_CycleBoundary(tetrahedronMesh)
        self.solver.computeTimeDiscretization(all_time)
```

---

## ✅ 快速集成流程

1. **继承 `SolverWrapper` 类**
2. **在 `__init__()` 中定义 `name`, `cell_type`, `data_location`, `var`, `bc_input_type` 等**
3. **在 `Solve()` 方法中初始化具体的求解器逻辑**
4. **使用时，通过 `Solve(mesh_path='your_mesh.off')` 触发求解器初始化和求解流程**

---
