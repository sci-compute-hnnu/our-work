import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


from GUI.box0.paned0.paned1.paned2.notebook.top_box_of_every_type import top_box_of_every_type


class data_box():

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../../ui/data_box.glade")

        # temp_top_box
        self.temp_top_box = self.builder.get_object("temp_top_box")

        # 将topbox从父类顶层部件中移除
        parent_container = self.temp_top_box.get_parent()
        parent_container.remove(self.temp_top_box)

        # 创建top_box 和 blue_edge_box
        self.top_box_class = top_box_of_every_type()
        self.top_box = self.top_box_class.top_box
        self.blue_edge_box = self.top_box_class.blue_edge_box

        # top_box的第一排的三个按钮
        self.horizontal = self.top_box_class.horizontal
        self.vertical = self.top_box_class.vertical
        self.close_box_button = self.top_box_class.close_box_button

        # 将temp_top_box放置于top_box
        self.top_box.pack_start(self.temp_top_box, True, True, 0)

        # 展示数据的box
        self.show_data_box = self.builder.get_object("data_box")

        # 初始化list_store的状态（先初始化为20个Fales(默认不超过20个False) 后续点击状态栏按钮时会更新）
        self.list_store_state = [False for _ in range(20)]


        """ 三个按钮 """
        # 显示所有网格文件列表的按钮
        self.showing_combobox = self.builder.get_object("showing")
        # 显示某个网格文件数据类型(点 单元)的按钮
        self.attribute_combobox = self.builder.get_object("attribute")
        # 保留小数位数的按钮
        self.precision_spinbox = self.builder.get_object("precision")

        # 网格
        self.mesh = None

        self.data = None
        self.name = None

        '''显示数据'''
        # 创建包含点集的数据模型的 ListStore，为了保留对应小数位数
        self.liststore = Gtk.ListStore(int, str, str, str)
        # 创建 TreeView，并且设置模型
        self.treeview = Gtk.TreeView()
        # 为 TreeView 设置 CSS 类，以便可以通过 CSS 定制
        self.treeview.set_name('treeview-grid-lines')
        # 应用css
        apply_css(self.treeview)
        # 设置网格线
        self.treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)  # 添加水平和垂直网格线
        # 创建box
        self.box_fixed = Gtk.Box()
        self.box_fixed.add(self.treeview)

        # 创建一个 ScrolledWindow 用于包裹 TreeView
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.box_fixed)
        self.show_data_box.pack_start(self.scrolled_window, True, True, 0)


        '''showing_combobox'''
        self.liststore1 = Gtk.ListStore(str)

        # 向 liststore1 中添加网格文件名的信息
        # self.update_mesh_data(list_store)

        self.showing_combobox.set_model(self.liststore1)
        # 显示选项
        cell = Gtk.CellRendererText()
        self.showing_combobox.pack_start(cell, True)
        self.showing_combobox.add_attribute(cell, "text", 0)



        '''attribute_combobox'''
        # 创建 ListStore 并添加数据
        self.liststore2 = Gtk.ListStore(str)
        self.liststore2.append(["Points"])
        self.liststore2.append(["Cells"])
        self.attribute_combobox.set_model(self.liststore2)
        self.attribute_combobox.set_active(0)  # 设置默认选中项
        #显示选项
        cell = Gtk.CellRendererText()
        self.attribute_combobox.pack_start(cell, True)
        self.attribute_combobox.add_attribute(cell, "text", 0)  


        '''precision_spinbox'''
        #步长为1 0-20
        self.precision_spinbox.set_range(0, 20)
        self.precision_spinbox.set_increments(1, 0)
        #默认保留两位
        self.precision_spinbox.set_value(2)



    # 更新网格文件列表
    def update_mesh_data(self, list_store):

        for row in list_store:
            # row 是一个包含两个元素的元组，第一个元素是bool值，第二个元素是网格的名字
            mesh_name = row[1]  # 获取网格名字列的文本
            mesh_name = [str(mesh_name)]

            self.liststore1.append(mesh_name)  # 添加到列表中



    # 读取文件点集并更新treeview
    def data_list(self):

        self.data = self.mesh.points

        # 更新绘制
        self.update_treeview()

    def cell_list(self):

        if self.mesh.type == 3:     # 如果是三角形
            self.data = int(self.mesh.ntriangle / 3)
            self.name = 'triangle'
        elif self.mesh.type == 4:     # 如果是四边形
            self.data = int(self.mesh.nquadrilateral / 4)
            self.name = 'quad'

        # 更新绘制
        self.update_treeview_cell()


    """ 更新面索引数据 """
    def update_treeview_cell(self):
        liststore = Gtk.ListStore(int, int, str)
        for i in range(self.data):
            type = self.name
            liststore.append([i, i, type])
            self.treeview.set_model(liststore)
        self.addcell_columns_to_treeview()

    def addcell_columns_to_treeview(self):

        # 确保清除所有已有列
        for column in self.treeview.get_columns():
            self.treeview.remove_column(column)
        # 创建列和单元格渲染器
        renderer_number = Gtk.CellRendererText()
        renderer_number.set_padding(6, 10)  # 初始值为 (10, 10)，现在设置为 (6, 10)
        column_text0 = Gtk.TreeViewColumn("Num", renderer_number, text=0)

        renderer_text = Gtk.CellRendererText()
        renderer_text.set_padding(6, 10)  # 初始值为 (10, 10)，现在设置为 (6, 10)
        column_text1 = Gtk.TreeViewColumn("Cell ID", renderer_text, text=1)

        renderer_number = Gtk.CellRendererText()
        renderer_number.set_padding(6, 10)  # 初始值为 (10, 10)，现在设置为 (6, 10)
        column_text2 = Gtk.TreeViewColumn("Cell Type", renderer_number, text=2)

        column_text0.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_text0.set_fixed_width(60)  # 设定想要的宽度

        column_text1.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_text1.set_fixed_width(150)  # 设定想要的宽度

        column_text2.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_text2.set_fixed_width(150)  # 设定想要的宽度

        self.treeview.append_column(column_text0)
        self.treeview.append_column(column_text1)
        self.treeview.append_column(column_text2)

        # 重新绘制 TreeView
        self.treeview.show_all()


    """ 更新点坐标数据 """
    def update_treeview(self):
        for i, line in enumerate(self.data, 1):
            x = "{:.2f}".format(line[0])  # 将第一个 float 数保留两位小数
            y = "{:.2f}".format(line[1])  # 将第二个 float 数保留两位小数
            z = "{:.2f}".format(line[2])  # 将第三个 float 数保留两位小数
            self.liststore.append([i, x, y, z])
            # 处理整个数据集，将每个向量的每个元素分别保留两位小数后添加到 liststore 中
        self.treeview.set_model(self.liststore)
        # 重新添加列到 TreeView
        self.add_columns_to_treeview()

    def add_columns_to_treeview(self):
        # 确保清除所有已有列
        for column in self.treeview.get_columns():
            self.treeview.remove_column(column)

        renderer_number = Gtk.CellRendererText()
        renderer_number.set_padding(6, 10)  # 初始值为 (10, 10)，现在设置为 (6, 10)
        column_text0 = Gtk.TreeViewColumn("Num", renderer_number, text=0)

        renderer_text = Gtk.CellRendererText()
        renderer_text.set_padding(6, 10)  # 初始值为 (10, 10)，现在设置为 (6, 10)
        column_text1 = Gtk.TreeViewColumn("X", renderer_text, text=1)

        renderer_number = Gtk.CellRendererText()
        renderer_number.set_padding(6, 10)  # 初始值为 (10, 10)，现在设置为 (6, 10)
        column_text2 = Gtk.TreeViewColumn("Y", renderer_number, text=2)

        renderer_number = Gtk.CellRendererText()
        renderer_number.set_padding(6, 10)  # 初始值为 (10, 10)，现在设置为 (6, 10)
        column_text3 = Gtk.TreeViewColumn("Z", renderer_number, text=3)

        column_text0.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_text0.set_fixed_width(60)  # 设定想要的宽度

        column_text1.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_text1.set_fixed_width(150)  # 设定想要的宽度

        column_text2.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_text2.set_fixed_width(150)  # 设定想要的宽度

        column_text3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column_text3.set_fixed_width(150)  # 设定想要的宽度

        self.treeview.append_column(column_text0)
        self.treeview.append_column(column_text1)
        self.treeview.append_column(column_text2)
        self.treeview.append_column(column_text3)

        # 重新绘制 TreeView
        self.treeview.show_all()




    """ 三个按钮的功能函数 """

    # 网格文件列表按钮
    def on_showing_value(self, widget, box1=None):

        # 获取网格文件列表按钮
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:  # 如果有选择

            # 获取选获取选中项的索引
            model = widget.get_model()
            tree_path = model.get_path(tree_iter)
            index = tree_path.get_indices()[0]

            # 赋予mesh成员网格变量
            self.mesh = box1.faceMeshList[index]

            # 获取 attribute_combobox 内容
            tree_iter1 = self.attribute_combobox.get_active_iter()
            model1 = self.attribute_combobox.get_model()
            value1 = model1[tree_iter1][0]  # 获取选中项的值
            if value1 == 'Points':
                self.data_list()
            elif value1 == 'Cells':
                self.cell_list()


    # 网格数据类型按钮
    def on_attribute_value(self, widget):
        tree_iter = widget.get_active_iter()
        if tree_iter is not None:

            # 获取选中项的值
            model = widget.get_model()
            value = model[tree_iter][0]

            # 首先清除所有已有列
            for column in self.treeview.get_columns():
                self.treeview.remove_column(column)

            # 根据选择的值显示特定列
            if value == "Points":
                self.data_list()
            elif value == "Cells":
                self.cell_list()

            # 先从scrolled_window中移除，避免重复添加
            # self.box_fixed.remove(self.treeview)
            # self.box_fixed.add(self.treeview)


    # 保留小数位数按钮
    def on_precision_value(self, widget):
        tree_iter = self.attribute_combobox.get_active_iter()
        if tree_iter is not None:
            model = self.attribute_combobox.get_model()
            value1 = model[tree_iter][0]  # 获取选中项的值

        if value1 == 'Points':
            value = int(self.precision_spinbox.get_value())
            for row in self.liststore:
                x = "{:.{}f}".format(float(row[1]), value)
                y = "{:.{}f}".format(float(row[2]), value)
                z = "{:.{}f}".format(float(row[3]), value)
                self.liststore[row.path][1] = x
                self.liststore[row.path][2] = y
                self.liststore[row.path][3] = z



# 应用 CSS 样式
def apply_css(window):
    css_provider = Gtk.CssProvider()
    css = """
    #treeview-grid-lines {
    border: 1px solid rgba(0, 0, 0, 0.5);  /* 半透明的黑色边框 */
    }


    #treeview-grid-lines row:nth-child(even) {
        background-color: #FFFF00; /* yellow background for even rows */
    }

    #treeview-grid-lines row:nth-child(odd) {
        background-color: #FFFFFF; /* white background for odd rows */
    }
    """
    css_provider.load_from_data(css)
    screen = Gdk.Screen.get_default()
    context = Gtk.StyleContext()
    context.add_provider_for_screen(screen, css_provider,
                                    Gtk.STYLE_PROVIDER_PRIORITY_USER)






