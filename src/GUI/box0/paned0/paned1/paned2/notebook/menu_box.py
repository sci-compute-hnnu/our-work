import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

import re
from GUI.box0.paned0.paned1.paned2.notebook.top_box_of_every_type import top_box_of_every_type

class meun_box():

    def __init__(self):

        # 创建top_box 和 blue_edge_box
        self.top_box_class = top_box_of_every_type()
        self.top_box = self.top_box_class.top_box
        self.blue_edge_box = self.top_box_class.blue_edge_box

        # top_box的第一排的三个按钮
        self.horizontal = self.top_box_class.horizontal
        self.vertical = self.top_box_class.vertical
        self.close_box_button = self.top_box_class.close_box_button


        # 创建垂直Box来垂直地排列标签和其他按钮
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.button_box.set_homogeneous(False)

        # 将button_box放置于top_box
        self.top_box.pack_start(self.button_box, True, True, 0)

        # 添加一个标签
        label = Gtk.Label(label="Select Function")
        self.button_box.pack_start(label, False, True, 0)

        button_width = 250  # 按钮宽度设置为250
        button_height = 40  # 按钮高度设为40

        # 创建网格引擎按钮
        self.button1 = Gtk.Button(label="Render View")
        self.button1.set_size_request(button_width, button_height)
        self.button_box.pack_start(self.button1, False, False, 0)

        # 创建显示数据的按钮
        self.button2 = Gtk.Button(label="SpreadSheet View")
        self.button2.set_size_request(button_width, button_height)
        self.button_box.pack_start(self.button2, False, True, 0)

        # 创建 Python 编辑器按钮
        self.button3 = Gtk.Button(label="Edit View")
        self.button3.set_size_request(button_width, button_height)
        self.button_box.pack_start(self.button3, False, True, 0)

        # 设置 button_box 的对齐方式
        self.button_box.set_valign(Gtk.Align.CENTER)
        self.button_box.set_halign(Gtk.Align.CENTER)


        # 初始化 list_store 的状态（先初始化为20个Fales (默认不超过20个网格) 后续会点击状态栏按钮时会更新）
        self.list_store_state = [False for _ in range(20)]




    # 转移到其他box
    def turn_to_otherbox(self, button, notebookClass, func):

        """ 预处理 """
        # 获取当前标签的文本
        Notebook = notebookClass.notebook
        page_num = Notebook.page_num(self.blue_edge_box)
        page_widget = Notebook.get_nth_page(page_num) # <Gtk.Box>
        tab_box = Notebook.get_tab_label(page_widget)
        tab_label = next(child for child in tab_box if isinstance(child, Gtk.Label))
        tab_text = tab_label.get_text()

        # 获取container的编号
        num = int(re.search(r'\d+', tab_text).group())

        # 添加需要跳转到的新的box
        new_box = notebookClass.creat_bbox(num, func)

        out_box = self.blue_edge_box.get_parent() # <Gtk.Box> (out_box)
        out_box.remove(self.blue_edge_box)
        out_box.add(new_box.blue_edge_box)
        out_box.show_all()


        # 将原本添加的menu_box 找出来并移除 （之前已经将新生成的new_box插入进去）
        for index, eachbox in enumerate(notebookClass.containerList[num][1]):

            # 找到与 self 地址相同的 menu_box
            if eachbox == self:
                # 移除原来的 menu_box
                notebookClass.containerList[num][1].pop(index)
                break

        # 当新建好一个new_box后 默认点击这个new_box
        notebookClass.choose_one_box(widget=None, event=None, bbox=new_box, force=True)


