import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from Pre.MeshGeneration import _2D_generate_mesh, _2D_generate_stru_mesh
from Utils.Mesh.MeshClass import FaceMesh
from Utils.Config.path import ui_dir
from Utils.Config.path import icon_dir


class _2DMeshWindow:

    def __init__(self):

        # 初始化 GTK Builder
        self.builder = Gtk.Builder()
        # 从 Glade 文件加载界面
        self.builder.add_from_file(ui_dir+'2D_mesh.glade')

        # 获取主窗口对象
        self.window = self.builder.get_object("window")
        self.window.connect("destroy", Gtk.main_quit)  # 确保程序退出时关闭主窗口

        # 获取按钮和其他控件
        self.cir_button = self.builder.get_object("cir_button")
        self.rec_button = self.builder.get_object("rec_button")
        self.other_button = self.builder.get_object("other_button")
        self.rec_x_entry = self.builder.get_object("rec_x")
        self.rec_y_entry = self.builder.get_object("rec_y")
        self.rec_z_entry = self.builder.get_object("rec_z")
        self.rec_dx_entry = self.builder.get_object("rec_dx")
        self.rec_dy_entry = self.builder.get_object("rec_dy")
        self.cir_x_entry = self.builder.get_object("cir_x")
        self.cir_y_entry = self.builder.get_object("cir_y")
        self.cir_z_entry = self.builder.get_object("cir_z")
        self.cir_r_entry = self.builder.get_object("cir_r")
        self.other_entry = self.builder.get_object("other_entry")
        self.algorithm = self.builder.get_object("algorithm")
        self.size = self.builder.get_object("size")
        self.mesh_name_entry = self.builder.get_object("mesh_name")
        self.structured_mesh = self.builder.get_object("structured_mesh")
        self.direction = self.builder.get_object("direction")
        self.selection = self.builder.get_object("selection")
        self.selection.hide()


        # 动态设置参数的堆叠容器
        self.para = self.builder.get_object("para")
        self.para_stack = Gtk.Stack()

        # 创建一个空白页面
        self.page_empty = Gtk.Box()  # 这是一个简单的空白页面

        # 获取界面的 Cube 和 Circle 页面
        self.page_cir = self.builder.get_object("Circle")
        self.page_rec = self.builder.get_object("Rectangle")
        self.page_other = self.builder.get_object("other")

        # 将 Cube 和 Circle 页面添加到 Stack 中
        self.para_stack.add_named(self.page_empty, "empty")  # 添加首页空白区域页面
        self.para_stack.add_titled(self.page_other, "other", "other")
        self.para_stack.add_titled(self.page_cir, "Circle", "CIRCLE")
        self.para_stack.add_titled(self.page_rec, "Rectangle", "RECTANGLE")

        # 获取确定按钮和取消按钮
        self.confirm_button = self.builder.get_object("confirm_button")
        self.cancel_button = self.builder.get_object("cancel_button")

        # 连接按钮点击事件到相应的处理函数
        self.cir_button.connect("clicked", self.on_button_cir_clicked)
        self.rec_button.connect("clicked", self.on_button_rec_clicked)
        self.other_button.connect("clicked", self.on_button_other_clicked)
        self.confirm_button.connect("clicked", self.on_confirm_clicked)
        self.cancel_button.connect("clicked", self.on_cancel_clicked)
        self.structured_mesh.connect("toggled", self.on_structured_mesh_toggled)

        # 将 Stack 添加到 para 容器中
        self.para.pack_start(self.para_stack, True, True, 0)

        # 初始页面设置
        self.para_stack.set_visible_child_name("empty")
        # 加载窗口icon
        self.load_icon()

        # 隐藏所有参数输入框
        self.selection.hide()
        self.hide_all_parameter_inputs()


        # box1
        self.box1 = None


    # 加载需要使用的部件
    def loadWidget(self, box1):
        self.box1 = box1


    def load_icon(self):

        _2d_dir = icon_dir + '/2DMesh/'
        icon_names = ['circle.png', 'rectangle.png', 'other.png']
        widgets = ['cir_image', 'rec_image', 'other_image']
        icons = {name: self.builder.get_object(name) for name in widgets}
        for widget, icon_name in zip(widgets, icon_names):
            icons[widget].set_from_file(_2d_dir + icon_name)



    # 隐藏参数
    def hide_all_parameter_inputs(self):
        for widget in [self.page_cir, self.page_rec, self.page_other]:
            widget.hide()

    # 检测是否生成结构网格
    def on_structured_mesh_toggled(self, button):
        if button.get_active():
            # 如果勾选，显示Direction网格
            self.selection.show()
            self.update_options(self.direction, [
                "Left",
                "Right"
            ], "Left")
        else:
            # 如果未勾选，隐藏Direction网格
            self.selection.hide()

    # 更新选项
    def update_options(self, combo_box, options, default_option):
        combo_box.clear()
        liststore = Gtk.ListStore(str)
        for option in options:
            liststore.append([option])

        combo_box.set_model(liststore)
        renderer = Gtk.CellRendererText()
        combo_box.pack_start(renderer, True)
        combo_box.add_attribute(renderer, "text", 0)

        default_iter = liststore.get_iter_first()
        while default_iter is not None:
            if liststore.get_value(default_iter, 0) == default_option:
                break
            default_iter = liststore.iter_next(default_iter)
        if default_iter is not None:
            combo_box.set_active_iter(default_iter)

    def update_mesh_name(self, shape_type):
        """确认Mesh name框中的默认名字字符串"""
        existing_names = [row[1] for row in self.box1.list_store]
        count = 1
        while f"{shape_type}{count}" in existing_names:
            count += 1
        self.mesh_name_entry.set_text(f"{shape_type}{count}")

    def on_button_cir_clicked(self, button):
        self.hide_all_parameter_inputs()
        self.page_cir.show()
        self.para_stack.set_visible_child_name("Circle")
        self.update_options(self.algorithm, [
            "1：MeshAdapt",
            "2：Automatic",
            "3：Initial mesh only",
            "5：Delaunay",
            "6：Frontal-Delaunay",
            "7：BAMG",
            "8：Frontal-Delaunay for Quads",
            "9：Packing of Parallelograms",
            "11：Quasi-structured Quad"
        ], "6：Frontal-Delaunay")
        self.update_mesh_name("circle")

    def on_button_rec_clicked(self, button):
        self.hide_all_parameter_inputs()
        self.page_rec.show()
        self.para_stack.set_visible_child_name("Rectangle")
        self.update_options(self.algorithm, [
            "1：MeshAdapt",
            "2：Automatic",
            "3：Initial mesh only",
            "5：Delaunay",
            "6：Frontal-Delaunay",
            "7：BAMG",
            "8：Frontal-Delaunay for Quads",
            "9：Packing of Parallelograms",
            "11：Quasi-structured Quad"
        ], "6：Frontal-Delaunay")
        self.update_mesh_name("rectangle")

    def on_button_other_clicked(self, button):
        self.hide_all_parameter_inputs()
        self.page_other.show()
        self.para_stack.set_visible_child_name("other")
        self.update_options(self.algorithm, [
            "1：MeshAdapt",
            "2：Automatic",
            "3：Initial mesh only",
            "5：Delaunay",
            "6：Frontal-Delaunay",
            "7：BAMG",
            "8：Frontal-Delaunay for Quads",
            "9：Packing of Parallelograms",
            "11：Quasi-structured Quad"
        ], "6：Frontal-Delaunay")
        self.update_mesh_name("other")



    def on_confirm_clicked(self, button):

        """step0. 获取Mesh name框中的名字"""
        mesh_name = self.mesh_name_entry.get_text()

        """step1. 获取当前界面的绘制信息"""
        current_page = self.para_stack.get_visible_child_name()
        model = self.algorithm.get_model()
        algorithm_selected = self.algorithm.get_active_iter()

        algorithm = model.get_value(algorithm_selected, 0).split("：")[0]
        algorithmcontent = model.get_value(algorithm_selected, 0).split("：")[1]
        size_value = float(self.size.get_text())

        if self.structured_mesh.get_active():
            direction_selected = str(self.direction.get_active_iter())
        else:
            direction_selected = ''

        if current_page == "Circle":
            entries = [
                self.cir_x_entry, self.cir_y_entry, self.cir_z_entry,
                self.cir_r_entry
            ]
            shape = ["circle"] + [float(entry.get_text()) for entry in entries]
        elif current_page == "Rectangle":
            entries = [
                self.rec_x_entry, self.rec_y_entry, self.rec_z_entry,
                self.rec_dx_entry, self.rec_dy_entry
            ]
            shape = ["rectangle"] + [float(entry.get_text()) for entry in entries]
        elif current_page == "other":
            other_points = eval(self.other_entry.get_text())
            shape = ["other", other_points]
        else:
            shape = None

        """step2. 调用gmsh算法 生成网格"""
        if shape:
            if direction_selected == '' :
                mesh = _2D_generate_mesh(shape, size_value, algorithm, direction_selected)
            else:
                mesh = _2D_generate_stru_mesh(shape, size_value, direction_selected)

            """step3. 设置information框输出信息"""
            elementType = 'triangle'
            points = mesh.points
            cells = mesh.cells_dict[elementType]

            pointNumber = points.shape[0]
            cellNumber = cells.shape[0]

            info = f"Mesh generated with:\n type: {current_page} \n points: {pointNumber}  \n cells: {cellNumber} \n " \
                   f"Algorithm: {algorithmcontent} \n \n"

            self.box1.info_print(info)

            """step4. 构建meshClass并载入box1"""

            meshWithGL = FaceMesh(points, cells, 'triangle')

            self.box1.load_Mesh(meshWithGL, name=mesh_name)

            """step5. 关闭窗口"""
            self.window.close()


    # 点击取消按钮
    def on_cancel_clicked(self, button):
        current_page = self.para_stack.get_visible_child_name()
        if current_page == "Circle":
            entries = [
                self.cir_x_entry, self.cir_y_entry, self.cir_z_entry,
                self.cir_r_entry
            ]
        elif current_page == "Rectangle":
            entries = [
                self.rec_x_entry, self.rec_y_entry, self.rec_z_entry,
                self.rec_dx_entry, self.rec_dy_entry
            ]
        elif current_page == "other":
            self.other_entry.set_text("")

        self.clear_entries(entries)

    def clear_entries(self, entries):
        for entry in entries:
            entry.set_text("")

    def run(self):
        self.window.show_all()
        Gtk.main()

if __name__ == "__main__":
    win = _2DMeshWindow()
    win.run()