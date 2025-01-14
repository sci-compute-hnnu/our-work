import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib


from GUI.box0.paned0.paned1.paned2.shell_box import shell_box
from GUI.box0.paned0.paned1.paned2.notebook.main import notebook


"""main"""

"""用于可拉索shellBox 和 Notebook的"""

class paned2:

    def __init__(self, builder):

        # 获取paned2
        self.paned2 = builder.get_object("paned2")
        self.paned2.set_position(900)

        # 获取shell_box
        self.shell_box = shell_box(builder)

        # 获取notebook
        self.notebook = notebook(builder)


    def on_paned_position_changed(self, paned, param):
        # 获取当前分隔线的位置
        position = paned.get_position()

        # 定义最小和最大位置限制
        min_position = 600
        max_position = 1000

        # 限制分隔线在 min_position 和 max_position 之间
        if position < min_position:
            paned.set_position(min_position)
            position = min_position
        elif position > max_position:
            paned.set_position(max_position)
            position = max_position

        # 定义临界值
        first_threshold = min_position
        second_threshold = max_position

        # 处理 shell_box 的缩小和隐藏
        if position <= first_threshold:
            self.shell_box.shell_box.set_size_request(0, 0)  # 缩小到消失
        else:
            self.shell_box.shell_box.set_size_request(-1, -1)  # 恢复默认大小

        # 处理 notebook 的缩小和隐藏
        if position > first_threshold and position < second_threshold:
            # 上面缩小之后，notebook 开始缩小
            self.notebook.notebook.set_size_request(0, 0)  # 隐藏 notebook
        elif position >= second_threshold:
            self.notebook.notebook.set_size_request(-1, -1)  # 恢复 notebook 默认大小







