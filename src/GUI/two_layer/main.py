import os
from enum import Enum
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf



# 背景颜色的枚举
class back_color(Enum):
    # blue_gray
    blue_gray = (0.35, 0.35, 0.4655)
    # white
    white = (1.0, 1.0, 1.0)
    # black
    black = (0.0, 0.0, 0.0)
    # warm_gray
    warm_gray = (0.42, 0.395, 0.395)
    # dark_gray
    dark_gray = (0.35, 0.32, 0.32)
    # neutral_gray
    neutral_gray = (0.45, 0.45, 0.45)
    # light_gray
    light_gray = (0.525, 0.5, 0.5)



class two_layer():

    def __init__(self, builder):

        # 文件按钮
        self.filebutton = builder.get_object("filebutton")

        # 更换背景颜色按钮
        self.blue_gray = builder.get_object("blue_gray")
        self.white = builder.get_object("white")
        self.warm_gray = builder.get_object("warm_gray")
        self.dark_gray = builder.get_object("dark_gray")
        self.neutral_gray = builder.get_object("neutral_gray")
        self.light_gray = builder.get_object("light_gray")
        self.black = builder.get_object("black")
        self.gradient = builder.get_object("gradient")

        # 背景颜色的枚举
        self.back_color = back_color

        # 计时器
        self.timer = builder.get_object('timer')
        self.timer_entry = self.timer.get_child()



    def on_file_set(self, widget, box1, showbox):
        # 创建文件选择器对话框
        buttonfile = Gtk.FileChooserDialog(title="Choose File", parent=None,
                                           action=Gtk.FileChooserAction.OPEN)
        buttonfile.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        buttonfile.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        response = buttonfile.run()
        if response == Gtk.ResponseType.OK:

            selected_file = buttonfile.get_filename()

            # # 只要文件名
            # name_only = os.path.basename(selected_file)

            # 读入网格数据
            box1.load_Mesh_file(selected_file)

            # """将新添加的网格设置为True 其余为False"""
            # 在box1.list_store添加新条目并设置为True
            # new_iter = box1.list_store.append([False, name_only])
            # # 获取新添加条目的路径
            # new_path = box1.list_store.get_path(new_iter)
            # # 添加了新条目后旧条目变成False
            # for row in box1.list_store:
            #     # 获取当前条目的路径
            #     path = box1.list_store.get_path(row.iter)
            #     # 检查当前条目是否不是新添加的条目
            #     if path != new_path:
            #         # 将当前条目的状态设置为False
            #         box1.list_store[row.iter][0] = False


            """更新showbox 的状态列表"""
            showbox.list_store_state = box1.record_status_from_list_store()

            # """更新should_draw"""
            # showbox.should_draw = box1.find_true_row()
            # # 重新初始化
            # showbox.on_realize(showbox.glarea, box1)
            # # 更新绘制
            # showbox.glarea.queue_draw()

        buttonfile.destroy()

    # 背景颜色改变
    def set_back_color(self, button, showbox, back_color):
        showbox.is_gradient = False
        showbox.back_red = back_color.value[0]
        showbox.back_green = back_color.value[1]
        showbox.back_blue = back_color.value[2]

        showbox.glarea.queue_draw()

