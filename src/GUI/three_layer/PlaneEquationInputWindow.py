import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


from Utils.Mesh.MeshSplitter import MeshSplitter

class SplitPlaneEquationWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../../ui/plane_equation.glade")  # 替换为你的 glade 文件名
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window1")
        self.window.connect("destroy", Gtk.main_quit)  # 确保程序退出时关闭主窗口

        self.entry_a = self.builder.get_object("entry_a")
        self.entry_b = self.builder.get_object("entry_b")
        self.entry_c = self.builder.get_object("entry_c")
        self.entry_d = self.builder.get_object("entry_d")

        # 设置默认值
        self.entry_a.set_text("-1.0")
        self.entry_b.set_text("1.0")
        self.entry_c.set_text("1.0")
        self.entry_d.set_text("-1.5")

        # 绑定按键事件
        for entry in [self.entry_a, self.entry_b, self.entry_c, self.entry_d]:
            entry.connect("key-press-event", self.on_key_press)

        self.button_confirm = self.builder.get_object("button_confirm")
        self.button_confirm.connect("clicked", self.on_button_confirm_clicked)


    def on_key_press(self, widget, event):
        cursor_pos = widget.get_position()  # 获取光标位置
        text_length = len(widget.get_text())  # 获取输入框文本的长度

        if event.keyval == Gdk.KEY_Right:
            if cursor_pos == text_length:  # 如果光标已经在最右侧
                if widget == self.entry_a:
                    self.entry_b.grab_focus()
                elif widget == self.entry_b:
                    self.entry_c.grab_focus()
                elif widget == self.entry_c:
                    self.entry_d.grab_focus()
                return True  # 阻止默认行为，防止触发系统警告音
        elif event.keyval == Gdk.KEY_Left:
            if cursor_pos == 0:  # 如果光标已经在最左侧
                if widget == self.entry_d:
                    self.entry_c.grab_focus()
                elif widget == self.entry_c:
                    self.entry_b.grab_focus()
                elif widget == self.entry_b:
                    self.entry_a.grab_focus()
                return True  # 阻止默认行为，防止系统警告音

        return False  # 允许其他按键的默认行为


    def load_widget(self, meshClass, box1):

        self.meshClass = meshClass  # 被切网格
        self.box1 = box1


    def on_button_confirm_clicked(self, button):
        a = self.entry_a.get_text()
        b = self.entry_b.get_text()
        c = self.entry_c.get_text()
        d = self.entry_d.get_text()
        cutting_plane = [float(a), float(b), float(c), float(d)]

        mesh_splitter = MeshSplitter(self.meshClass, cutting_plane)
        mesh_A, mesh_B, mesh_C = mesh_splitter.split()

        self.box1.load_Mesh(mesh_A, name='mesh_A')
        self.box1.load_Mesh(mesh_B, name='mesh_B')
        self.box1.load_Mesh(mesh_C, name='mesh_C')

        self.window.destroy()



    def run(self):
        self.window.show_all()
        Gtk.main()


