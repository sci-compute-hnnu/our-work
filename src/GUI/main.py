import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk

from GUI.box0.main import box0
from GUI.one_layer.main import one_layer
from GUI.two_layer.main import two_layer
from GUI.three_layer.main import three_layter


class UI():

    def __init__(self):

        self.builder = Gtk.Builder()
        self.builder.add_from_file("../../ui/main.glade")

        self.window = self.builder.get_object("window")
        self.window.connect("destroy", Gtk.main_quit)



        """----------------one_layer----------------"""
        """
            部件:
            file_button      file下拉列表
            edit_button      edit下拉列表
            view_button      view下拉列表
            sources_button   source下来列表
        """
        self.one_layer = one_layer(self.builder)

        """File的下拉列表"""
        self.open_button = self.one_layer.open_button

        """Edit的下拉列表"""
        self.apply_button = self.one_layer.apply_button
        self.reset_hide_button = self.one_layer.reset_hide_button
        self.delete_hide_button = self.one_layer.delete_hide_button

        """View的下拉列表"""
        # Pipline Browse
        self.PB = self.one_layer.PB

        """Mesh的下拉列表"""
        self._2DMesh = self.one_layer._2DMesh
        self._3DMesh = self.one_layer._3DMesh

        """Solver的下拉列表"""
        self._2D_Solver = self.one_layer._2D_Solver
        self._3D_Solver = self.one_layer._3D_Solver

        """Style的下拉列表"""
        self.default_style = self.one_layer.default_style
        self.simple_style = self.one_layer.simple_style
        self.dark_style = self.one_layer.dark_style


        """----------------two_layer----------------"""

        """
            部件:
            filebutton   文件选择按钮
            back_color_button   背景颜色选择按钮
        """
        self.two_layer = two_layer(self.builder)

        # filebutton
        self.filebutton = self.two_layer.filebutton

        # back_color_button
        self.blue_gray = self.two_layer.blue_gray
        self.white = self.two_layer.white
        self.warm_gray = self.two_layer.warm_gray
        self.dark_gray = self.two_layer.dark_gray
        self.neutral_gray = self.two_layer.neutral_gray
        self.light_gray = self.two_layer.light_gray
        self.black = self.two_layer.black
        self.gradient = self.two_layer.gradient

        # back_color of enum
        self.back_color = self.two_layer.back_color

        # camera
        self.camera = self.two_layer.camera



        """----------------three_layer----------------"""

        """
            部件
            select_type_box: 点线面选择绘制按钮
            select_var_box: 颜色选择绘制按钮
            sb_button, bs_button:  变大变小按钮
            Xposi_button...  :     坐标轴旋转按钮
            Color:    颜色选择按钮
        """
        self.three_layer = three_layter(self.builder)

        # 线面点绘制选择按钮
        self.select_type_box = self.three_layer.select_type_box
        self.select_var_box = self.three_layer.select_var_box

        # 变大变小按钮
        self.sb_button = self.three_layer.sb_button
        self.bs_button = self.three_layer.bs_button

        # 坐标轴旋转按钮
        self.Xposi_button = self.three_layer.Xposi_button
        self.Xnega_button = self.three_layer.Xnega_button
        self.Yposi_button = self.three_layer.Yposi_button
        self.Ynega_button = self.three_layer.Ynega_button
        self.Zposi_button = self.three_layer.Zposi_button
        self.Znega_button = self.three_layer.Znega_button
        self.iso_button = self.three_layer.iso_button

        # 顺时针逆时针旋转按钮
        self.clockwise_button = self.three_layer.clockwise_button
        self.counter_button = self.three_layer.counter_button

        # 颜色选择按钮
        self.color_button = self.three_layer.color_button

        # 切平面方程输入按钮
        self.split_plane_button = self.three_layer.split_plane_button


        """----------------box0----------------"""

        self.box0 = box0(self.builder)

        """
        paned部分: 
        box1_paned: 拉索Pb 和 information
        paned0: 拉索box1 和 paned1
        paned1: 拉索box3 和 paned2
        paned2: 拉索shell_box 和 notebook 
        """
        self.box1_paned = self.box0.paned0.box1.box1_paned
        self.paned0 = self.box0.paned0.paned0
        self.paned1 = self.box0.paned0.paned1.paned1
        self.paned2 = self.box0.paned0.paned1.paned2.paned2

        """
        box1部分:
        Pipline Browse:  PB_close_button（关闭按钮）, treeview（文件状态列表）
        information  information_close_button (关闭按钮)
        """
        self.box1 = self.box0.paned0.box1

        # Pipline Browse
        self.PB_close_button = self.box1.PB_close_button
        self.treeview = self.box1.treeview
        self.list_store = self.box1.list_store
        # information
        self.information_close_button = self.box1.information_close_button


        """
        box2部分
        """
        self.box2 = self.box0.box2
        self.file_button = self.box0.box2.file_button
        self.variable_button = self.box0.box2.variable_button

        """
        box3部分
        open_folder_button 打开文件夹
        new_file_button 新建文件夹
        save_file_button 保存文件夹
        close_folder_button 关闭文件框
        """
        self.box3 = self.box0.paned0.paned1.box3

        self.open_folder_button = self.box3.open_folder_button
        self.close_folder_button = self.box3.close_folder_button
        self.file_tree_view = self.box3.file_tree_view



        """
        notebook部分
        notebook 
        showbox (实时更新的当前状态下的showbox) 包含viewbox databox meunbox
        containerList  (用于存放包括showbox的容器的列表)
        add_button  (notebook的添加按钮)
        """
        self.notebook = self.box0.paned0.paned1.paned2.notebook
        # notebook
        self.note_book = self.notebook.notebook
        # add_button（notebook的添加按钮）
        self.add_button = self.notebook.add_button


        """
        shell_box部分
        shell_box
        text_view 文本显示
        shell_box_close_button 关闭
        shell (View中的shell)
        """
        self.shell_box = self.box0.paned0.paned1.paned2.shell_box
        self.text_view = self.shell_box.text_view
        self.shell_box_close_button = self.shell_box.shell_box_close_button
        self.Shell = self.shell_box.Shell







        """--------------连接函数-------------"""
        """连接信号时之所以使用Lambda表达式是为了实时更新当前的showbox"""

        """--------------one_layerd的连接信号--------------"""

        self.one_layer.loadWidget(self.box1, self.notebook, self.two_layer, self.three_layer)

        # 第一层的view的 Pipline Browse, PB_close_button 的关闭按钮
        self.PB.connect("activate", self.one_layer.PB_active, self.box1)
        # 第一层Edit的三个按钮
        self.apply_button.connect("activate", lambda btn: self.box1.apply_clicked(btn, self.get_current_showbox()))
        self.reset_hide_button.connect("activate", lambda btn: self.box1.reset_clicked(btn, self.get_current_showbox()))
        self.delete_hide_button.connect("activate",
                                        lambda btn: self.box1.delete_clicked(btn, self.get_current_showbox()))
        # 第一层file的open按钮
        self.open_button.connect("activate", self.one_layer.open_clicked, self.two_layer.filebutton)

        # 第一层的Mesh按钮
        self._2DMesh.connect("activate", self.one_layer.open_2d_mesh_widonw)
        self._3DMesh.connect("activate", self.one_layer.open_3d_mesh_widonw)

        # 第一层的Solver按钮
        self._2D_Solver.connect("activate", self.one_layer.open_2D_solver_window)
        self._3D_Solver.connect("activate", self.one_layer.open_3D_solver_window)

        self.default_style.connect("activate", self.one_layer.change_style)
        self.simple_style.connect("activate", self.one_layer.change_style)
        self.dark_style.connect("activate", self.one_layer.change_style)


        """--------------two_layerd的连接信号--------------"""
        # 第二层的文件按钮
        self.filebutton.connect("clicked",
                                lambda btn: self.two_layer.on_file_set(btn, self.box1, self.get_current_showbox()))
        # 第二层的更换背景颜色按钮
        self.blue_gray.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                     self.back_color.blue_gray))
        self.white.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                 self.back_color.white))
        self.black.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                 self.back_color.black))
        self.warm_gray.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                     self.back_color.warm_gray))
        self.dark_gray.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                     self.back_color.dark_gray))
        self.neutral_gray.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                        self.back_color.neutral_gray))
        self.light_gray.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                      self.back_color.light_gray))
        self.gradient.connect("activate", lambda btn: self.two_layer.set_back_color(btn, self.get_current_showbox(),
                                                                                    self.back_color.gradient))
        # 连接截图
        self.camera.connect("clicked",
                            lambda btn: self.two_layer.on_screenshot_button_clicked(self.note_book, self.box1.box1,
                                                                                    btn))


        """--------------three_layerd连接函数--------------"""
        # 第三层的选择框
        self.select_type_box.connect('changed', lambda btn: self.three_layer.select_option_with_face_or_edge(
                                                                                    btn, self.get_current_showbox()))
        self.select_var_box.connect('changed', lambda btn: self.three_layer.select_option_with_color(
                                                                                    btn, self.get_current_showbox()))
        # 第三层的变大变小按钮
        self.sb_button.connect('clicked',
                               lambda btn: self.three_layer.restore_original_state(btn, self.get_current_showbox(), 1))
        self.bs_button.connect('clicked',
                               lambda btn: self.three_layer.restore_original_state(btn, self.get_current_showbox(), 2))
        # 第三层的坐标轴旋转按钮
        self.Xposi_button.connect('clicked',
                                  lambda btn: self.three_layer.set_view_to_XYZ(btn, self.get_current_showbox(), 1))
        self.Xnega_button.connect('clicked',
                                  lambda btn: self.three_layer.set_view_to_XYZ(btn, self.get_current_showbox(), 2))
        self.Yposi_button.connect('clicked',
                                  lambda btn: self.three_layer.set_view_to_XYZ(btn, self.get_current_showbox(), 3))
        self.Ynega_button.connect('clicked',
                                  lambda btn: self.three_layer.set_view_to_XYZ(btn, self.get_current_showbox(), 4))
        self.Zposi_button.connect('clicked',
                                  lambda btn: self.three_layer.set_view_to_XYZ(btn, self.get_current_showbox(), 5))
        self.Znega_button.connect('clicked',
                                  lambda btn: self.three_layer.set_view_to_XYZ(btn, self.get_current_showbox(), 6))
        self.iso_button.connect('clicked',
                                lambda btn: self.three_layer.set_view_to_XYZ(btn, self.get_current_showbox(), 7))
        # 第三层网格颜色选择按钮
        self.color_button.connect("clicked", lambda btn: self.three_layer.select_color(btn, self.get_current_showbox()))
        # 第三层的顺时针逆时针旋转按钮
        self.clockwise_button.connect("clicked",
                                      lambda btn: self.three_layer.rotation_90(btn, self.get_current_showbox(), 1))
        self.counter_button.connect("clicked",
                                    lambda btn: self.three_layer.rotation_90(btn, self.get_current_showbox(), 2))

        # 第三层切平面方程输入按钮
        self.split_plane_button.connect("clicked",
                                        lambda btn: self.three_layer.open_split_plane_input(
                                            btn, self.get_current_showbox(), self.box1))


        """--------------box0连接函数--------------"""
        """  paned部分  """
        self.box1_paned.connect("notify::position", self.box0.paned0.box1.on_paned_position_changed)
        self.paned0.connect("notify::position", self.box0.paned0.on_paned_position_changed)
        self.paned1.connect("notify::position", self.box0.paned0.paned1.on_paned_position_changed)
        self.paned2.connect("notify::position", self.box0.paned0.paned1.paned2.on_paned_position_changed)

        """  box1部分  """
        # Pipline Browse 的相关按钮
        # treeview的按钮列 （状态栏）
        self.box1.renderer_toggle.connect("toggled",
                                          lambda *args: self.box1.on_toggle_button_toggled(args[0], args[1],
                                            self.get_current_showbox(), self.select_var_box, self.three_layer.setup_combobox))
        # Pipline Browse 的关闭按钮
        self.PB_close_button.connect("clicked", self.box1.PB_close, self.one_layer)

        # information 的相关按钮
        # information 的关闭按钮
        self.information_close_button.connect("clicked", self.box1.information_close, self.one_layer)


        """ box2部分 """
        self.file_button.connect("clicked", self.box2.file_button_clicked, self.paned1, self.box3)
        self.variable_button.connect("clicked", self.box2.variable_button_clicked, self.paned1, self.paned2,
                                     self.shell_box)


        """ box3部分 """
        # 打开文件夹
        self.open_folder_button.connect("clicked", self.box3.on_open_folder_clicked)
        # 打开文件
        self.file_tree_view.connect("row-activated", lambda *args:
                self.box3.on_file_activated(args[0], args[1], args[2], self.get_current_showbox()))
        # 关闭文件框
        self.close_folder_button.connect("clicked", self.box3.close_editFile_box)



        """ notebook部分"""
        # 添加标签页的按钮
        self.add_button.connect("clicked", self.notebook.from_add_button)
        self.notebook.setting_other_widget(self.box1, self.box3, self.three_layer)
        # 更改标签页的按钮
        self.note_book.connect("switch-page", self.notebook.from_on_switch_page)
        # 先初始化一个 view_box
        self.notebook.create_tab("Layout  #1", func=1)


        """ shell_box部分 """
        # 键盘回调
        self.text_view.connect("key-press-event", self.shell_box.on_key_press, self.paned1, self.paned2)
        # shell_box关闭
        self.shell_box_close_button.connect("clicked", self.shell_box.shell_close, self.one_layer)
        # shell 选项切换
        self.Shell.connect("toggled", self.shell_box.on_shell_toggled, self.paned2)



    # 实时更新showbox
    def get_current_showbox(self):
        return self.notebook.showbox


    def run(self):
        self.window.show_all()
        Gtk.main()

win = UI()
win.run()
