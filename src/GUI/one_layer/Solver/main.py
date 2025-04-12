import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gtk, Gdk

import sys
import os
import importlib.util
import numpy as np

from Utils.Connector.SolverViewBoxConn import SolverViewBoxConn

from Utils.Config.path import solve_dir

class SolverWindow:

    def __init__(self, glade_path, box1, notebook, two_layer, three_layer):

        self.builder = Gtk.Builder()
        self.builder.add_from_file(glade_path)

        self.window = self.builder.get_object("solver_windows")

        # 边值函数的输入类型
        self.bc_input_type_list = ['file', 'pyfunc']

        # 其他需要使用的部件
        self.box1 = box1
        self.notebook = notebook
        self.two_layer = two_layer
        self.three_layer = three_layer

        # 关闭窗口 销毁界面
        self.window.connect("destroy", Gtk.main_quit)

        # "选择网格"combobox
        self.mesh_combobox = self.builder.get_object("select_mesh")
        # "选择绘制窗口"combobox
        self.draw_combobox = self.builder.get_object("select_draw")
        # "选择变量"combobox
        self.var_combobox = self.builder.get_object("select_var")
        # "选择变量"combobox
        self.ele_combobox = self.builder.get_object("select_ele")


        # 相关参数box
        self.para_box = self.builder.get_object("para_box")
        # 刷新频率
        self.freq_spin = self.builder.get_object("freq_spin")
        # 总时间
        self.all_time_spin = self.builder.get_object("time_spin")
        # 开始按钮
        self.start_button = self.builder.get_object('start_button')

        # 美化
        self.beautify_win()

        # 求解器名字标签
        self.solver_name = self.builder.get_object("solver_name")
        # 求解器名字选择框
        self.solver_name_combobox = self.builder.get_object("solver_name_combobox")
        self.solver_name_combobox.connect("changed", self.on_selection_changed)
        # 边界条件放置框
        self.bc_box = self.builder.get_object("bc_box")
        # 边界条件文件选择框
        self.bc_box_file = self.builder.get_object('bc_box_'+self.bc_input_type_list[0])
        parent = self.bc_box_file.get_parent()
        parent.remove(self.bc_box_file)
        # 边界条件输入选择框
        self.bc_box_pyfunc = self.builder.get_object('bc_box_'+self.bc_input_type_list[1])
        parent = self.bc_box_pyfunc.get_parent()
        parent.remove(self.bc_box_pyfunc)

        # 创建网格选择下拉框
        mesh_list = self.get_current_mesh()
        self.load_store_on_combobox(self.mesh_combobox, mesh_list)

        # 创建绘制窗口选择下拉框
        draw_list = ["current viewbox"]
        self.load_store_on_combobox(self.draw_combobox, draw_list)

        # 设置刷新频率freq_spin参数
        adjustment1 = self.freq_spin.get_adjustment()
        adjustment1.set_lower(0)  # 下界
        adjustment1.set_upper(100.0)  # 上界
        adjustment1.set_step_increment(0.1)  # 步长
        self.freq_spin.set_digits(1) # 小数点后1位
        self.freq_spin.set_value(0.1)  # 设置默认0.1s

        # 设置总时间time_spin参数
        adjustment2 = self.all_time_spin.get_adjustment()
        adjustment2.set_lower(0)  # 下界
        adjustment2.set_upper(100.0)  # 上界
        adjustment2.set_step_increment(1)  # 步长
        self.freq_spin.set_digits(1) # 小数点后1位
        self.all_time_spin.set_value(30.0)  # 设置默认30.0s


        # 选择的求解器
        self.docking_solver = None
        # 连接器
        self.Connector = SolverViewBoxConn()
        # 选择的网格
        self.selectedMeshClass = None


        self.start_button.connect("clicked", self.start_)

    def run(self):

        self.window.show_all()
        Gtk.main()


    def beautify_win(self):

        """ 设置参数框底色 """
        # 为para_box设置 ID
        self.para_box.set_name("para_box")
        # 加载内联CSS样式
        css = """
        #para_box {
            background-color: #d3d3d3; /* 设置 para_box 为浅灰色 */
        }
        """

        # 创建CSS提供者并加载内联 CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode('utf-8'))

        # 将 CSS 提供者应用到屏幕
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


    # 获取求解器
    def get_solvers_folder_name(self):

        # 二维求解器目录
        solve2d_dir = solve_dir+'/Solver_2D'
        # 列出指定路径下的所有项目
        items = os.listdir(solve2d_dir)
        # 过滤出文件夹
        folder2d_names = [item for item in items if os.path.isdir(os.path.join(solve2d_dir, item))]

        # 三维求解器目录
        solve3d_dir = solve_dir+'/Solver_3D'
        # 列出指定路径下的所有项目
        items = os.listdir(solve3d_dir)
        # 过滤出文件夹
        folder3d_names = [item for item in items if os.path.isdir(os.path.join(solve3d_dir, item))]

        return folder2d_names, folder3d_names

    def get_docking_solver(self, file_path):
        """
        从指定的 Python 文件加载 DockingSolver 类并实例化。

        :param file_path: Python 文件的路径，例如 "/sdas/sads/aasd/win.py"
        :return: DockingSolver 类的实例
        """
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"无法加载模块: {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, "DockingSolver"):
            raise AttributeError(f"模块 {module_name} 中未找到类 'DockingSolver'")

        docking_solver_class = getattr(module, "DockingSolver")
        if not callable(docking_solver_class):
            raise TypeError(f"'DockingSolver' 不是一个可调用的类")

        return docking_solver_class()  # 实例化并返回



    # 将求解器文件夹名添加至combobox
    def populate_combobox_and_bind(self, namelist):

        for name in namelist:
            self.solver_name_combobox.append_text(name)

        dimstr = '二维' if self.dim == 2 else '三维'

        if namelist:
            self.solver_name_combobox.set_active(-1)  # 默认选中第一个选项
            self.solver_name.set_text(f"请选择{dimstr}求解器")  # 初始化 Label 显示内容


    def get_bc_box(self, choice):

        if choice == None:
            return None

        bc_box = None
        if choice == self.bc_input_type_list[0]:  # 当边值条件输入类型为文件时
            bc_box = self.bc_box_file
            self.bc_file = self.builder.get_object("bc_file")  # 获取边值函数文件按钮

        elif choice == self.bc_input_type_list[1]:  # 当边值条件输入类型为python函数时
            bc_box = self.bc_box_pyfunc
            self.bc_entry = self.builder.get_object("bc_entry")  # 获取边值函数输入框
            combobox_BEM = self.builder.get_object("bc_combobox")
            combobox_BEM.remove_all()  # 先清空所有选项
            if self.docking_solver.bc_pyfunc_default:  # 如果提前设置了默认的待加载边值函数
                for option in self.docking_solver.bc_pyfunc_default:
                    combobox_BEM.append_text(option)  # 设置待加载边值函数表达式

        return bc_box


    def set_bc_box(self, choice):

        # 先移除 bc_box 里的所有子组件
        for child in self.bc_box.get_children():
            self.bc_box.remove(child)

        # 获取边值条件方案
        bc_input = self.get_bc_box(choice)
        if bc_input is None:
            return

        self.bc_box.pack_start(bc_input, True, True, 0)


    def on_selection_changed(self, widget):

        # 构建求解器
        folder_dim = '/Solver_2D/' if self.dim == 2 else '/Solver_3D/'
        selected_text = widget.get_active_text()
        solver_path = solve_dir + folder_dim + selected_text + '/DockingSolver.py'
        solver = self.get_docking_solver(solver_path)
        self.docking_solver = solver

        if all([
            solver.name is None,
            solver.cell_type is None,
            solver.data_location is None,
            solver.bc_input_type is None,
            solver.var is None
        ]):
            raise ValueError("DockingSolver信息不完全")

        # 加载信息
        # 1. 求解器名字
        self.solver_name.set_text(solver.name)
        # 2. 边值条件框
        self.set_bc_box(solver.bc_input_type)
        # 3. 变量名框
        self.load_store_on_combobox(self.var_combobox, solver.var)
        # 4. 绘制方式框
        self.load_store_on_combobox(self.ele_combobox, solver.data_location)



    # 在选择框中加载内容
    def load_store_on_combobox(self, combobox, content):

        # 先移除所有已存在的 CellRenderer
        for renderer in combobox.get_cells():
            combobox.clear()  # 清空所有列（包括 renderer）

        # 先清空 combobox 之前的内容
        combobox.set_model(None)

        if isinstance(content, str):
            content = [content]

        store = Gtk.ListStore(str)
        for item in content:
            store.append([item])

        renderer = Gtk.CellRendererText()
        combobox.pack_start(renderer, True)
        combobox.add_attribute(renderer, "text", 0)
        combobox.set_model(store)

        # 设置默认选中第一项（如果列表不为空）
        if len(content) > 0:
            combobox.set_active(0)



    # 获取当前box1中的网格名
    def get_current_mesh(self):

        meshnamelist = []
        for item in self.box1.list_store:
            value = list(item)  # 获取当前条目的值 [bool, str]
            meshName = value[1]  # 获取网格名字
            meshnamelist.append(meshName)  # 将网格加载至draw_store

        return meshnamelist


    # 获取当前tag标签页的viewbox
    def get_current_tag_viewbox(self):

        pass


    # 从combobox中获取选项
    def get_opt_from_combobox(self, combobox):

        opt = None
        tree_iter = combobox.get_active_iter()
        if tree_iter is not None:
            model = combobox.get_model()
            value = model[tree_iter][0]  # 获取当前选中项的网格
            opt = value
        return opt


    # 执行pyfunc（边界条件）
    def execute_pyfunc(self, pyfunc_str):

        local_dict = {}
        # 将字符串转化为函数
        exec(f"def g(x): return {pyfunc_str}", globals(), local_dict)  # local_dict['g'] 函数对象
        g = local_dict['g']
        return g


    # 点击开始按钮
    def start_(self, button):

        """step0  获取相关参数"""
        # 获取所选网格的名字
        currentMeshName = self.get_opt_from_combobox(self.mesh_combobox)

        # 获取渲染变量
        draw_var = self.get_opt_from_combobox(self.var_combobox)

        # 获取刷新频率
        freq = float(self.freq_spin.get_value())
        # 获取总时间
        all_time = float(self.all_time_spin.get_value())

        """step1  来到box1中查找网格"""
        for index, item in enumerate(self.box1.list_store):
            value = list(item)  # 获取当前条目的值 [bool, str]
            meshName = value[1]  # 获取网格名字

            # 检查是否匹配
            if currentMeshName == meshName:
                self.selectedMeshClass = self.box1.MeshList[index]  # 获取当前的索引
                self.notebook.showbox.should_draw = index   # 更新should_draw
                break

        """step2  设置three_layer的var_combobox"""
        self.three_layer.setup_combobox(0, ['Neutral Mode']+self.docking_solver.var, draw_var)

        """step3  加载渲染连接器"""
        self.Connector.load_fit(self.notebook.showbox, self.selectedMeshClass, self.two_layer.timer_entry, self.box1, freq, all_time)

        """step4  准备传入参数"""
        fixed_params = {}  # 固定的输入参数 如边界条件
        optional_args = ()  # 用户可自行选择的输入参数

        # 文件地址
        fixed_params['mesh_path'] = self.selectedMeshClass.file_path

        # 边值条件
        boundary_conditions = None
        if self.docking_solver.bc_input_type == self.bc_input_type_list[0]:  # 边值条件输入方式为文件
            boundary_conditions = self.bc_file.get_filename()  # 边值条件是文件

        elif self.docking_solver.bc_input_type == self.bc_input_type_list[1]:  # 边值条件输入方式为python函数
            bc_pyfunc = self.bc_entry.get_text()
            boundary_conditions = self.execute_pyfunc(bc_pyfunc)  # 边值条件是函数表达式
        fixed_params['bc'] = boundary_conditions


        """关闭窗口"""""
        self.window.destroy()

        # 加载求解器(初始化)
        self.Connector.load_solver(self.docking_solver)

        self.Connector.detectorWithRealTime(*optional_args, **fixed_params)
