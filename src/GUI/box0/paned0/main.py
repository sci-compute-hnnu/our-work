import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from GUI.box0.paned0.box1 import box1
from GUI.box0.paned0.paned1.main import paned1

"""main"""

"""paned0 实现拉索box1（information 和 pB）和 paned1（用于实现拉索 paned2(notebook 和 shell_box) 和 box3）"""

class paned0:

    def __init__(self, builder):

        # 获取box1 （information 和 pB）
        self.box1 = box1(builder)

        # 获取paned1 （用于实现拉索 paned2(notebook 和 shell_box) 和 box3
        self.paned1 = paned1(builder)

        # 获取paned0
        self.paned0 = builder.get_object("paned0")


    def on_paned_position_changed(self, paned, param):

        min_position = 300
        max_position = 900
        position = paned.get_position()
        if position < min_position:
            paned.set_position(min_position)
        elif position > max_position:
            paned.set_position(max_position)