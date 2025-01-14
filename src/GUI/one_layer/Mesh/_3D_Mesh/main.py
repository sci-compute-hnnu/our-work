import gmsh
import numpy as np
import gi
import meshio

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class _3DMeshWindow:

    def __init__(self):
        # 初始化 GTK Builder
        self.builder = Gtk.Builder()
        # 从 Glade 文件加载界面
        self.builder.add_from_file("../../ui/3D_mesh.glade")

        # 获取主窗口对象
        self.window = self.builder.get_object("window")
        self.window.connect("destroy", Gtk.main_quit)  # 确保程序退出时关闭主窗口

        # 获取按钮和其他控件
        self.cube_button = self.builder.get_object("cube_button")
        self.sphe_button = self.builder.get_object("sphe_button")
        self.other_button = self.builder.get_object("other_button")
        self.cu_x_entry = self.builder.get_object("cu_x")
        self.cu_y_entry = self.builder.get_object("cu_y")
        self.cu_z_entry = self.builder.get_object("cu_z")
        self.cu_dx_entry = self.builder.get_object("cu_dx")
        self.cu_dy_entry = self.builder.get_object("cu_dy")
        self.cu_dz_entry = self.builder.get_object("cu_dz")
        self.sphe_x_entry = self.builder.get_object("sphe_x")
        self.sphe_y_entry = self.builder.get_object("sphe_y")
        self.sphe_z_entry = self.builder.get_object("sphe_z")
        self.sphe_r_entry = self.builder.get_object("sphe_r")
        self.other_entry = self.builder.get_object("other_entry")
        self.other_entry1 = self.builder.get_object("other_entry1")
        self.algorithm = self.builder.get_object("algorithm")
        self.mesh_type = self.builder.get_object("mesh_type")
        self.size = self.builder.get_object("size")

        # 动态设置参数的堆叠容器
        self.para = self.builder.get_object("para")
        self.para_stack = Gtk.Stack()

        # 创建一个空白页面
        self.page_empty = Gtk.Box()  # 这是一个简单的空白页面

        # 获取界面的 Cube 和 Circle 页面
        self.page_cube = self.builder.get_object("Box")
        self.page_sphe = self.builder.get_object("Sphere")
        self.page_other = self.builder.get_object("other")

        # 将 Cube 和 Circle 页面添加到 Stack 中
        self.para_stack.add_named(self.page_empty, "empty")  # 添加首页空白区域页面
        self.para_stack.add_titled(self.page_other, "other", "other")
        self.para_stack.add_titled(self.page_sphe, "Sphere", "SPHERE")
        self.para_stack.add_titled(self.page_cube, "Box", "BOX")

        # 获取确定按钮和取消按钮
        self.confirm_button = self.builder.get_object("confirm_button")
        self.cancel_button = self.builder.get_object("cancel_button")

        # 连接按钮点击事件到相应的处理函数
        self.cube_button.connect("clicked", self.on_button_cube_clicked)
        self.sphe_button.connect("clicked", self.on_button_sphe_clicked)
        self.other_button.connect("clicked", self.on_button_other_clicked)
        self.confirm_button.connect("clicked", self.on_confirm_clicked)
        self.cancel_button.connect("clicked", self.on_cancel_clicked)

        # 将 Stack 添加到 para 容器中
        self.para.pack_start(self.para_stack, True, True, 0)

        # 初始页面设置
        self.para_stack.set_visible_child_name("empty")

        # 隐藏所有参数输入框
        self.hide_all_parameter_inputs()

    def hide_all_parameter_inputs(self):
        for widget in [self.page_cube, self.page_sphe, self.page_other]:
            widget.hide()

    def update_algorithm_options(self, combo_box, options, default_option):
        """
        更新 ComboBox 的选项及默认选项
        :param combo_box: 要更新的 ComboBox 控件
        :param options: 选项列表
        :param default_option: 默认选中的选项
        """
        # 清除现有模型
        combo_box.clear()
        liststore = Gtk.ListStore(str)
        for option in options:
            liststore.append([option])

        # 设置 ComboBox 的模型
        combo_box.set_model(liststore)

        # 创建 CellRendererText 对象并添加到 ComboBox
        renderer = Gtk.CellRendererText()
        combo_box.pack_start(renderer, True)
        combo_box.add_attribute(renderer, "text", 0)

        # 设置默认选项
        default_iter = liststore.get_iter_first()
        while default_iter is not None:
            if liststore.get_value(default_iter, 0) == default_option:
                break
            default_iter = liststore.iter_next(default_iter)
        if default_iter is not None:
            combo_box.set_active_iter(default_iter)

    def on_button_cube_clicked(self, button):
        # 切换到 Circle 页面并更新选项
        self.hide_all_parameter_inputs()
        self.page_cube.show()
        self.para_stack.set_visible_child_name("Box")
        self.update_algorithm_options(self.algorithm, [
            "1：MeshAdapt",
            "3：Initial mesh only",
            "4：Frontal",
            "7：MMG3D",
            "9：R-tree",
            "10:HXT"
        ], "1：MeshAdapt")
        self.update_algorithm_options(self.mesh_type, [
            "2:Surface",
            "3:Volume"
        ], "Volume")

    def on_button_sphe_clicked(self, button):
        # 切换到 Rectangle 页面并更新选项
        self.hide_all_parameter_inputs()
        self.page_sphe.show()
        self.para_stack.set_visible_child_name("Sphere")
        self.update_algorithm_options(self.algorithm, [
            "1：MeshAdapt",
            "3：Initial mesh only",
            "4：Frontal",
            "7：MMG3D",
            "9：R-tree",
            "10:HXT"
        ], "1：MeshAdapt")

        self.update_algorithm_options(self.mesh_type, [
            "2:Surface",
            "3:Volume"
        ], "Volume")

    def on_button_other_clicked(self, button):
        # 切换到 other 页面并更新选项
        self.hide_all_parameter_inputs()
        self.page_other.show()
        self.para_stack.set_visible_child_name("other")
        self.update_algorithm_options(self.algorithm, [
            "1：MeshAdapt",
            "3：Initial mesh only",
            "4：Frontal",
            "7：MMG3D",
            "9：R-tree",
            "10:HXT"
        ], "1：MeshAdapt")
        self.update_algorithm_options(self.mesh_type, [
            "2:Surface",
            "3:Volume"
        ], "Volume")


    def on_confirm_clicked(self, button):
        # 获取当前页面
        current_page = self.para_stack.get_visible_child_name()
        model = self.algorithm.get_model()
        # 所选中的算法
        algorithm_selected = self.algorithm.get_active_iter()
        algorithm = model.get_value(algorithm_selected, 0).split("：")[0]
        # 获取网格类型
        type_selected = self.mesh_type.get_active_iter()
        type_value = model.get_value(algorithm_selected, 0).split("：")[0]

        # 获取网格尺寸
        size_value = float(self.size.get_text())

        # 根据当前页面获取相应的 Entry
        if current_page == "Box":
            entries = [
                self.cu_x_entry, self.cu_y_entry, self.cu_z_entry,
                self.cu_dx_entry, self.cu_dy_entry, self.cu_dz_entry
            ]
            shape = ["box"] + [float(entry.get_text()) for entry in entries]
        elif current_page == "Sphere":
            entries = [
                self.sphe_x_entry, self.sphe_y_entry, self.sphe_z_entry,
                self.sphe_r_entry
            ]
            shape = ["sphere"] + [float(entry.get_text()) for entry in entries]
        elif current_page == "other":

            other_points = eval(self.other_entry.get_text())
            other_faces = eval(self.other_entry1.get_text())
            shape = ["other", other_points , other_faces]
        else:
            shape = None

        # 调用 generate_mesh 方法
        if shape:
            self.generate_mesh(shape, size_value, algorithm, type_value)
            node_tags, node_coords, _ = gmsh.model.mesh.getNodes()

            # 将节点坐标转换为 NumPy 数组
            points = np.array(node_coords).reshape(-1, 3)

            # 计算和打印统计信息
            num_points = points.shape[0]

            # 获取元素数据
            element_tags, element_types, element_nodes = gmsh.model.mesh.getElements()

            # 计算元素总数
            total_elements = sum(len(nodes) for nodes in element_nodes)
            # 打印
            info = f"Mesh generated with:\n {num_points} points \n {total_elements} cells\n Algorithm: \n {algorithm}"
            print(info)
            gmsh.finalize()
            # # 打印网格信息
            # elementType = 'triangle'
            # featureEdge = 'line'
            # meshio_mesh = meshio.Mesh(points=mesh.points, cells={elementType: mesh.cells_dict[elementType]})
            # line = meshio.Mesh(points=mesh.points, cells=[(featureEdge, mesh.cells_dict[featureEdge])])
            #
            # nodeNumber = meshio_mesh.points.shape[0]
            # elementNumber = meshio_mesh.cells_dict[elementType].shape[0]
            # info = f"Mesh generated with:\n {nodeNumber} points \n {elementNumber} cells \n Algorithm: \n {algorithm}"
            # info = f"Mesh generated with:\n {len(mesh.points)} points \n  {len(mesh.cells)} cells \nAlgorithm:\n{algorithm}"
            # buffer = self.information_textview.get_buffer()
            # buffer.set_text(info)

            # 这里可以添加进一步处理网格的代码，例如保存或可视化

    def generate_mesh(self, shape, mesh_size, algorithm, mesh_type):
        gmsh.initialize()
        gmsh.model.add("model")
        if shape[0] == "box":
            gmsh.model.occ.addBox(shape[1],  shape[2], shape[3] , shape[4], shape[5], shape[6])
        elif shape[0] == "sphere":
            gmsh.model.occ.addSphere(shape[1], shape[2], shape[3], shape[4])
        elif shape[0] == "other":
            # 定义点和面
            point = shape[1]
            face = shape[2]

            # 添加点
            points = [gmsh.model.occ.addPoint(*pt, mesh_size) for pt in point]

            # 创建一个存储线段的字典
            lines_dict = {}
            lines = []

            # 添加线段
            def add_line(p1, p2):
                if (p1, p2) not in lines_dict and (p2, p1) not in lines_dict:
                    line_id = gmsh.model.occ.addLine(p1, p2)
                    lines_dict[(p1, p2)] = line_id
                    lines_dict[(p2, p1)] = line_id
                    return line_id
                return lines_dict.get((p1, p2)) or lines_dict.get((p2, p1))

            for f in face:
                for i in range(len(f)):
                    p1 = f[i]
                    p2 = f[(i + 1) % len(f)]
                    add_line(p1, p2)

            # 根据存储的线段定义线环
            def get_curve_loop(vertex_ids):
                loop_lines = []
                for i in range(len(vertex_ids)):
                    p1 = vertex_ids[i]
                    p2 = vertex_ids[(i + 1) % len(vertex_ids)]
                    line_id = lines_dict.get((p1, p2)) or lines_dict.get((p2, p1))
                    if line_id is not None:
                        loop_lines.append(line_id)
                    else:
                        raise ValueError(f"Line segment ({p1}, {p2}) not found in lines_dict.")
                return gmsh.model.occ.addCurveLoop(loop_lines)

            # 生成面环（face loops）
            def generate_face_loops(faces):
                face_loops = []
                for face in faces:
                    face_loop = get_curve_loop(face)
                    face_loops.append(face_loop)
                return face_loops

            # 计算面环
            face_loops = generate_face_loops(face)

            # 添加面
            faces = [gmsh.model.occ.addPlaneSurface([loop]) for loop in face_loops]

            # 创建体
            surface_loop = gmsh.model.occ.addSurfaceLoop(faces)
            gmsh.model.occ.addVolume([surface_loop])

        # 同步几何模型
        gmsh.model.occ.synchronize()
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), mesh_size)
        gmsh.option.setNumber("Mesh.Algorithm3D", int(algorithm))
        gmsh.model.mesh.generate(int(mesh_type))


    def on_cancel_clicked(self, button):
        # 获取当前页面
        current_page = self.para_stack.get_visible_child_name()

        # 根据当前页面清空相应的 Entry
        if current_page == "Box":
            entries = [
                self.cu_x_entry, self.cu_y_entry, self.cu_z_entry,
                self.cu_dx_entry, self.cu_dy_entry, self.cu_dz_entry
            ]
        elif current_page == "Sphere":
            entries = [
                self.sphe_x_entry, self.sphe_y_entry, self.sphe_z_entry,
                self.sphe_r_entry
            ]
        elif current_page == "other":
            self.other_entry.set_text("")

        # 清空 Entry 中的内容
        self.clear_entries(entries)

    def clear_entries(self, entries):
        """
        清空 Entry 中的内容
        :param entries: 要清空的 Entry 列表
        """
        for entry in entries:
            entry.set_text("")

    def run(self):
        # 显示主窗口并启动 GTK 主循环
        self.window.show_all()
        Gtk.main()


# 创建 UI 实例并运行
if __name__ == "__main__":
    win = _3DMeshWindow()
    win.run()
