import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import os
from Utils.Mesh.MeshReader import MeshReader


class box1:

    def __init__(self, builder):


        self.box1 = builder.get_object("box1")


        """ 获取Pipline Browser"""
        self.PB_box = builder.get_object("PB_box")
        self.PB_close_button = builder.get_object("PB_close")

        """ 获取到information"""
        self.information_box = builder.get_object("information_box")
        self.infotextview = builder.get_object('infotextview')   # 显示文本的textview
        self.information_close_button = builder.get_object("information_close")


        # 设置网格显示列表
        self.list_store = Gtk.ListStore(bool, str)

        # 创建可滚动的窗口
        self.scrolleds = builder.get_object("scrolleds")
        self.scrolleds.set_size_request(-1, 350)

        # 获取box1_paned
        self.box1_paned = builder.get_object("box1_paned")
        self.box1_paned.set_position(400)

        # 绘制网格队列信息
        self.treeview = builder.get_object("tree_view")
        self.treeview.set_rubber_banding(True)

        self.treeview.set_model(self.list_store)

        # 添加按钮列
        self.renderer_toggle = Gtk.CellRendererToggle()
        column_toggle = Gtk.TreeViewColumn("Button", self.renderer_toggle, active=0)
        self.treeview.append_column(column_toggle)

        # 添加网格名字列
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Text", renderer_text, text=1)
        self.treeview.append_column(column_text)


        """ 储存网格信息的列表 """

        self.faceMeshList = []


    def box1_show(self):
        if self.PB_box.get_property("visible"):
            self.box1.show()
        else:
            self.box1.hide()

    def PB_close(self, button, one_layer):
        self.PB_box.hide()   # PB_box
        one_layer.PB.set_active(False)    # 第一层的关闭按钮
        self.box1_show()    # PB_box上的x


    def information_close(self, button, one_layer):
        self.information_box.hide()   # information_box
        one_layer.information.set_active(False)   # 第一层的关闭按钮
        self.box1_show()    # information_box上的x


    def delete_clicked(self, button, showbox):

        if self.PB_box.get_property("visible"):
            # 获取选中项的路径
            selection = self.treeview.get_selection()
            model, path_list = selection.get_selected_rows()
            # 删除选中的项
            for path in reversed(path_list):
                iter = model.get_iter(path)
                model.remove(iter)    # path 就是0 , 1 ,2 索引 每次path_list只有一个
                self.faceMeshList.pop(int(str(path)))    # 移除该面网格数据

            showbox.should_draw = self.find_true_row()
            showbox.glarea.queue_draw()

    def apply_clicked(self, button, showbox):

        if self.PB_box.get_property("visible"):
            # 获取所有的项
            model = self.treeview.get_model()

            # 首先设置所有项为False
            def set_all_to_false(model, path, iter):
                model.set_value(iter, 0, False)

            model.foreach(set_all_to_false)

            # 获取选中项的路径
            selection = self.treeview.get_selection()
            model, path_list = selection.get_selected_rows()
            # 打勾选中的项
            for path in path_list:
                iter = model.get_iter(path)
                model.set_value(iter, 0, True)

            # 更新绘制
            showbox.should_draw = self.find_true_row()
            showbox.on_realize(self)
            showbox.glarea.queue_draw()


    def reset_clicked(self, button, showbox):

        if self.PB_box.get_property("visible"):
            # 获取选中项的路径
            selection = self.treeview.get_selection()
            model, path_list = selection.get_selected_rows()
            # 取消打勾选中的项
            for path in reversed(path_list):
                iter = model.get_iter(path)
                model.set_value(iter, 0, False)

            showbox.should_draw = self.find_true_row()
            showbox.glarea.queue_draw()


    # information框打印信息
    def info_print(self, info):

        # 设置information字体
        buffer = self.infotextview.get_buffer()
        tag_table = buffer.get_tag_table()
        font_tag = tag_table.lookup("font_tag")

        if font_tag is None:
            font_tag = Gtk.TextTag.new("font_tag")
            font_tag.set_property("font", "Monospace 10")
            tag_table.add(font_tag)

        end_iter = buffer.get_end_iter()
        buffer.insert_with_tags(end_iter, info, font_tag)


    # 更新状态栏打勾和是否绘制
    def on_toggle_button_toggled(self, cell, path_str, showbox):

        # 将路径字符串转换为TreePath对象
        path = Gtk.TreePath(path_str)

        # step1: 更新当前行的勾选状态
        current_iter = self.list_store.get_iter(path)
        self.list_store[current_iter][0] = not self.list_store.get_value(current_iter, 0)

        # step2: 获取当前行的True or False值
        value = self.list_store.get_value(current_iter, 0)

        # step3: 如果当前是打勾状态，则取消其他的勾选
        if value:
            # 迭代 ListStore 中的所有其他行
            for row in self.list_store:
                # 如果不是当前行，则取消勾选
                if row.path != path:
                    self.list_store[row.iter][0] = False


        # step4: 以当前状态记录并更新showbox的list_store_state
        showbox.list_store_state = self.record_status_from_list_store()


        # step5: 更新是否绘制, 以及绘制谁
        if value:

            showbox.should_draw = self.find_true_row()
            showbox.on_realize(self)
            showbox.glarea.queue_draw()
        else:

            showbox.should_draw = self.find_true_row()
            showbox.glarea.queue_draw()


    # 找到为True的索引 (该阶段为True的一个)
    def find_true_row(self):
        # 遍历list_store中的所有条目
        for i, row in enumerate(self.list_store):
            # 如果这一行的状态为True，则返回它的索引
            if row[0]:
                return i
        return -1


    # 读取网格文件, 并存入列表
    def load_Mesh_file(self, filename):

        # 存入网格列表
        mesh = MeshReader(filename)
        self.faceMeshList.append(mesh)

        # 更新box1的list_store
        name_only = os.path.basename(filename)
        self.list_store.append([False, name_only])


    def load_Mesh(self, mesh, name='mesh'):

        # 存入网格列表
        self.faceMeshList.append(mesh)

        self.list_store.append([False, name])



    # 批量更改list_store的状态
    def from_list_change_status(self, status_list):
        # 更新list_store中每个条目的状态为status_list中对应的值
        for row, status in zip(self.list_store, status_list):
            row[0] = status


    # 加个list_store的状态存入列表
    def record_status_from_list_store(self):

        status_list = [item[0] for item in self.list_store]
        return status_list



    # 实现拉索的空间范围
    def on_paned_position_changed(self, paned, param):
        # 获取当前分隔线的位置
        position = paned.get_position()

        # 定义最小和最大位置限制
        min_position = 400
        max_position = 700

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
            self.PB_box.set_size_request(0, 0)  # 缩小到消失
        else:
            self.PB_box.set_size_request(-1, -1)  # 恢复默认大小

        # 处理 notebook 的缩小和隐藏
        if position > first_threshold and position < second_threshold:
            # 上面缩小之后，notebook 开始缩小
            self.information_box.set_size_request(0, 0)  # 隐藏
        elif position >= second_threshold:
            self.information_box.set_size_request(-1, -1)  # 恢复默认大小



