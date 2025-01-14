import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from GUI.box0.box2 import box2
from GUI.box0.paned0.main import paned0

"""main"""

"""box0 包含paned0 和 box2（最右侧工具栏按钮）"""

class box0:

    def __init__(self, builder):

        # 获取box2 （最右侧工具栏按钮）
        self.box2 = box2(builder)

        # 获取paned0
        self.paned0 = paned0(builder)


