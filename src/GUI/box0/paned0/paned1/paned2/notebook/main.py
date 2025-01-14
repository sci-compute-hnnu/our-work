import gi
import re
import os
import chardet
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf,GtkSource

from GUI.box0.paned0.paned1.paned2.notebook.view_box import view_box
from GUI.box0.paned0.paned1.paned2.notebook.menu_box import meun_box
from GUI.box0.paned0.paned1.paned2.notebook.data_box import data_box
from GUI.box0.paned0.paned1.paned2.notebook.edit_box import edit_box


class notebook():

    def __init__(self, builder):


        self.notebook = builder.get_object("notebook")
        self.notebook.set_scrollable(True)  # 允许滚动标签页

        # 装放容器的列表 (容器指的是各个bbox(view_box, data_box, menu_box, edit_box))
        # 该字典的形式为 {key: [idx, [bbox1, bbox2, bbox3, ...]]} key是layout, #key idx是当前layout锁定的bbox的列表位置索引
        self.containerList = {}

        # 加号按钮，点击时添加新标签页
        self.add_button = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.MENU)
        self.add_button.show()

        # 在 notebook 的边上创建一个空白的盒子，将加号按钮放在里面
        self.notebook.set_action_widget(self.add_button, Gtk.PackType.START)

        # 一些其他配件
        self.box1 = None
        self.box3 = None
        self.three_layer = None

        # 当前的showbox
        self.showbox = None


    # 配置相关的其他部件
    def setting_other_widget(self, box1, box3, three_layer):

        self.box1 = box1
        self.box3 = box3
        self.three_layer = three_layer


    # 创建一个bbox num: 当前的标签页编号 func表示bbox的类型
    def creat_bbox(self, num, func):

        # 初始化bbox
        bbox = None

        if func == 0:  # 菜单box
            bbox = meun_box()

            """ menu_box的信号函数 """
            bbox.button1.connect('clicked', bbox.turn_to_otherbox, self, 1)
            bbox.button2.connect('clicked', bbox.turn_to_otherbox, self, 2)
            bbox.button3.connect('clicked', bbox.turn_to_otherbox, self, 3)


        elif func == 1:  # 网格引擎box
            bbox = view_box()


        elif func == 2:  # 显示数据box
            bbox = data_box()

            """ data_box的信号函数 """
            bbox.showing_combobox.connect("changed", bbox.on_showing_value, self.box1)
            bbox.attribute_combobox.connect("changed", bbox.on_attribute_value)
            bbox.precision_spinbox.connect("value-changed", bbox.on_precision_value)


        elif func == 3:  # 编辑界面box
            bbox = edit_box()

            """ edit_box的信号函数 """
            # 新建文件
            self.box3.new_file_button.connect("clicked", self.box3.newFile_clicked, bbox)
            # 保存文件
            self.box3.save_file_button.connect("clicked", self.box3.saveEdit_clicked, bbox)


        # 使任意 bbox 连接函数 实现关闭和分割
        bbox.close_box_button.connect("clicked", bbox.top_box_class.close_one_box, self)
        bbox.horizontal.connect("clicked", bbox.top_box_class.on_add_paned_clicked, self, Gtk.Orientation.HORIZONTAL)
        bbox.vertical.connect("clicked", bbox.top_box_class.on_add_paned_clicked, self, Gtk.Orientation.VERTICAL)

        # 设置每个窗口点击后的函数
        bbox.blue_edge_box.connect("button-press-event", self.choose_one_box, bbox)


        # 将生成的showbox添加到容器字典中

        if num not in self.containerList: # 如果该Layout没有(新建的Layout)
            self.containerList[num] = [0, [bbox]]
        else:  # 如果layout 已建好 (做分割操作)
            self.containerList[num][1].append(bbox)

        return bbox



    # 添加标签页后的行为
    def create_tab(self, title, func):

        # 提取序号
        num = int(re.search(r'\d+', title).group())

        # 生成一个bbox
        bbox = self.creat_bbox(num, func)

        # tab_box 初始化
        # 创建一个水平盒子来放置标签内容(Layout # ) 和 关闭按钮
        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        # 标签内容(Layout # )
        tab_label = Gtk.Label(label=title)
        # 关闭按钮 (标签页盒子上的)
        close_image = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_button = Gtk.Button.new()
        close_button.set_image(close_image)
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        close_button.set_focus_on_click(False)
        close_button.connect("clicked", self.close_current_tab, bbox.blue_edge_box)  # 关闭当前标签页

        tab_box.pack_start(tab_label, True, True, 0)
        tab_box.pack_start(close_button, False, False, 0)
        tab_box.show_all()

        # 设置一个新的外层Gtk.Box来放置bbox.blue_edge_box
        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer_box.pack_start(bbox.blue_edge_box, True, True, 0)

        # 添加标签页进入notebook
        self.notebook.append_page(outer_box, tab_box)

        # 添加标签页时的一些额外设置
        self.notebook.set_tab_reorderable(outer_box, True)  # 允许用户重新排序标签页
        self.notebook.set_tab_detachable(outer_box, True)  # 允许用户将标签页拖拽到新窗口
        self.notebook.show_all()
        self.notebook.set_current_page(self.notebook.get_n_pages() - 1)

        # 新建好一个标签页后, 就默认选择它
        self.choose_one_box( widget=None, event=None, bbox=bbox, force=True)



    # 切换标签页
    def from_on_switch_page(self, button, page, page_num):

        """预处理"""
        page_widget = self.notebook.get_nth_page(page_num)
        tab_box = self.notebook.get_tab_label(page_widget)
        tab_label = next(child for child in tab_box if isinstance(child, Gtk.Label))
        tab_text = tab_label.get_text()

        # 获取container的编号
        num = int(re.search(r'\d+', tab_text).group())

        if num not in self.containerList:  # 说明还没初始化完成
            return
        else:
            # 之前第page_num的layout 锁定的box
            idx = self.containerList[int(num)][0]
            prev_box = self.containerList[int(num)][1][idx]

            # 切换的时候默认点击该box
            self.choose_one_box(widget=None, event=None, bbox=prev_box, force=True)




    # 添加标签页并更新showbox
    def from_add_button(self, button):

        # 获取当前所有已存在的标签序号
        existing_numbers = self.get_existing_tab_numbers()
        # 找出缺失的最小序号
        new_tab_number = 1
        while new_tab_number in existing_numbers:
            new_tab_number += 1

        # 使用新序号创建标签 (func=0 创建菜单box)
        self.create_tab(f"Layout  #{new_tab_number}", func=0)



    # 关闭标签页
    def close_current_tab(self, widget, box):

        # 查找当前页面的索引位置
        page_num, num = self.find_Layout_Num(box)

        # 删除标签页
        self.notebook.remove_page(page_num)

        # 并将对应的container从containerList中移除
        del self.containerList[num]


    # 检查标签页的序号
    def get_existing_tab_numbers(self):
        existing_numbers = []
        for page_index in range(self.notebook.get_n_pages()):
            tab_box = self.notebook.get_nth_page(page_index)
            # 确保从正确的地方提取标签文本
            label = self.notebook.get_tab_label(tab_box).get_children()[0].get_text()
            # 使用正则表达式来寻找数字
            match = re.search(r'#(\d+)', label)
            if match:
                existing_numbers.append(int(match.group(1)))
        return existing_numbers


    # 按点击某个标签页后返回一个之前定位的showbox
    def on_switch_page(self, page, page_num):

        # 获取当前标签的文本
        tab_box = self.notebook.get_tab_label(page)
        label = tab_box.get_children()[0].get_text()

        # 提取序号
        num = int(re.search(r'\d+', label).group())

        # 获取之前layout锁定位的idx
        beforeIdx = self.containerList[num][0]

        # 定位到之前的shoubox
        showbox = self.containerList[num][1][beforeIdx]

        return showbox


    # 更换标签页  （EventBox的连接函数）  bbox为当前点击的bbox force: 是否强制点击box(新建tab 切换tab 点击menu按钮)
    def choose_one_box(self, widget, event, bbox, force=False):

        # 查找Layout num
        _, num = self.find_Layout_Num(bbox.blue_edge_box)

        # 之前记录的锁定box的idx
        fore_idx = self.containerList[num][0]

        if not(force or not self.containerList[num][1][fore_idx] == bbox):  # 如果之前锁定的就是现在点击的bbox 并且不是新键标签页
            return  # 直接跳过

        # 更新当前的showbox
        self.showbox = bbox
        # 设置显示蓝色边框 并关闭其他蓝色框
        self.showbox.top_box_class.view_blue_edge(self.showbox.blue_edge_box, self)

        # 如果更换到的是view_box
        if isinstance(self.showbox, view_box):

            # 设置第三层的按钮可点击
            self.three_layer.enable_three_layer()
            self.showbox.glarea.queue_draw()
            # 更换list_store_status的状态
            self.box1.from_list_change_status(self.showbox.list_store_state)


        # 如果更换到的是meun_box
        elif isinstance(self.showbox, meun_box):

            # 设置第三层的按钮不可点击
            self.three_layer.disable_three_layer()
            # 更换list_store_status的状态
            self.box1.from_list_change_status(self.showbox.list_store_state)


        # 如果更换到的是data_box
        elif isinstance(self.showbox, data_box):

            # 设置第三层的按钮不可点击
            self.three_layer.disable_three_layer()
            # 更换list_store_status的状态
            self.box1.from_list_change_status(self.showbox.list_store_state)


        # 如果更换到的是edit_box
        elif isinstance(self.showbox, edit_box):

            # 设置第三层的按钮不可点击
            self.three_layer.disable_three_layer()



        # 更新编号（每个layout的索引box的索引）
        for index, eachbox in enumerate(self.containerList[num][1]):

            # 找到与 self 地址相同的 box
            if eachbox == bbox:  # 将其锁定索引更换为为当前点击的bbox的的索引
                self.containerList[num][0] = int(index)

                break



    # 查找box位于notebook的那个标签页 (num 是 Layout后面的数字 page_num 是notebook的标签索引)
    def find_Layout_Num(self, blue_edge_box):

        parent = blue_edge_box
        while parent is not None:
            if isinstance(parent.get_parent(), Gtk.Notebook):  # 直至找到父级为notebook时
                break
            parent = parent.get_parent()  # 否则继续向上查找父级

        page_num = self.notebook.page_num(parent)
        page_widget = self.notebook.get_nth_page(page_num)  # <Gtk.Box>
        tab_box = self.notebook.get_tab_label(page_widget)
        tab_label = next(child for child in tab_box if isinstance(child, Gtk.Label))
        tab_text = tab_label.get_text()

        # 获取container的编号
        num = int(re.search(r'\d+', tab_text).group())

        return page_num, num


