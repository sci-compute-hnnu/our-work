# FEM/BEM 可视化平台 — 开发手册

> 面向团队新成员，帮助快速理解各模块职责与函数作用。

---

## 目录

1. [项目总览](#1-项目总览)
2. [启动流程](#2-启动流程)
3. [GUI 模块](#3-gui-模块)
4. [后处理 / OpenGL 渲染](#4-后处理--opengl-渲染)
5. [前处理 / 网格生成](#5-前处理--网格生成)
6. [求解器集成](#6-求解器集成)
7. [Utils 工具库](#7-utils-工具库)
8. [Shell 模块](#8-shell-模块)
9. [C++ 插件](#9-c-插件)

---

## 1. 项目总览

```
src/
├── GUI/          # GTK3 图形界面 (三层菜单 + notebook/viewport 系统)
├── Post/         # OpenGL 3D 渲染 (GLArea 封装 + 着色器管线)
├── Pre/          # 网格生成 (Gmsh/pygmsh)
├── Solve/        # 求解器调度 (对接 C++ 求解模块)
├── Shell/        # 嵌入式命令行
└── Utils/        # 工具库 (网格读写、几何计算、配置、着色器、求解器连接)
ui/               # Glade XML 布局文件
icon/             # 图标资源
plugin/           # C++ 求解器源码 (pybind11 + CMake)
data/             # 示例网格文件
```

**数据流概要：**

```
网格文件(.off/.msh/.dat) → MeshReader → FaceMesh/BodyMesh
    → base_glarea.load_mesh() → VBO/IBO → 着色器渲染

求解器(.so) → DockingSolver → SolverViewBoxConn
    → 轮询 getRenderingData() → 更新 gl_var → 触发重绘
```

---

## 2. 启动流程

`run.sh` → `python3 src/GUI/main.py`

`main.py` 中的 `UI.__init__()` 执行：

1. 加载 `ui/main.glade`，从 XML 构建全部 GTK 控件
2. 依次初始化 `box0`、`one_layer`、`two_layer`、`three_layer`
3. 连接全部信号（按钮点击、notebook 切换、鼠标事件等）
4. 通过 `notebook.create_tab("Layout #1", func=1)` 创建初始 view_box
5. `window.show_all()` + `Gtk.main()` 进入事件循环

---

## 3. GUI 模块

### 3.1 `GUI/main.py` — 主窗口与信号连接

| 类/函数 | 作用 |
|----------|------|
| `UI.__init__()` | 加载 Glade 文件，初始化三层菜单和 box0，连接所有信号 |
| `UI.get_current_showbox()` | 返回 notebook 当前激活的 showbox（供各层按钮的 lambda 回调使用） |
| `UI.run()` | 显示窗口，启动 GTK 主循环 |

**信号连接模式：** 所有按钮信号使用 `lambda` 包装，确保回调触发时 `get_current_showbox()` 获取的是实时的当前激活窗口。

### 3.2 `GUI/one_layer/` — 顶部菜单栏

**`one_layer/main.py` — `one_layer` 类**

菜单包含：File, Edit, View, Mesh, Solver, Style

| 函数 | 作用 |
|------|------|
| `loadWidget(box1, notebook, two_layer, three_layer)` | 注入其他 UI 组件的引用 |
| `PB_active(button, box1)` | 控制 Pipeline Browser 面板显隐 |
| `information_active(button, box1)` | 控制 information 面板显隐 |
| `apply_clicked/reset_clicked/delete_clicked` | 编辑动作的控制 |
| `open_2d_mesh_widonw(button)` | 弹出 2D 网格生成窗口 |
| `open_3d_mesh_widonw(button)` | 弹出 3D 网格生成窗口 |
| `open_2D_solver_window(button)` | 弹出 2D 求解器窗口 |
| `open_3D_solver_window(button)` | 弹出 3D 求解器窗口 |
| `change_style(button)` | 切换 UI 图标风格 (Default / Simple / Dark) |

**`one_layer/Style/main.py` — `Style` 类**

| 函数 | 作用 |
|------|------|
| `default_style()` | 恢复默认图标风格（内置图标 + 部分自定义 PNG） |
| `set_icons(style_type)` | 按 Simple / Dark 主题切换全部图标 |

**`one_layer/Mesh/_2D_Mesh/main.py` — `_2DMeshWindow` 类**

2D 网格生成窗口，支持圆形、矩形、自定义多边形。

| 函数 | 作用 |
|------|------|
| `loadWidget(box1)` | 注入 box1 引用 |
| `on_button_cir_clicked / rec / other` | 切换 Stack 页面到对应形状的参数输入面板 |
| `on_confirm_clicked(button)` | 收集参数 → 调用 `_2D_generate_mesh` → 构造 `FaceMesh` → 载入 `box1.MeshList` → 关闭窗口 |
| `on_cancel_clicked(button)` | 清空输入框 |
| `on_structured_mesh_toggled(button)` | 切换结构化/非结构化网格，显示/隐藏方向选项 |

**`one_layer/Mesh/_3D_Mesh/main.py` — `_3DMeshWindow` 类**

3D 网格生成窗口，支持长方体、球体、自定义（点+面定义）。

| 函数 | 作用 |
|------|------|
| `loadWidget(box1)` | 注入 box1 引用 |
| `on_button_cube_clicked / sphe / other` | 切换形状参数页面 |
| `on_confirm_clicked(button)` | 收集参数 → 调用 `_3D_generate_mesh` → 构造 `BodyMesh` → 载入 `box1.MeshList` |

**`one_layer/Solver/main.py` — `SolverWindow` 类**

求解器调度窗口基类，2D/3D 子类通过 `self.dim` 区分。

| 函数 | 作用 |
|------|------|
| `get_solvers_folder_name()` | 扫描 `src/Solve/Solver_2D/` 和 `Solver_3D/` 下的子文件夹，返回求解器名称列表 |
| `get_docking_solver(file_path)` | 动态 import 指定路径的 `.py` 文件，实例化其中的 `DockingSolver` 类 |
| `on_selection_changed(widget)` | 切换求解器时：动态加载 DockingSolver → 更新边值条件输入框、变量名列表 |
| `set_bc_box(choice)` | 根据求解器的 `bc_input_type` 切换边值条件输入方式（文件 / Python 函数表达式） |
| `start_(button)` | 收集参数 → 加载 `SolverViewBoxConn` → `detectorWithRealTime()` 启动后台求解+实时渲染 |
| `execute_pyfunc(pyfunc_str)` | 将字符串编译为 Python 可调用函数（边值条件） |

**`one_layer/Solver/Solver2D/main.py` — `Solver2DWindow(SolverWindow)`**
- 设置 `self.dim = 2`，加载 `solver.glade`，填充 2D 求解器列表

**`one_layer/Solver/Solver3D/main.py` — `Solver3DWindow(SolverWindow)`**
- 设置 `self.dim = 3`，加载 `solver.glade`，填充 3D 求解器列表

### 3.3 `GUI/two_layer/main.py` — 第二层工具栏

| 类/函数 | 作用 |
|----------|------|
| `back_color` (Enum) | 预定义 6 种背景颜色 |
| `two_layer.on_file_set(widget, box1, showbox)` | 弹出文件选择对话框 → 调用 `box1.load_Mesh_file()` 加载网格 |
| `two_layer.set_back_color(button, showbox, back_color)` | 修改当前 viewport 背景色 |
| `two_layer.on_screenshot_button_clicked(showbox, box1, widget)` | 截取 OpenGL 视口并保存为 PNG |
| `two_layer.take_screenshot(notebook, box1)` | 用 `glReadPixels` 读取 OpenGL 帧缓冲 → Cairo 转换 |
| `two_layer.get_custom_filename(default_filename)` | 在 `results/photo/` 下生成带时间戳的文件名 |

### 3.4 `GUI/three_layer/main.py` — 第三层工具栏

| 函数 | 作用 |
|------|------|
| `setup_combobox(select_box_num, options, default_option)` | 初始化 0 号(颜色/变量)或 1 号(点线面类型)下拉框 |
| `select_option_with_face_or_edge(widget, showbox)` | 切换绘制模式：Lines / Surface / Points / Surface With Edges / Gmsh style |
| `select_option_with_color(widget, showbox)` | 切换变量着色模式（Neutral Mode 或按变量值着色） |
| `restore_original_state(button, showbox, func)` | 放大 (func=1) / 缩小 (func=2) |
| `set_view_to_XYZ(button, showbox, func)` | 切换视角到 ±X, ±Y, ±Z 或等轴测视图 |
| `rotation_90(button, showbox, func)` | 顺时针/逆时针旋转 90° |
| `select_color(button, showbox)` | 弹出 GTK 颜色选择器，设定面颜色 |
| `open_split_plane_input(button, showbox, box1)` | 弹出切平面方程输入窗口 |
| `disable_three_layer() / enable_three_layer()` | 禁用/启用第三层全部按钮（非 view_box 时禁用） |

**`three_layer/PlaneEquationInputWindow.py` — `SplitPlaneEquationWindow`**

| 函数 | 作用 |
|------|------|
| `load_widget(meshClass, box1)` | 注入被切网格和 box1 引用 |
| `on_button_confirm_clicked(button)` | 读取平面方程 a/b/c/d → 构造 `MeshSplitter` → 执行 `split()` → 将三个结果网格载入 box1 |
| `on_key_press(widget, event)` | 方向键在四个输入框间切换焦点 |

### 3.5 `GUI/box0/` — 主内容区容器层级

整体嵌套结构：

```
box0
└── box2 (右侧工具栏按钮: 文件浏览器 / 变量表)
└── paned0 (水平分割)
    ├── box1 (左侧: Pipeline Browser + information)
    └── paned1 (水平分割)
        ├── paned2 (垂直分割)
        │   ├── shell_box (命令行)
        │   └── notebook (多标签页 viewport)
        └── box3 (文件夹/文件浏览面板, 默认隐藏)
```

**`box0/main.py` — `box0` 类**
- 持有 `box2` 和 `paned0`，是最外层容器

**`box0/box2.py` — `box2` 类**

右侧两个按钮的实现：

| 函数 | 作用 |
|------|------|
| `file_button_clicked(button, paned1, box3)` | 在 paned1 右侧显示文件夹浏览面板 (box3) |
| `variable_button_clicked(button, paned1, paned2, shell_box)` | 在 paned1 右侧显示变量表格（从 shell 的 variables 字典读取） |
| `close_variable_box(widget, box)` | 隐藏变量表格 |

**`box0/paned0/main.py` — `paned0` 类**
- 持有 `box1` 和 `paned1`
- `on_paned_position_changed(paned, param)` — 限制拖拽范围 300~900px

**`box0/paned0/box1.py` — `box1` 类**

Pipeline Browser + information 面板：

| 函数 | 作用 |
|------|------|
| `load_Mesh_file(filename)` | 通过 `MeshReader` 读取文件 → 追加到 `self.MeshList` → 更新 ListStore |
| `load_Mesh(mesh, name)` | 将已有的 mesh 对象追加到 `self.MeshList` |
| `on_toggle_button_toggled(cell, path_str, showbox, ...)` | 复选框点击：切换选中网格 → 更新 showbox 的 `color_opt_list` / `type_opt_list` → 触发重绘 |
| `find_true_row()` | 找到 ListStore 中唯一为 True 的行索引（-1 表示无选中） |
| `record_status_from_list_store()` | 将 ListStore 的全部勾选状态导出为列表 |
| `from_list_change_status(status_list)` | 用传入的状态列表批量更新 ListStore |
| `info_print(info)` | 向 information 面板追加文本 |
| `apply_clicked / reset_clicked / delete_clicked` | 编辑操作，委托自 one_layer |
| `on_paned_position_changed(paned, param)` | 限制拖拽范围 400~700px，控制在 PB 和 info 之间的伸缩 |

**`box0/paned0/paned1/main.py` — `paned1` 类**
- 持有 `paned2` 和 `box3`
- `on_paned_position_changed` — 限制拖拽范围 1250~2000px

**`box0/paned0/paned1/box3.py` — `box3` 类**

右侧文件夹/文件浏览面板：

| 函数 | 作用 |
|------|------|
| `on_open_folder_clicked(button)` | 弹出文件夹选择对话框 |
| `open_folder(folder_path)` | 创建文件树视图并填充 |
| `create_paned_view(folder_path)` | 构建 TreeView + 后台线程加载目录结构 |
| `on_file_activated(tree_view, path, column, edit_box)` | 点击文件时的处理（在 edit_box 中打开） |
| `list_files(folder_path, file_store)` | 递归扫描文件夹 |
| `newFile_clicked(button, edit_box)` | 在 edit_box 中新建空白标签页 |
| `saveEdit_clicked(button, edit_box)` | 保存编辑内容到文件 |
| `close_editFile_box(widget)` | 隐藏 box3 面板 |

**`box0/paned0/paned1/paned2/main.py` — `paned2` 类**
- 持有 `shell_box` 和 `notebook`
- `on_paned_position_changed` — 控制 shell_box 和 notebook 的伸缩与隐藏（随拖拽位置改变）

**`box0/paned0/paned1/paned2/shell_box.py` — `shell_box` 类**

| 函数 | 作用 |
|------|------|
| `on_key_press(widget, event, paned1, paned2)` | 回车键触发命令执行 |
| `execute_command(paned1, paned2)` | 解析最后一个 `>>>` 后的命令 → `CommandProcessor.process_command()` → 显示结果 |
| `on_shell_toggled(widget, paned2)` | View 菜单 Shell 开关 |
| `update_variable_tree_view(paned1, paned2)` | 命令执行后刷新变量表 |
| `shell_close(button, one_layer)` | 隐藏 shell 面板 |

### 3.6 Notebook / Viewport 系统

**`notebook/main.py` — `notebook` 类**

多标签页容器。每个标签页（Layout）对应一个 `containerList[num]` 条目：`[idx, [bbox1, bbox2, ...]]`，其中 `idx` 记录当前激活的 bbox 索引。

| 函数 | 作用 |
|------|------|
| `creat_bbox(num, func)` | 工厂方法：func=0→menu_box, 1→view_box, 2→data_box, 3→edit_box |
| `create_tab(title, func)` | 创建新标签页（含关闭按钮），插入 notebook |
| `from_add_button(button)` | 点击 + 按钮时自动分配最小可用 Layout 号 |
| `from_on_switch_page(button, page, page_num)` | 切换标签页时恢复上一次锁定的 bbox |
| `choose_one_box(widget, event, bbox, force)` | 激活指定 bbox：更新 `self.showbox`，绘制蓝色边框，根据 bbox 类型启用/禁用 three_layer |
| `close_current_tab(widget, box)` | 关闭标签页并从 containerList 中移除 |
| `find_Layout_Num(blue_edge_box)` | 从 EventBox 向上查找定位到 Layout 编号 |
| `setting_other_widget(box1, box3, three_layer)` | 注入外部依赖 |

**`notebook/top_box_of_every_type.py` — `top_box_of_every_type` 类**

每个 bbox 的公共头部（分割按钮、关闭按钮、蓝色边框）。

| 函数 | 作用 |
|------|------|
| `view_blue_edge(widget, notebookClass)` | CSS 高亮当前选中的 bbox |
| `on_add_paned_clicked(button, notebookClass, orientation)` | 分割当前 bbox（水平/垂直），创建新的 menu_box 并放入 Gtk.Paned |
| `close_one_box(button, notebookClass)` | 关闭当前 bbox：若被分割过则替换回另一个 bbox，否则转为 menu_box |

**`notebook/view_box.py` — `view_box` 类**

3D 渲染视口。

| 函数 | 作用 |
|------|------|
| `on_render(area, contex)` | 渲染回调：根据 `should_draw` 决定调用 `on_render` 还是 `on_render_background` |
| `on_realize(mesh, rotation_matrix)` | 加载网格并初始化 OpenGL（调用 `base_glarea.load_mesh()` + `on_realize()`） |
| `queue_draw()` | 触发 GTK GLArea 重绘 |
| `get_last_rotation()` | 获取当前旋转矩阵（用于变量着色切换时保持视角） |
| `get_current_mesh()` | 获取当前渲染的 mesh 对象（用于切平面操作） |

**`notebook/menu_box.py` — `meun_box` 类**

新标签页的欢迎页面，提供三个功能入口。

| 函数 | 作用 |
|------|------|
| `turn_to_otherbox(button, notebookClass, func)` | 点击按钮将当前 menu_box 替换为 view_box (1) / data_box (2) / edit_box (3) |

**`notebook/data_box.py` — `data_box` 类`

网格数据表格展示。

| 函数 | 作用 |
|------|------|
| `on_showing_value(widget, box1)` | 选择要显示的网格文件 |
| `on_attribute_value(widget)` | 切换 Points / Cells 视图 |
| `on_precision_value(widget)` | 控制小数点位数 |
| `data_list()` | 显示顶点坐标表 (Num, X, Y, Z) |
| `cell_list()` | 显示单元索引表 (Num, Cell ID, Cell Type) |

**`notebook/edit_box.py` — `edit_box` 类**

内嵌文本编辑器（基于 GtkSourceView）。

| 函数 | 作用 |
|------|------|
| `display_file_content(text_view, label_text)` | 在 notebook 中新建编辑标签页 |
| `set_language_for_file(file_path, text_view)` | 根据文件扩展名设置语法高亮 |

---

## 4. 后处理 / OpenGL 渲染

### 4.1 `Post/BaseGLArea.py` — `base_glarea` 类

核心 3D 渲染类，封装 `Gtk.GLArea`。每个 `view_box` 持有一个实例。

**数据加载：**

| 函数 | 作用 |
|------|------|
| `load_mesh(mesh)` | 从 FaceMesh/BodyMesh 提取 `gl_points`, `gl_cells`, `gl_edges`, `gl_normal`, `gl_var` |

**初始化与渲染：**

| 函数 | 作用 |
|------|------|
| `on_realize(rotation_matrix, color_opt)` | 初始化着色器程序、VBO/IBO、透视投影矩阵、观察矩阵、光源位置；setup 顶点属性指针 |
| `on_render(area, contex)` | 每帧渲染：清屏 → 绑 VAO → 向着色器传 uniform（矩阵、颜色、光源）→ 按当前模式绘制面/边/点/Gmsh/变量 |
| `on_render_background(area, contex)` | 仅渲染背景色+小坐标轴（无网格时或 should_draw==-1 时） |

**交互：**

| 函数 | 作用 |
|------|------|
| `on_button_press(area, event)` | 记录鼠标点击起始位置 |
| `on_mouse_move(area, event)` | 左键拖拽旋转（更新 `rotation_matrix`），右键拖拽平移（更新 `translation_matrix`） |
| `on_scroll(area, event)` | 滚轮缩放（修改 `scale` → 累积到 `rotation_matrix`） |

**工具函数：**

| 函数 | 作用 |
|------|------|
| `update_rotation_matrix()` | 从 `angle_x` / `angle_y` 计算旋转矩阵并累积 |
| `update_translation_matrix()` | 从 `translate_x` / `translate_y` 直接设置平移矩阵 |
| `set_background_color(red, green, blue, alpha)` | 设置 `glClearColor` |
| `init_axes()` | 初始化小坐标轴的 VBO 和着色器程序 |
| `draw_small_axes()` | 在视口右下角绘制旋转跟踪的 RGB 小坐标轴 |

---

## 5. 前处理 / 网格生成

### 5.1 `Pre/MeshGeneration.py`

基于 Gmsh 的网格生成。

| 函数 | 作用 |
|------|------|
| `_2D_generate_mesh(shape, mesh_size, algorithm, selection)` | 2D 非结构化网格生成（圆形/矩形/自定义多边形） |
| `_2D_generate_stru_mesh(shape, mesh_size, selection)` | 2D 结构化网格生成（扇形分割/矩形超限网格） |
| `_3D_generate_mesh(shape, mesh_size, algorithm, mesh_type)` | 3D 网格生成（长方体/球体/自定义体），支持 Surface/Volume 两种模式 |

2D 使用 `pygmsh`；3D 使用低层 `gmsh` API。

---

## 6. 求解器集成

### 6.1 整体架构

```
SolverWrapper (ABC)
    └── DockingSolver (每个求解器一个)
            └── C++ .so 模块 (pybind11)

SolverViewBoxConn (桥接层)
    ├── 后台线程执行 Solve()
    └── GLib.timeout_add 定时轮询 → 更新渲染
```

### 6.2 `Utils/Connector/SolverWrapper.py` — ABC

| 成员 | 说明 |
|------|------|
| `name: str` | 求解器名称 |
| `cell_type: str` | 网格类型 (triangle/quadrilateral/tetrahedron/hexahedron) |
| `data_location: str` | 渲染数据在 `vertex` 还是 `cell` 上 |
| `bc_input_type: str` | 边值条件输入方式 (file / pyfunc / None) |
| `var: List[str]` | 变量名列表 |
| `bc_pyfunc_default: List[str]` | （可选）预设的 Python 边值函数表达式 |
| `Solve(*args, **kwargs)` | 抽象方法，子类实现：初始化 C++ 求解器并开始求解 |

### 6.3 各 DockingSolver

**`Solve/Solver_2D/DG_2D/DockingSolver.py`** — 2D DG 求解器
- `cell_type='triangle'`, `data_location='vertex'`, `var=['rho','vx','vy','E','p']`
- Solve: 创建 `TriangleMesh` → `read_off()` → 创建 `LinearDGSolver_2D_CycleBoundary` → `computeTimeDiscretization(2)`

**`Solve/Solver_3D/DG_3D/DockingSolver.py`** — 3D DG 求解器
- `cell_type='tetrahedron'`, `data_location='vertex'`, `var=['rho','vx','vy','vz','E','p']`
- Solve: 创建 `TetrahedronMesh` → `read_off()` → 创建 `LinearDGSolver_3D_CycleBoundary` → `computeTimeDiscretization(2)`

**`Solve/Solver_3D/BEM/DockingSolver.py`** — 3D BEM 求解器
- `cell_type='triangle'`, `data_location='cell'`, `bc_input_type='pyfunc'`
- Solve: `ComputeSingularIntegral()` → `computeRHS(g)` → `solve()`

**`Solve/Solver_3D/BEM_FMM/DockingSolver.py`** — 3D BEM + FMM 快速求解器
- `cell_type='triangle'`, `data_location='cell'`, `bc_input_type='file'`
- Solve: `ComputeSingularIntegral()` → `computeRHS(g)` → `preconditionsolve()`

### 6.4 `Utils/Connector/SolverViewBoxConn.py` — 桥接器

核心职责：将后台求解器的输出实时映射到 OpenGL 渲染。

| 函数 | 作用 |
|------|------|
| `load_solver(docking_solver)` | 保存求解器引用，确定数据位置和变量名 |
| `load_fit(showbox, mesh, timer, box1, freq, all_time)` | 注入渲染相关组件 |
| `load_var()` | 从求解器获取 `getRenderingData()` → 按 `data_location` 转换为点值 → 更新 mesh 的 `gl_var` |
| `cell_to_vertex_values(cellsData)` | 将面心数据插值到顶点（对每个顶点取共用面的平均值） |
| `check_for_changes_and_draw(all_time, start_time)` | GLib 定时回调：检查 `getRenderingData()` 是否有新值 → 有则 `load_var()` + `on_realize()` + `queue_draw()` |
| `detectorWithRealTime(*args, **kwargs)` | 启动后台线程执行 `Solve()`，并设置 GLib timeout 定时轮询 |

### 6.5 `Utils/Connector/OutputTracker.py` — 输出捕获器

| 函数 | 作用 |
|------|------|
| `start_tracking()` | 重定向 `sys.stdout` 到内部缓冲区 |
| `stop_tracking()` | 恢复 `sys.stdout` |
| `get_new_output()` | 获取并清空缓冲区内容（去重：相同内容不重复返回） |

用于捕获求解器 `print()` 输出并显示在 information 面板。

---

## 7. Utils 工具库

### 7.1 `Utils/Mesh/MeshClass.py` — 网格数据结构

**`FaceMesh` 类** — 面网格 (triangle / quadrilateral)

| 成员 | 说明 |
|------|------|
| `gl_points` | `(n, 3) float32` 顶点坐标 |
| `gl_cells` | `(n*3,) uint32` 三角面索引（四边形被平展） |
| `gl_edges` | `(m*2,) uint32` 边索引（去重） |
| `gl_normal` | `(n, 3) float32` 每个顶点的法向量 |
| `gl_var` | `{name: (n, 3)}` 变量数据字典，前两列为 0，第三列为变量值 |

**`BodyMesh` 类** — 体网格 (tetrahedron / hexahedron)

与 FaceMesh 类似，额外有 `surface_mesh` 属性（用于渲染时自动提取边界面）。

### 7.2 `Utils/Mesh/MeshReader.py` — 网格文件读取

**`MeshReader(path)`** — 主入口函数，根据扩展名分发：

| 格式 | 读取器 | 返回类型 |
|------|--------|----------|
| `.off` | `read_off()` | FaceMesh 或 BodyMesh（自动判四面体/四边形） |
| `.dat` (Tecplot) | `read_dat()` | FaceMesh 或 BodyMesh（含 var 字段） |
| `.msh`, `.stl`, `.vtk` 等 | meshio | FaceMesh 或 BodyMesh |

**辅助函数：**
- `read_off(filepath)` — 手动解析 OFF 文件（meshio 对 OFF 支持有限）
- `read_dat(file)` — 解析 Tecplot DAT 格式

### 7.3 `Utils/Mesh/GeometryUtils.py` — 几何计算

| 函数 | 作用 |
|------|------|
| `determine_tetra_or_quad(points, cells)` | 通过混合积判断 4 顶点是共面（四边形）还是构成四面体 |
| `calculate_vertex_normals(vertices, faces)` | 基于面法向量加权平均计算顶点法向量 |
| `extract_edges(cells, cell_type)` | 从单元中提取唯一边（去重） |
| `extract_faces(cells, cell_type)` | 从体网格单元提取三角面（tetrahedron→4, hexahedron→6） |
| `get_faces_from_volume_mesh(cells, vertices)` | 从体网格提取边界面（只出现一次的面） |
| `check_point_order(face_vertices, reference_direction)` | 检查面顶点顺序是否与参考方向一致 |

### 7.4 `Utils/Mesh/MeshSplitter.py` — 网格切割

对四面体网格用任意平面 `ax+by+cz+d=0` 进行切割。

`MeshSplitter` 类：

| 函数 | 作用 |
|------|------|
| `split()` | 主入口：遍历四面体 → 按交点数量分三种情况处理 → 返回 A、B（两侧体网格）、C（切割面网格） |
| `split_tetrahedron(vertices, cells, plane, var)` | 对每个四面体判断与平面关系并拆分 |
| `split_tetrahedron_three(...)` | 处理三点交点情况 |
| `split_tetrahedron_four(...)` | 处理四点交点情况（四边形截面） |
| `computer_intersection_point(vertices, plane)` | 计算四面体各边与平面的交点 |
| `is_point_on_edge / is_point_on_face / is_line_segments_intersecting_3d` | 几何判定工具 |
| `decide_tetrahedron(vertices, plane)` | 判断四面体在平面哪一侧 |

### 7.5 `Utils/Compute/Interpolation.py` — 插值

| 函数 | 作用 |
|------|------|
| `barycentric_coordinates(p, p0, p1, p2, p3)` | 计算点 p 在四面体中的重心坐标 |
| `tetrahedral_lagrange_interpolation(...)` | 用重心坐标对四个顶点的 var 值做线性插值 |

用于网格切割时计算新交点的变量值。

### 7.6 `Utils/Config/path.py` — 项目路径

基于 `__file__` 向上 4 层定位项目根目录，导出一致路径：

| 变量 | 路径 |
|------|------|
| `project_dir` | 项目根目录 |
| `ui_dir` | `{root}/ui/` — Glade XML |
| `icon_dir` | `{root}/icon/` — 图标 |
| `solve_dir` | `{root}/src/Solve/` — 求解器 |

### 7.7 `Utils/Config/ReadYml.py` — YAML 配置

| 函数 | 作用 |
|------|------|
| `parse_yaml(path)` | 读取并解析 YAML 文件，返回 Python 字典 |

用于读取项目配置（如网格类型、变量列表等）。

### 7.8 `Utils/OpenGL/GLShader.py` — 着色器源码

| 变量 | 说明 |
|------|------|
| `vertex_src` | 主顶点着色器：旋转/平移/投影变换，光照参数计算，法向量和位置传递 |
| `fragment_src` | 主片段着色器：Phong 光照模型，支持 Face / Edge / Point / Gmsh / Var 五种渲染模式 |
| `axes_vertex_src` | 小坐标轴顶点着色器（支持字母不随旋转而旋转） |
| `axes_fragment_src` | 小坐标轴片段着色器（纯色输出） |

### 7.9 `Utils/OpenGL/GLTransformUtils.py` — 矩阵计算

| 函数 | 作用 |
|------|------|
| `set_perspective_matrix(fov, aspect_ratio, near_plane, far_plane)` | 构造透视投影矩阵 |
| `set_view_matrix(camera_position, target_position, up_vector)` | 构造 LookAt 观察矩阵 |

---

## 8. Shell 模块

### 8.1 `Shell/ShellCommand.py` — `CommandProcessor`

| 函数 | 作用 |
|------|------|
| `process_command(command)` | 分类命令：赋值 (`var = expr`) 或 `load()` 插件加载 |
| `process_variable(command)` | 正则匹配 `name = value` → `eval()` 求值 → 存入 `self.variables` |

`self.variables` 是一个 `{name: (value, type)}` 字典，供 box2 变量表显示。

---

## 9. C++ 插件

位于 `plugin/` 目录。通过 pybind11 编译为 `.so` Python 模块：

| 模块 | 说明 |
|------|------|
| `PY_DG_2D` | 二维 DG 求解器 (TriangleMesh, LinearDGSolver_2D_CycleBoundary) |
| `PY_DG_3D` | 三维 DG 求解器 (TetrahedronMesh, LinearDGSolver_3D_CycleBoundary) |
| `CE_3D` | 三维 BEM 求解器 (TriangleMesh, BEM_3DCESolver) |

各求解器遵循统一 Python 接口：
- `Mesh.read_off(path)` — 读取网格
- `Mesh.collect_edges() / collect_faces()` — 预处理
- `Solver.ComputeSingularIntegral()` — (BEM) 计算奇异积分
- `Solver.computeRHS(g)` — 设置边界条件
- `Solver.solve() / preconditionsolve() / computeTimeDiscretization(t)` — 执行求解
- `Solver.getRenderingData()` — 返回当前渲染数据（numpy 数组）

---

> 内部文档，维护者：项目开发团队
