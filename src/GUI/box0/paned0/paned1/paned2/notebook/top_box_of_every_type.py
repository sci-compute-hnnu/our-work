import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import re


class top_box_of_every_type():
    def __init__(self):

        # top_box
        self.top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # 蓝色边框box
        self.blue_edge_box = Gtk.EventBox()
        self.blue_edge_box.add(self.top_box)


        # 第一层的三个按钮 (水平, 竖直分割, 关闭)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        horizontal_image = Gtk.Image.new_from_icon_name("sidebar-show-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        self.horizontal = Gtk.Button()  # 创建空白按钮
        self.horizontal.set_image(horizontal_image)  # 将图像添加到按钮
        self.horizontal.set_relief(Gtk.ReliefStyle.NONE)

        vertical_image = Gtk.Image.new_from_icon_name("scanner-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        self.vertical = Gtk.Button()
        self.vertical.set_image(vertical_image)
        self.vertical.set_relief(Gtk.ReliefStyle.NONE)

        close_image = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        self.close_box_button = Gtk.Button()
        self.close_box_button.set_image(close_image)
        self.close_box_button.set_relief(Gtk.ReliefStyle.NONE)

        # 调整按钮的大小请求,使得按钮栏变窄
        self.horizontal.set_size_request(40, 30)  # 设置宽度和高度
        self.vertical.set_size_request(40, 30)
        self.close_box_button.set_size_request(40, 30)

        button_box.pack_end(self.close_box_button, False, False, 0)
        button_box.pack_end(self.vertical, False, False, 0)
        button_box.pack_end(self.horizontal, False, False, 0)
        button_box.set_homogeneous(False)

        # 添加按钮层到top_box
        self.top_box.pack_start(button_box, False, False, 0)
        button_box.set_size_request(-1, -1)

        # 第二层 添加一个分割线
        self.top_box.pack_start(Gtk.HSeparator(), False, False, 0)


        # 控制部件水平和垂直的扩展行为
        self.top_box.set_hexpand(True)
        self.top_box.set_vexpand(True)




    # 显示蓝色边框, 每次更换show_box时调用(添加标签页, 更换标签页, 分割标签页)
    def view_blue_edge(self, widget, notebookClass):
        # 蓝色边款的样式设置部分
        css_provider = Gtk.CssProvider()
        css = """
                            .highlight {
                                border: 2px solid blue;
                            }
                        """
        css_provider.load_from_data(css.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # 先为之前的所有bbox取消高亮
        for num, box_list in notebookClass.containerList.items():
            # 遍历 box_list[1] 中的所有元素
            for eachbox in box_list[1]:
                # 获取每个 box 的样式上下文
                style_context = eachbox.blue_edge_box.get_style_context()
                # 如果样式上下文中包含高亮样式类 "highlight"，则移除它
                if style_context.has_class("highlight"):
                    style_context.remove_class("highlight")


        # 为当前点击的 EventBox 添加高亮样式
        widget.get_style_context().add_class("highlight")





    # 点击分割按钮
    def on_add_paned_clicked(self, button, notebookClass, orientation):

        # 当点击分割按钮时 默认点击该按钮所在的bbox
        for num, box_list in notebookClass.containerList.items():
            # 遍历 box_list[1] 中的所有元素
            for eachbbox in box_list[1]:
                if self.blue_edge_box == eachbbox.blue_edge_box:  # 找到该box
                    notebookClass.choose_one_box(widget=None, event=None, bbox=eachbbox, force=True)


        # 获取标签页Layout num
        _, num = notebookClass.find_Layout_Num(notebookClass.showbox.blue_edge_box)

        # 新建一个分割后新生成的menubox
        new_menubox = notebookClass.creat_bbox(num=num, func=0)

        page_widget = notebookClass.showbox.blue_edge_box.get_parent()  # outbox
        childbox = page_widget.get_children()[0]  # <Gtk.EventBox> blue_edge_box

        # remove 原来的blue_edge_box
        page_widget.remove(childbox)

        # 同样创建out_box放置两个切分后的box
        outer_box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer_box1.pack_start(childbox, True, True, 0)
        outer_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer_box2.pack_start(new_menubox.blue_edge_box, True, True, 0)

        # 创建新的 Paned 容器，允许用户指定方向
        paned = Gtk.Paned(orientation=orientation)

        # 将 childbox 放置在 paned 的左侧
        paned.add1(outer_box1)
        paned.add2(outer_box2)
        # 获取out_box的尺寸

        if orientation == Gtk.Orientation.HORIZONTAL:  # 竖向分割时 取width二分之一为分割线位置
            width = page_widget.get_allocated_width()
            paned.set_position(width/2)
        else:   # 横向分割时 取height二分之一位置为分割线位置
            height = page_widget.get_allocated_height()
            paned.set_position(height / 2)

        page_widget.add(paned)
        page_widget.show_all()

        # 默认点击新生成的bbox
        notebookClass.choose_one_box(widget=None, event=None, bbox=new_menubox, force=True)



    # ,当点击showbox关闭按钮时, 切换到menubox
    def close_one_box(self, button, notebookClass):

        """ 预处理 """
        _, num = notebookClass.find_Layout_Num(self.blue_edge_box)

        # 判断该box是否是分割后的box (父级的父级是否是paned 第一个父级是outbox)
        parent = self.blue_edge_box.get_parent().get_parent()

        if isinstance(parent, Gtk.Paned):  # 如果是 则直接关闭该box (将paned替换为paned中另一个未点击关闭按钮的box)

            # 找到Paned中没有点击关闭按钮的另一个bbox
            another_box = None
            close_box = None
            bbox1 = parent.get_children()[0].get_children()[0]  # Eventbox (blue_edge_box)
            bbox2 = parent.get_children()[1].get_children()[0]

            if self.blue_edge_box == bbox1:
                another_box = bbox2   # get 另一个未点击关闭按钮的box
                close_box = bbox1
            elif self.blue_edge_box == bbox2:
                another_box = bbox1
                close_box = bbox2

            page_widget = parent.get_parent()  # outbox
            childbox = page_widget.get_children()[0]  # <Gtk.Paned>

            # 将another_box从其父级中移除
            parent = another_box.get_parent()
            if parent is not None:
                parent.remove(another_box)

            # remove 原来的Paned 添加another_box
            page_widget.remove(childbox)
            page_widget.add(another_box)
            page_widget.show_all()

            # 更新containList
            # 将原本点击关闭按钮的box移除 并获取其blue_edge_box 与another_box 相同的bbox 并保存
            another_bbox = None
            for index, eachbox in enumerate(notebookClass.containerList[num][1]):

                # 找到与 其中blue_edge_box  与 close_box 地址相同的
                if eachbox.blue_edge_box == close_box:
                    # 将其移除
                    notebookClass.containerList[num][1].pop(index)

                # 找到与another_box 地址相同的bbox.blue_edge_box
                if eachbox.blue_edge_box == another_box:
                    another_bbox = eachbox

            # 点击another_bbox
            notebookClass.choose_one_box(widget=None, event=None, bbox=another_bbox, force=True)

        else:  # 如果该标签页只有一个box 未进行分割 则将该box跳转至menubox

            # 新建menu_box
            new_menubox = notebookClass.creat_bbox(num, 0)

            out_box = self.blue_edge_box.get_parent()  # <Gtk.Box> (out_box)
            out_box.remove(self.blue_edge_box)
            out_box.add(new_menubox.blue_edge_box)
            out_box.show_all()

            # 更新containerList
            # 将原本添加的bbox 找出来并移除 （之前已经将新生成的menu_box插入进去, 在上面的的creat_bbox中实现）
            for index, eachbox in enumerate(notebookClass.containerList[num][1]):

                # 找到与 self 地址相同的 box
                if eachbox == notebookClass.showbox:
                    # 移除原来的 box
                    notebookClass.containerList[num][1].pop(index)
                    break

            # 当新建好一个menu_box后 默认点击这个menu_box
            notebookClass.choose_one_box(widget=None, event=None, bbox=new_menubox, force=True)


