import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GtkSource

from GUI.box0.paned0.paned1.paned2.notebook.top_box_of_every_type import top_box_of_every_type

class edit_box():

    def __init__(self):

        # 创建top_box 和 blue_edge_box
        self.top_box_class = top_box_of_every_type()
        self.top_box = self.top_box_class.top_box
        self.blue_edge_box = self.top_box_class.blue_edge_box

        # top_box的第一排的三个按钮
        self.horizontal = self.top_box_class.horizontal
        self.vertical = self.top_box_class.vertical
        self.close_box_button = self.top_box_class.close_box_button

        # 创建一个 Box 用于包裹 notebook (使得蓝色边框清晰可见)
        self.inner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.inner_box.set_margin_start(3)  # 左边距
        self.inner_box.set_margin_end(3)  # 右边距
        self.inner_box.set_margin_top(0)  # 上边距
        self.inner_box.set_margin_bottom(3)  # 下边距
        self.notebook = Gtk.Notebook()
        self.inner_box.pack_start(self.notebook, True, True, 0)
        self.top_box.pack_start(self.inner_box, True, True, 0)

        # 创建语言管理器
        self.current_text_view = None

        self.manager = GtkSource.LanguageManager()



    # 当点击关闭标签页的按钮时
    def on_tab_close_button_clicked(self, button, child):
        page_num = self.notebook.page_num(child)
        if page_num != -1:
            self.notebook.remove_page(page_num)


    # 显示文件内容
    def display_file_content(self, text_view, label_text):
        # 创建关闭按钮
        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.add(Gtk.Image.new_from_icon_name("window-close", Gtk.IconSize.MENU))

        # 创建标签
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=label_text)
        label_box.pack_start(label, True, True, 0)
        label_box.pack_start(close_button, False, False, 0)
        label_box.show_all()

        # 创建可滑动的窗口
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(text_view)

        # 添加到标签页内
        self.notebook.append_page(scrolled_window, label_box)
        self.notebook.set_tab_reorderable(scrolled_window, True)

        # 设置可滚动
        self.notebook.set_scrollable(True)

        # 添加关闭按钮事件
        close_button.connect("clicked", self.on_tab_close_button_clicked, scrolled_window)
        self.notebook.show_all()
        self.notebook.set_current_page(-1)
        self.current_text_view = text_view


    # 设置文件显示高亮
    def set_language_for_file(self, file_path, text_view):
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.cpp': 'cpp',
            '.c': 'c',
            '.html': 'html',
            '.lua': 'lua',
            '.java': 'java',
            '.css': 'css',
        }
        _, ext = os.path.splitext(file_path)
        language = self.manager.get_language(ext_map.get(ext, 'text'))
        text_view.get_buffer().set_language(language)

