import gi
import numpy as np
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf


class three_layter():

    def __init__(self, builder):

        ''' 线面点选择框 '''

        self.select_box = builder.get_object("select_box")
        # 创建一个ListStore对象
        self.liststore = Gtk.ListStore(str)
        # 添加各个选项
        self.liststore.append(["Points"])
        self.liststore.append(["Lines"])
        self.liststore.append(['Surface With Edges'])
        self.liststore.append(["Surface"])
        self.liststore.append(['Gmsh style'])

        # 将ListStore对象设置为ComboBox的模型
        self.select_box.set_model(self.liststore)
        # 创建一个CellRendererText对象
        renderer = Gtk.CellRendererText()
        # 将CellRendererText对象添加到ComboBox中的第一个列
        # 显示列表
        self.select_box.pack_start(renderer, True)
        self.select_box.add_attribute(renderer, "text", 0)

        # 获取Surface选项的迭代器
        surface_iter = self.liststore.get_iter_first()
        while surface_iter is not None:
            if self.liststore.get_value(surface_iter, 0) == "Surface":
                break
            surface_iter = self.liststore.iter_next(surface_iter)
        # 将Surface选项设置为默认显示选项
        self.select_box.set_active_iter(surface_iter)


        ''' 颜色绘制选择框 '''
        self.select_box1 = builder.get_object("select_box1")
        # 创建一个ListStore对象
        self.liststore1 = Gtk.ListStore(str)
        # 添加各个选项
        self.liststore1.append(["Solid Color"])
        self.liststore1.append(["var"])
        # 将ListStore对象设置为ComboBox的模型
        self.select_box1.set_model(self.liststore1)
        # 创建一个CellRendererText对象
        renderer1 = Gtk.CellRendererText()
        # 将CellRendererText对象添加到ComboBox中的第一个列
        # 显示列表
        self.select_box1.pack_start(renderer1, True)
        self.select_box1.add_attribute(renderer1, "text", 0)

        # 获取Surface选项的迭代器
        surface_iter = self.liststore1.get_iter_first()
        while surface_iter is not None:
            if self.liststore1.get_value(surface_iter, 0) == "Solid Color":
                break
            surface_iter = self.liststore1.iter_next(surface_iter)
        # 将Surface选项设置为默认显示选项
        self.select_box1.set_active_iter(surface_iter)


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
        showbox.edge_draw = showbox.face_draw = showbox.points_draw = showbox.var_draw = False


    # 选择在选项框中切换选项
    # select_box_num=1  颜色选择框  select_box_num=2 点线面选择框
    def switch_option_in_select_box(self, select_box_num, option, showbox):

        liststore = None
        select_box = None

        if select_box_num == 1:  # 颜色选择框
            liststore = self.liststore1
            select_box = self.select_box1
        elif select_box_num == 2:   # 点线面选择框
            liststore = self.liststore
            select_box = self.select_box

        # 切换至所选选项
        for index, row in enumerate(liststore):
            if row[0] == option:
                select_box.set_active(index)
                break

        if select_box_num == 1:  # 颜色选择框
            self.select_option_with_color(widget=None, showbox=showbox)  # 调用相关函数
        elif select_box_num == 2:   # 点线面选择框
            self.select_option_with_face_or_edge(widget=None, showbox=showbox)  # 调用相关函数


    # 是否绘制 点 线 面
    def select_option_with_face_or_edge(self, widget, showbox):
        # 获取选中项的迭代器
        active_iter = self.select_box.get_active_iter()

        if active_iter is not None:
            # 获取选中项的值
            model = self.select_box.get_model()
            selected_value = model.get_value(active_iter, 0)

            # 根据不同的选项显示对应的元素
            if selected_value == "Lines":
                self.reset_draw_states(showbox)  # 重置

                showbox.edge_draw = True

            elif selected_value == "Surface":
                self.reset_draw_states(showbox)   # 重置

                showbox.face_draw = True

            elif selected_value == "Points":
                self.reset_draw_states(showbox)   # 重置

                showbox.points_draw = True

            elif selected_value == 'Surface With Edges':
                self.reset_draw_states(showbox)   # 重置

                showbox.edge_draw = True
                showbox.face_draw = True

            elif selected_value == 'Gmsh style':

                self.reset_draw_states(showbox)  # 重置
                showbox.gmsh_draw = True

            showbox.glarea.queue_draw()  # 绘制更新



    # 是否绘制 颜色
    def select_option_with_color(self, widget, showbox):
        # 获取选中项的迭代
        active_iter = self.select_box1.get_active_iter()

        if active_iter is not None:
            # 获取选中项的值
            model = self.select_box1.get_model()
            selected_value = model.get_value(active_iter, 0)

            # 根据不同的选项显示对应的元素
            if selected_value == "Solid Color":
                self.reset_draw_states(showbox)  # 重置
                showbox.face_draw = True

            elif selected_value == "var":
                self.reset_draw_states(showbox)   # 重置

                showbox.var_draw = True


            showbox.glarea.queue_draw()  # 绘制更新


    # 放大或缩小按钮
    def restore_original_state(self, button, showbox, func):

        if func == 1:  # 执行放大
            showbox.scale = 1 + showbox.zoom_sensitivity
        elif func == 2:   # 执行缩小
            showbox.scale = 1 - showbox.zoom_sensitivity

        s = showbox.scale

        # 更新size
        showbox.size *= s

        # 创建一个缩放矩阵
        scale_matrix = np.array([
            [s, 0, 0, 0],
            [0, s, 0, 0],
            [0, 0, s, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        showbox.rotation_matrix = np.dot(showbox.rotation_matrix, scale_matrix).astype(np.float32)

        # 更新渲染
        showbox.glarea.queue_draw()



    # 旋转按钮
    def set_view_to_XYZ(self, button, showbox, func):

        showbox.rotation_matrix = np.array([
            [showbox.size, 0, 0, 0],
            [0, showbox.size, 0, 0],
            [0, 0, showbox.size, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        if func == 1:
            showbox.angle_x = 3 * np.pi / 2
            showbox.angle_y = np.pi
            showbox.update_rotation_matrix()
            showbox.angle_x = 0
            showbox.angle_y = np.pi / 2
        elif func == 2:
            showbox.angle_x = 1 * np.pi / 2
            showbox.angle_y = -np.pi
            showbox.update_rotation_matrix()
            showbox.angle_x = np.pi
            showbox.angle_y = np.pi / 2
        elif func == 3:
            showbox.angle_x = 3 * np.pi/2
            showbox.angle_y = np.pi
        elif func == 4:
            showbox.angle_x = np.pi/2
            showbox.angle_y = 0
        elif func == 5:
            showbox.angle_x = 0
            showbox.angle_y = 0
        elif func == 6:
            showbox.angle_x = 0
            showbox.angle_y = np.pi
        elif func == 7:
            showbox.angle_x = 0
            showbox.angle_y = np.pi
            showbox.update_rotation_matrix()
            showbox.angle_x = np.pi / 4
            showbox.angle_y = - np.pi / 4

        # 更新旋转矩阵
        showbox.update_rotation_matrix()
        showbox.glarea.queue_draw()


    # 顺时针逆时针旋转90度
    def rotation_90(self, button, showbox, func):
        if func == 1:
            showbox.angle_x = np.pi / 2
            showbox.angle_y = np.pi / 2
            showbox.update_rotation_matrix()
            showbox.angle_x = -np.pi
            showbox.angle_y = np.pi / 2
        elif func == 2:
            showbox.angle_x = - np.pi / 2
            showbox.angle_y = np.pi / 2
            showbox.update_rotation_matrix()
            showbox.angle_x = -np.pi
            showbox.angle_y = np.pi / 2
        # 更新旋转矩阵
        showbox.update_rotation_matrix()
        showbox.glarea.queue_draw()


    # 颜色选择
    def select_color(self, button, showbox):
        dialog = Gtk.ColorChooserDialog(title="Select  Color", parent=None)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            color = dialog.get_rgba()
            # Convert color channel values to the appropriate range [0, 1]
            showbox.face_color[0] = color.red
            showbox.face_color[1] = color.green
            showbox.face_color[2] = color.blue
            showbox.face_color[3] = color.alpha

            showbox.glarea.queue_draw()

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

        self.disable_button(self.select_box)

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

        self.enable_button(self.select_box)
