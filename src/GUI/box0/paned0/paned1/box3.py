import gi
import os
import chardet
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GtkSource


"""box3 用于放置打开最右侧工具栏后 显示的工具列表 (文件 内存变量 插件)"""

class box3:

    def __init__(self, builder):

        # 获取右侧框
        self.box3 = builder.get_object("box3")
        # 获取项目打开框
        self.folder_box = builder.get_object("folder_box")
        # 获取打开文件夹按钮
        self.open_folder_button = builder.get_object("open_folder_button")
        # 获取新建文件按钮
        self.new_file_button = builder.get_object("new_file_button")
        # 获取保存文件按钮
        self.save_file_button = builder.get_object("save_file_button")
        # 获取关闭文件框按钮
        self.close_folder_button = builder.get_object("close_folder_button")


        # 初始化管理器
        self.current_paned = None
        self.current_folder_path = None
        self.current_file_store = None


        # 初始化时先隐藏box3
        self.box3.hide()

        self.file_store = Gtk.TreeStore(str, str)
        self.file_tree_view = Gtk.TreeView(model=self.file_store)





    # 打开文件夹
    def on_open_folder_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="选择文件夹",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            folder_path = dialog.get_filename()
            self.open_folder(folder_path)
        dialog.destroy()



    # 打开文件夹并创建视图
    def open_folder(self, folder_path):
        if self.current_paned:
            self.current_paned.destroy()
            # 先刷新视图
            # self.refresh_folder_view(folder_path)

        self.current_folder_path = folder_path

        self.current_paned = self.create_paned_view(folder_path)
        self.folder_box.pack_start(self.current_paned, True, True, 0)
        self.current_paned.show()


    # 创建文件树视图
    def create_paned_view(self, folder_path):

        box = Gtk.Box()

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("项目", renderer, text=0)
        self.file_tree_view.append_column(column)

        file_scrolled_window = Gtk.ScrolledWindow()
        file_scrolled_window.set_min_content_width(200)
        file_scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        file_scrolled_window.add(self.file_tree_view)

        box.pack_start(file_scrolled_window, True, True, 0)

        self.current_file_store = self.file_store

        # 使用线程加载文件夹内容
        threading.Thread(target=self.list_files, args=(folder_path, self.file_store)).start()

        box.show_all()
        box.hide()

        return box


    # 点击文件时，显示文件内容
    def on_file_activated(self, tree_view, path, column, edit_box):
        model = tree_view.get_model()
        tree_iter = model.get_iter(path)
        file_path = model[tree_iter][1]
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='gbk') as file:
                    file_content = file.read()

        text_view = GtkSource.View()
        text_view.set_editable(True)
        text_view.set_show_line_numbers(True)  # 显示行号
        text_view.get_buffer().set_text(file_content)
        edit_box.set_language_for_file(file_path, text_view)

        edit_box.display_file_content(text_view, os.path.basename(file_path))



    # 文件夹路径下的文件列表
    def list_files(self, folder_path, file_store):
        def add_items(tree_iter, path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                child_iter = file_store.append(tree_iter, [item, item_path])
                if os.path.isdir(item_path):
                    add_items(child_iter, item_path)

        folder_iter = file_store.append(None, [os.path.basename(folder_path), folder_path])

        def update_ui():
            add_items(folder_iter, folder_path)
            return False

        GLib.idle_add(update_ui)




    # 新建文件
    def newFile_clicked(self, button, edit_box):
        text_view = GtkSource.View()
        text_view.set_editable(True)  # 可编辑
        text_view.set_show_line_numbers(True)  # 显示行号
        text_view.set_auto_indent(True)  # 自动缩进
        text_view.set_insert_spaces_instead_of_tabs(True)  # 用空格代替 tab
        text_view.set_tab_width(4)  # tab 宽度为 4
        src_buffer = GtkSource.Buffer()
        text_view.set_buffer(src_buffer)

        # 新建标签页
        edit_box.display_file_content(text_view, "Unnamed")

        edit_box.notebook.show_all()


    # 保存文件
    def saveEdit_clicked(self, button, edit_box):
        parent_window = button.get_toplevel()

        # 获取当前的标签页
        current_page = edit_box.notebook.get_current_page()
        if current_page == -1:
            return  # 没有打开的标签页

        # 获取当前活动的TextView
        current_box = edit_box.notebook.get_nth_page(current_page)
        text_view = current_box.get_children()[0]
        buffer = text_view.get_buffer()

        # 获取文件名，如果当前文件已经保存过则使用该路径
        current_file_path = getattr(self, 'current_file_path', None)

        # 文件选择对话框
        dialog = Gtk.FileChooserDialog(
            title="请选择保存文件的路径",
            parent=parent_window,
            action=Gtk.FileChooserAction.SAVE,
        )

        if current_file_path:
            dialog.set_filename(current_file_path)  # 设置默认文件名

        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()

            # 获取缓冲区的文本内容
            start_iter, end_iter = buffer.get_bounds()
            text = buffer.get_text(start_iter, end_iter, True)

            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(text)

            # 更新标签页的标签
            label_box = edit_box.notebook.get_tab_label(current_box)
            if label_box:
                label = label_box.get_children()[0]  # 获取标签
                label.set_text(os.path.basename(filename))

            # 更新当前文件的路径
            current_file_path = filename

            # 刷新文件内容和高亮
            self.refresh_file_view(filename, edit_box)

            # 如果保存文件的目录与当前文件夹相同，则刷新文件夹视图
            if os.path.dirname(current_file_path) == self.current_folder_path:
                self.refresh_folder_view(self.current_folder_path)

        dialog.destroy()


    # 刷新文件夹视图
    def refresh_folder_view(self, folder_path):
        # 清空当前文件视图
        self.current_file_store.clear()
        # 重新加载文件夹内容
        threading.Thread(target=self.list_files, args=(folder_path, self.current_file_store)).start()

    # 刷新文件视图
    def refresh_file_view(self, filename, edit_box):
        if edit_box.current_text_view:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    file_content = file.read()
            except UnicodeDecodeError:
                with open(filename, 'r', encoding='gbk') as file:
                    file_content = file.read()

            # 更新文件内容
            edit_box.current_text_view.get_buffer().set_text(file_content)
            # 应用高亮
            edit_box.set_language_for_file(filename, edit_box.current_text_view)


    # 关闭文件框
    def close_editFile_box(self, widget):

        self.box3.hide()




