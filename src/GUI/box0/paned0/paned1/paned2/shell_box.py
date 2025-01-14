import gi
from gi.repository import Gtk, Gdk
gi.require_version('Gtk', '3.0')

from Shell.ShellCommand import CommandProcessor

""" shell_box 用于放命令行"""

class shell_box:

    def __init__(self, builder):

        # 获取View中的Shell选项
        self.Shell = builder.get_object("Shell")

        # 获取shell_box
        self.shell_box = builder.get_object("shell_box")


        # 获取shell_box 的关闭按钮
        self.shell_box_close_button = builder.get_object("shell_close")

        # 获取shell_box中的text_box 用于放置可滑动的文本显示区域
        self.text_box = builder.get_object("text_box")

        # 创建一个多行文本显示区域
        self.scrolleds_box = Gtk.ScrolledWindow()
        self.text_view = Gtk.TextView()
        # 设置文本的换行模式为按单词换行（WORD 模式）
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        # 允许编辑文本
        self.text_view.set_editable(True)
        self.text_box.pack_start(self.scrolleds_box, True, True, 0)
        self.scrolleds_box.add(self.text_view)

        # 显示初始提示
        self.append_to_text_view(">>> ")

        # 初始化Command指令
        self.processor = CommandProcessor()
        self.variables = self.processor.variables


    # 将新的文本添加到textview后面 而不覆盖之前的文本
    def append_to_text_view(self, text):
        buffer = self.text_view.get_buffer()
        buffer.insert(buffer.get_end_iter(), text)


    # shell_box的关闭按钮连接函数
    def shell_close(self, button, one_layer):
        self.shell_box.hide()
        one_layer.shell.set_active(False)  # 第一层的关闭按钮




    # View中Shell选项的开关
    def on_shell_toggled(self, widget, paned2):
        if self.Shell.get_active():
            # 显示shell_box，并调整分隔线位置以显示上半部分
            self.shell_box.show_all()
            paned2.set_position(paned2.get_position() + self.shell_box.get_allocated_height())
        else:
            # 隐藏shell_box，并调整分隔线位置以回收上半部分的空间
            paned2.set_position(paned2.get_position() - self.shell_box.get_allocated_height())
            self.shell_box.hide()


    # 绑定键盘事件的回调函数 即按回车键时，执行该条件下的代码
    def on_key_press(self, widget, event, paned1, paned2):
        if event.keyval == Gdk.KEY_Return:
            self.execute_command(paned1, paned2)
            return True  # 阻止进一步处理事件（防止插入新行）


    # 执行命令
    def execute_command(self, paned1, paned2):
        buffer = self.text_view.get_buffer()
        start_iter, end_iter = buffer.get_bounds()
        text = buffer.get_text(start_iter, end_iter, True)
        # 找到最后一个输入行的开始和结束位置
        last_line_start = text.rfind('\n>>> ') + len('\n')
        last_line_end = len(text)
        last_command = text[last_line_start:last_line_end].strip()

        if last_command:
            # 清理命令中的 '>>>'
            last_command = last_command.replace('>>> ', '')
            result = self.processor.process_command(last_command)

            # 将结果追加到文本显示区域
            self.append_to_text_view(f"\n{result}\n>>> ")

        self.update_variable_tree_view(paned1, paned2)



    # 在shell_box中添加命令后的 对box2中变量树型视图进行更新
    # def update_variable_tree_view(self, paned1):
    #     # 获取box2中的tree_view
    #     tree_view = paned1.get_children()[1].get_children()[2].get_children()[0]
    #
    #     # 获取tree_view
    #     if tree_view:
    #         model = tree_view.get_model()
    #         # 清空模型中的数据
    #         model.clear()
    #         # 更新模型中的数据
    #         for var_name, (value, var_type) in self.variables.items():
    #             # 将变量名、值和类型更新到模型中
    #             model.append([var_name, str(value), var_type.__name__])
    def update_variable_tree_view(self, paned1, paned2):
        # 获取当前树形视图的模型
        children = paned1.get_children()
        if len(children) > 1:
            new_box = children[1]
            # 查找当前的 Gtk.TreeView
            tree_view = None
            for child in new_box.get_children():
                if isinstance(child, Gtk.ScrolledWindow):
                    tree_view = child.get_child()
                    break
            if tree_view:
                model = tree_view.get_model()
                # 清空模型中的数据
                model.clear()
                # 更新模型中的数据
                for var_name, (value, var_type) in self.variables.items():
                    # 将变量名、值和类型更新到模型中
                    model.append([var_name, str(value), var_type.__name__])


