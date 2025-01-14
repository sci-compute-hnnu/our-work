import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


"""box2 最右侧工具栏按钮"""

class box2:

    def __init__(self, builder):

        # 获取右部按钮
        self.file_button = builder.get_object("file_button")
        self.variable_button = builder.get_object("variable_button")
        self.plugin_button = builder.get_object("plugin_button")


    def file_button_clicked(self, button, paned1, box3):

        # 移除 paned_show 中的现有第二个部件
        children = paned1.get_children()
        if len(children) > 1:
            paned1.remove(children[1])

        paned1.add2(box3.box3)

        box3.folder_box.show_all()

        box3.box3.show()


    def variable_button_clicked(self, button, paned1, paned2, shell_box):

        # 移除 paned_show 中的现有第二个部件
        children = paned1.get_children()
        if len(children) > 1:
            paned1.remove(children[1])

        # 创建一个新的 Gtk.Box
        new_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        close_image = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_button = Gtk.Button.new()
        close_button.set_image(close_image)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.set_focus_on_click(False)
        close_button.connect("clicked", self.close_variable_box, new_box)

        # 创建一个水平的 Box 来放置关闭按钮
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Variables Table")
        header_box.pack_start(label, True, True, 0)
        header_box.pack_end(close_button, False, False, 0)


        # 创建一个分割线
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        # 创建树型结构来显示 self.variables
        variable_store = Gtk.ListStore(str, str, str)


        for var_name, (value, var_type) in shell_box.variables.items():

            variable_store.append([var_name, str(value), var_type.__name__])


        variable_tree_view = Gtk.TreeView(model=variable_store)
        renderer_text = Gtk.CellRendererText()

        # 创建两列: 变量名 、 值 、 类型
        column_name = Gtk.TreeViewColumn("Variable", renderer_text, text=0)
        column_value = Gtk.TreeViewColumn("Value", renderer_text, text=1)
        column_type = Gtk.TreeViewColumn("Type", renderer_text, text=2)

        variable_tree_view.append_column(column_name)
        variable_tree_view.append_column(column_value)
        variable_tree_view.append_column(column_type)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_width(300)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(variable_tree_view)
        scrolled_window.show_all()

        # 将 header_box 和树型结构添加到新的 Box 中
        new_box.pack_start(header_box, False, False, 0)
        new_box.pack_start(separator, False, False, 0)
        new_box.pack_start(scrolled_window, True, True, 0)

        paned1.add2(new_box)
        shell_box.update_variable_tree_view(paned1, paned2)
        new_box.show_all()


    # 关闭variable_box
    def close_variable_box(self, widget, box):

        box.hide()


