import gi
import os


gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from GUI.box0.paned0.paned1.box3 import box3
from GUI.box0.paned0.paned1.paned2.main import paned2

"""main"""

"""paned1 用于实现拉索 paned2(notebook 和 shell_box) 和 box3"""

class paned1:

    def __init__(self, builder):

        # 获取paned1
        self.paned1 = builder.get_object("paned1")
        self.paned1.set_position(1650)


        # 获取paned2 用于可拉索shellBox 和 Notebook的
        self.paned2 = paned2(builder)


        # 获取box3 用于放置打开最右侧工具栏后 显示的工具列表 (文件 内存变量 插件)
        self.box3 = box3(builder)


    def on_paned_position_changed(self, paned, param):

        min_position = 1250
        max_position = 2000
        position = paned.get_position()
        if position < min_position:
            paned.set_position(min_position)
        elif position > max_position:
            paned.set_position(max_position)




















