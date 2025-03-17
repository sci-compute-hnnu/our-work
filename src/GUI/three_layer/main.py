import gi
import numpy as np
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf


class three_layter():

    def __init__(self, builder):

        ''' 线面点选择框 '''

        self.select_type_box = builder.get_object("select_box")
        self.type_list = ["Points", "Lines", "Surface With Edges", "Surface", "Gmsh style"]
        self.setup_combobox(self.select_type_box, self.type_list, 'Surface')


        ''' 颜色绘制选择框 '''
        self.select_var_box = builder.get_object("select_box1")

        """放大放小按钮"""

        self.sb_button = builder.get_object("small_big")
        self.bs_button = builder.get_object("big_small")

        '''坐标轴旋转按钮'''

        self.Xposi_button = builder.get_object("Xposi")
        self.Xnega_button = builder.get_object("Xnega")
        self.Yposi_button = builder.get_object("Yposi")
        self.Ynega_button = builder.get_object("Ynega")
        self.Zposi_button = builder.get_object("Zposi")
        self.Znega_button = builder.get_object("Znega")
        self.iso_button = builder.get_object("isometric_view")


        '''网格颜色选择按钮'''
        self.color_button = builder.get_object("Color")

        '''顺时针逆时针旋转90度按钮'''
        self.clockwise_button = builder.get_object("clockwise")
        self.counter_button = builder.get_object("counterclockwise")


    # 重置draw的状态
    def reset_draw_states(self, showbox):

        glarea = showbox.glareaClass
        glarea.edge_draw = glarea.face_draw = glarea.points_draw = glarea.var_draw = False


    # 选择在选项框中切换选项
    # select_box_num=1  颜色选择框  select_box_num=2 点线面选择框
    def switch_option_in_select_box(self, select_box_num, option, showbox):

        liststore = None
        select_box = None

        if select_box_num == 1:  # 颜色选择框
            select_box = self.select_var_box

        elif select_box_num == 2:   # 点线面选择框
            select_box = self.select_type_box

        liststore = select_box.get_model()

        # 切换至所选选项
        for index, row in enumerate(liststore):
            if row[0] == option:
                select_box.set_active(index)
                break

        if select_box_num == 1:  # 颜色选择框
            self.select_option_with_color(widget=None, showbox=showbox)  # 调用相关函数
        elif select_box_num == 2:   # 点线面选择框
            self.select_option_with_face_or_edge(widget=None, showbox=showbox)  # 调用相关函数


    # 给select_box设置新的选项
    def setup_combobox(self, select_box, options=[' '], default_option=' '):
        """
        初始化一个 Gtk.ComboBox，添加渲染器，并设置默认选项

        :param select_type_box: Gtk.ComboBox 实例
        :param options: 可选项列表
        :param default_option: 默认选项"
        """

        # 创建 ListStore 对象
        liststore = Gtk.ListStore(str)

        # 添加选项
        for option in options:
            liststore.append([option])

        # 设置 ListStore 为 ComboBox 的模型
        select_box.set_model(liststore)

        # 创建渲染器并添加到 ComboBox
        if not select_box.get_cells():  # 避免重复添加渲染器
            renderer = Gtk.CellRendererText()
            select_box.pack_start(renderer, True)
            select_box.add_attribute(renderer, "text", 0)

        # 获取默认选项的迭代器并设置为默认选项
        default_iter = liststore.get_iter_first()
        while default_iter is not None:
            if liststore.get_value(default_iter, 0) == default_option:
                select_box.set_active_iter(default_iter)
                break
            default_iter = liststore.iter_next(default_iter)
        # 设置按钮可不可用
        if default_option == ' ':
            self.disable_button(select_box)
        else:
            self.enable_button(select_box)



    # 是否绘制 点 线 面
    def select_option_with_face_or_edge(self, widget, showbox):
        # 获取选中项的迭代器
        active_iter = self.select_type_box.get_active_iter()

        if active_iter is not None:
            # 获取选中项的值
            model = self.select_type_box.get_model()
            selected_value = model.get_value(active_iter, 0)

            glarea = showbox.glareaClass

            # 根据不同的选项显示对应的元素
            if selected_value == "Lines":
                self.reset_draw_states(showbox)  # 重置

                glarea.edge_draw = True

            elif selected_value == "Surface":
                self.reset_draw_states(showbox)   # 重置

                glarea.face_draw = True

            elif selected_value == "Points":
                self.reset_draw_states(showbox)   # 重置

                glarea.points_draw = True

            elif selected_value == 'Surface With Edges':
                self.reset_draw_states(showbox)   # 重置

                glarea.edge_draw = True
                glarea.face_draw = True

            elif selected_value == 'Gmsh style':

                self.reset_draw_states(showbox)  # 重置
                glarea.gmsh_draw = True

            glarea.glarea.queue_draw()  # 绘制更新


    # 是否绘制 颜色
    def select_option_with_color(self, widget, showbox):

        # 获取选中项的迭代
        active_iter = self.select_var_box.get_active_iter()

        if active_iter is not None:
            # 获取选中项的值
            model = self.select_var_box.get_model()
            selected_value = model.get_value(active_iter, 0)
            glarea = showbox.glareaClass

            # 根据不同的选项显示对应的元素
            if selected_value == "Neutral Mode":
                self.reset_draw_states(showbox)  # 重置
                glarea.face_draw = True

            # 当点击color_opt后 记得更新viewbox(showbox)的color_opt
            else:

                self.reset_draw_states(showbox)   # 重置
                showbox.color_opt = selected_value
                glarea.var_draw = True

            showbox.on_realize()
            glarea.glarea.queue_draw()


    # 放大或缩小按钮
    def restore_original_state(self, button, showbox, func):

        glarea = showbox.glareaClass

        if func == 1:  # 执行放大
            glarea.scale = 1 + glarea.zoom_sensitivity
        elif func == 2:   # 执行缩小
            glarea.scale = 1 - glarea.zoom_sensitivity

        s = glarea.scale

        # 更新size
        glarea.size *= s

        # 创建一个缩放矩阵
        scale_matrix = np.array([
            [s, 0, 0, 0],
            [0, s, 0, 0],
            [0, 0, s, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        glarea.rotation_matrix = np.dot(glarea.rotation_matrix, scale_matrix).astype(np.float32)

        # 更新渲染
        glarea.glarea.queue_draw()



    # 旋转按钮
    def set_view_to_XYZ(self, button, showbox, func):

        glarea = showbox.glareaClass

        glarea.rotation_matrix = np.array([
            [glarea.size, 0, 0, 0],
            [0, glarea.size, 0, 0],
            [0, 0, glarea.size, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        if func == 1:
            glarea.angle_x = 3 * np.pi / 2
            glarea.angle_y = np.pi
            glarea.update_rotation_matrix()
            glarea.angle_x = 0
            glarea.angle_y = np.pi / 2
        elif func == 2:
            glarea.angle_x = 1 * np.pi / 2
            glarea.angle_y = -np.pi
            glarea.update_rotation_matrix()
            glarea.angle_x = np.pi
            glarea.angle_y = np.pi / 2
        elif func == 3:
            glarea.angle_x = 3 * np.pi/2
            glarea.angle_y = np.pi
        elif func == 4:
            glarea.angle_x = np.pi/2
            glarea.angle_y = 0
        elif func == 5:
            glarea.angle_x = 0
            glarea.angle_y = 0
        elif func == 6:
            glarea.angle_x = 0
            glarea.angle_y = np.pi
        elif func == 7:
            glarea.angle_x = 0
            glarea.angle_y = np.pi
            glarea.update_rotation_matrix()
            glarea.angle_x = np.pi / 4
            glarea.angle_y = - np.pi / 4

        # 更新旋转矩阵
        glarea.update_rotation_matrix()
        glarea.glarea.queue_draw()


    # 顺时针逆时针旋转90度
    def rotation_90(self, button, showbox, func):

        glarea = showbox.glareaClass

        if func == 1:
            glarea.angle_x = np.pi / 2
            glarea.angle_y = np.pi / 2
            glarea.update_rotation_matrix()
            glarea.angle_x = -np.pi
            glarea.angle_y = np.pi / 2
        elif func == 2:
            glarea.angle_x = - np.pi / 2
            glarea.angle_y = np.pi / 2
            glarea.update_rotation_matrix()
            glarea.angle_x = -np.pi
            glarea.angle_y = np.pi / 2
        # 更新旋转矩阵
        glarea.update_rotation_matrix()
        glarea.glarea.queue_draw()


    # 颜色选择
    def select_color(self, button, showbox):
        dialog = Gtk.ColorChooserDialog(title="Select  Color", parent=None)
        response = dialog.run()

        glarea = showbox.glareaClass

        if response == Gtk.ResponseType.OK:
            color = dialog.get_rgba()
            # Convert color channel values to the appropriate range [0, 1]
            glarea.face_color[0] = color.red
            glarea.face_color[1] = color.green
            glarea.face_color[2] = color.blue
            glarea.face_color[3] = color.alpha

            glarea.glarea.queue_draw()

        dialog.destroy()

    # 设置按钮无法点击且颜色变灰
    def disable_button(self, button):
        button.set_sensitive(False)
        button.get_style_context().add_class("sensitive")

    # 恢复按钮
    def enable_button(self, button):
        button.set_sensitive(True)
        button.get_style_context().remove_class("insensitive")

    # 设置第三层按钮无法点击且颜色变灰
    def disable_three_layer(self):
        self.disable_button(self.sb_button)
        self.disable_button(self.bs_button)

        self.disable_button(self.Xnega_button)
        self.disable_button(self.Xposi_button)
        self.disable_button(self.Ynega_button)
        self.disable_button(self.Yposi_button)
        self.disable_button(self.Znega_button)
        self.disable_button(self.Zposi_button)
        self.disable_button(self.iso_button)

        self.disable_button(self.color_button)

        self.disable_button(self.counter_button)
        self.disable_button(self.clockwise_button)

        self.disable_button(self.select_type_box)

    # 恢复第三层按钮

    def enable_three_layer(self):
        self.enable_button(self.sb_button)
        self.enable_button(self.bs_button)

        self.enable_button(self.Xnega_button)
        self.enable_button(self.Xposi_button)
        self.enable_button(self.Yposi_button)
        self.enable_button(self.Ynega_button)
        self.enable_button(self.Zposi_button)
        self.enable_button(self.Znega_button)
        self.enable_button(self.iso_button)

        self.enable_button(self.color_button)

        self.enable_button(self.counter_button)
        self.enable_button(self.clockwise_button)

        self.enable_button(self.select_type_box)


