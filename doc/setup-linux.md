# Linux 环境搭建与打包指南

> 适用平台：Ubuntu 20.04 / 22.04  
> 更新日期：2026-05-05  
> 最低 Python 版本：3.8（推荐 3.10+，求解器 `.so` 模块按版本编译）

---

## 前置说明

本指南采用 **系统 Python + venv 虚拟环境** 方案：直接用 apt 安装 GTK 系统包，创建可共享系统 site-packages 的虚拟环境，避免自行编译 GTK/PyGObject 的复杂性。

---

## 一、安装系统依赖

```bash
# 1.1 基础构建工具与 Python venv
sudo apt update
sudo apt install python3.8-venv -y      # 20.04 默认 python3.8
# sudo apt install python3.10-venv -y   # 22.04 使用 python3.10

# 1.2 GTK3 运行时与 Python 绑定（PyGObject）
sudo apt install -y python3-gi python3-cairo gir1.2-gtk-3.0

# 1.3 GtkSourceView（代码编辑器组件）
sudo apt install -y gir1.2-gtksource-3.0
```

---

## 二、创建虚拟环境

在项目根目录下执行：

```bash
# 20.04
/usr/bin/python3.8 -m venv Gtk3 --system-site-packages

# 22.04
# /usr/bin/python3.10 -m venv Gtk3 --system-site-packages

# 激活环境
source Gtk3/bin/activate
```

> `--system-site-packages` 让 venv 直接使用 apt 安装的 `gi`、`cairo` 等系统包，避免 pip 安装 PyGObject 的依赖问题。

---

## 三、安装 Python 依赖

```bash
# 20.04
pip install -r requirements-20.04.txt

# 22.04
# pip install -r requirements-22.04.txt
```

两个 requirements 文件的核心差异仅在 numpy/scipy/gmsh 的版本号，其他依赖一致：

| 软件包 | 用途 |
|--------|------|
| `numpy`, `scipy` | 科学计算与稀疏矩阵求解 |
| `meshio` | 多格式网格文件读写 |
| `gmsh`, `pygmsh` | 网格生成 |
| `PyOpenGL` | OpenGL 渲染绑定 |
| `PyYAML` | 配置文件解析 |
| `chardet` | 文件编码检测 |

---

## 四、从源码启动

```bash
bash run.sh
```

`run.sh` 自动将 `src/` 加入 `PYTHONPATH` 并启动 `src/GUI/main.py`。

---

## 五、打包为独立可执行程序

```bash
bash build_pyinstaller.sh
```

输出目录：`dist/FEM-BEM-Viewer/`

---

## 六、启动打包程序

```bash
./dist/FEM-BEM-Viewer/run_FEM-BEM-Viewer.sh
```

> 启动脚本自动配置 `PYOPENGL_PLATFORM=glx` 和 `GI_TYPELIB_PATH`。

---

## 七、分发

```bash
tar -czf FEM-BEM-Viewer.tar.gz -C dist FEM-BEM-Viewer
```

---

## 注意事项

- **Python 版本与求解器兼容性**：`src/Solve/` 下的 `.so` 模块（DG_2D、DG_3D、BEM_FMM）按特定 Python 版本编译。例如 `PY_DG_2D.cpython-38-x86_64-linux-gnu.so` 仅能在 Python 3.8 下加载。请根据实际 `.so` 文件名选择匹配的 Python 版本。
- **跨系统分发限制**：PyInstaller 打包的程序依赖系统 GL 库和 GTK typelib，仅能在同版本 Ubuntu 上运行，跨版本或跨发行版会出现库版本不兼容。
