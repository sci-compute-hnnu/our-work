import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from Utils.Connector.SolverViewBoxConn import SolverViewBoxConn

class SolverWindow:

    def __init__(self, glade_path, box1, notebook, two_layer, three_layer):

        self.builder = Gtk.Builder()
        self.builder.add_from_file(glade_path)

        self.window = self.builder.get_object("solver_windows")

        # 关闭窗口 销毁界面
        self.window.connect("destroy", Gtk.main_quit)

        # "选择网格"combobox
        self.mesh_combobox = self.builder.get_object("select_mesh")
        # "选择绘制窗口"combobox
        self.draw_combobox = self.builder.get_object("select_draw")
        # 相关参数box
        self.para_box = self.builder.get_object("para_box")
        # 刷新频率
        self.freq_spin = self.builder.get_object("freq_spin")
        # 总时间
        self.all_time_spin = self.builder.get_object("time_spin")
        # 开始按钮
        self.start_button = self.builder.get_object('start_button')

        # 其他需要使用的部件
        self.box1 = box1
        self.notebook = notebook
        self.two_layer = two_layer
        self.three_layer = three_layer

        # 创建网格选择下拉框
        # 创建 ListStore
        mesh_store = self.get_current_mesh()
        renderer = Gtk.CellRendererText()
        self.mesh_combobox.pack_start(renderer, True)
        self.mesh_combobox.add_attribute(renderer, "text", 0)
        self.mesh_combobox.set_model(mesh_store)

        # 创建绘制窗口选择下拉框
        draw_store = Gtk.ListStore(str)
        draw_store.append(["current viewbox"])
        renderer = Gtk.CellRendererText()
        self.draw_combobox.pack_start(renderer, True)
        self.draw_combobox.add_attribute(renderer, "text", 0)
        self.draw_combobox.set_model(draw_store)

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
        self.all_time_spin.set_value(30.0)  # 设置默认60.0s


        # 连接器
        self.Connector = SolverViewBoxConn()
        # 选择的网格
        self.selectedMeshClass = None


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

        self.start_button.connect("clicked", self.start_)

    def run(self):

        self.window.show_all()
        Gtk.main()


    # 获取当前box1中的网格 并加载至网格下拉框
    def get_current_mesh(self):

        draw_store = Gtk.ListStore(str)

        for item in self.box1.list_store:
            value = list(item)  # 获取当前条目的值 [bool, str]
            meshName = value[1]  # 获取网格名字
            draw_store.append([meshName])  # 将网格加载至draw_store

        return draw_store


    # 点击开始按钮
    def start_(self, button):

        """step0  获取相关参数"""
        # 获取所选网格的名字
        currentMeshName = None
        tree_iter = self.mesh_combobox.get_active_iter()
        if tree_iter is not None:
            model = self.mesh_combobox.get_model()
            value = model[tree_iter][0]  # 获取当前选中项的网格
            currentMeshName = value
        else:
            print("未选择任何网格")

        # 获取刷新频率
        freq = float(self.freq_spin.get_value())
        # 获取总时间
        all_time = float(self.all_time_spin.get_value())


        """step1  来到box1中查找网格"""
        should_draw = -1
        for index, item in enumerate(self.box1.list_store):
            value = list(item)  # 获取当前条目的值 [bool, str]
            meshName = value[1]  # 获取网格名字

            # 检查是否匹配
            if currentMeshName == meshName:
                self.selectedMeshClass = self.box1.faceMeshList[index]  # 获取当前的索引
                should_draw = index
                break

        """step2  在three_layer的两个选择框中切换相关选项"""
        # 将点线面选择框中切换为 "Surface" 绘制模式
        self.three_layer.switch_option_in_select_box(2, 'Surface', self.notebook.showbox)

        # 将颜色绘制选择框设置为 "var" 模式
        self.three_layer.switch_option_in_select_box(1, 'var', self.notebook.showbox)


        """step3  建立渲染连接器"""
        self.Connector.load_fit(self.notebook.showbox, should_draw,
                                      self.two_layer.timer_entry, self.box1, freq, all_time)



