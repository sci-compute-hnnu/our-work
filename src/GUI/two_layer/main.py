import datetime
import os
from enum import Enum

import cairo
import gi
import numpy as np

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from OpenGL import GL


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

        # 截图按钮
        self.camera = builder.get_object("camera")

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

        showbox.queue_draw()



    # 对glarea进行截图
    def on_screenshot_button_clicked(self, showbox,box1, widget):
        # 获取图像内容并保存为 PNG
        screenshot = self.take_screenshot(showbox,box1)

        # 获取默认的文件名
        default_filename = "screenshot.png"

        # 自定义命名（可以通过对话框或其他方式获取用户输入）
        custom_filename = self.get_custom_filename(default_filename)

        # 保存为 PNG
        screenshot.write_to_png(custom_filename)
        print(f"Screenshot saved as {custom_filename}")

    def take_screenshot(self, notebook, box1):
        # 获取当前页面的控件
        current_page = notebook.get_nth_page(notebook.get_current_page())  # 获取当前页
        children = current_page.get_children()  # 获取该页面的所有子控件

        eventbox = children[0]  # 获取第一个子控件 为eventbox

        # 获取 EventBox 中的子控件
        child_widget = eventbox.get_child() # 为box
        child = child_widget.get_children()[2] # 为glarea
        # 获取子控件的分配区域（即横纵坐标）
        allocation = child.get_allocation()
        width, height = allocation.width, allocation.height

        # 获取box1的宽
        box1_width = box1.get_allocated_width()
        x_start = box1_width + 9
        y_start = 24

        # 获取 OpenGL 渲染内容并保存为 cairo 表面
        screenshot_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cairo_context = cairo.Context(screenshot_surface)

        # 从 OpenGL 渲染读取内容并进行截图
        GL.glReadBuffer(GL.GL_FRONT)
        pixels = np.zeros((height, width, 4), dtype=np.uint8)
        GL.glReadPixels(x_start, y_start, width, height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pixels)

        # 将 OpenGL 渲染结果转换为 Cairo 图像
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[y, x]
                cairo_context.set_source_rgba(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
                cairo_context.rectangle(x, height - 1 - y, 1, 1)
                cairo_context.fill()

        return screenshot_surface


    def get_custom_filename(self, default_filename):
        # 指定相对路径的保存文件夹
        save_dir = os.path.join(os.getcwd(), "..", "..", "results", "photo")

        # 转换为绝对路径，确保跨平台兼容
        save_dir = os.path.abspath(save_dir)

        # 确保目录存在
        os.makedirs(save_dir, exist_ok=True)

        # 获取当前时间戳作为默认文件名的一部分
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        custom_filename = f"screenshot_{timestamp}.png"

        return os.path.join(save_dir, custom_filename)
