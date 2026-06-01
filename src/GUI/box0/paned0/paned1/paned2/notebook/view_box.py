import gi

from GUI.box0.paned0.paned1.paned2.notebook.top_box_of_every_type import top_box_of_every_type

from gi.repository import Gtk
gi.require_version('Gtk', '3.0')

from Post.BaseGLArea import base_glarea


class view_box():

    def __init__(self):

        # 创建top_box 和 blue_edge_box
        self.top_box_class = top_box_of_every_type()
        self.top_box = self.top_box_class.top_box
        self.blue_edge_box = self.top_box_class.blue_edge_box

        # top_box的第一排的三个按钮
        self.horizontal = self.top_box_class.horizontal
        self.vertical = self.top_box_class.vertical
        self.close_box_button = self.top_box_class.close_box_button

        # 创建一个 Box 用于包裹 GLArea (使得蓝色边框清晰可见)
        self.inner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.inner_box.set_margin_start(3)  # 左边距
        self.inner_box.set_margin_end(3)  # 右边距
        self.inner_box.set_margin_top(0)  # 上边距
        self.inner_box.set_margin_bottom(3)  # 下边距
        self.glareaClass = base_glarea()
        self.glarea = self.glareaClass.glarea
        self.glarea.connect('render', self.on_render)
        self.inner_box.pack_start(self.glarea, True, True, 0)
        self.top_box.pack_start(self.inner_box, True, True, 0)


        # 初始化list_store的状态（先初始化为20个False(默认不超过20个网格) 后续点击状态按钮是会自动更新）
        self.list_store_state = [False for _ in range(20)]

        # 初始化color_opt
        self.color_opt_list = [' ']
        # 初始化type_opt_list
        self.type_opt_list = [' ']

        self.color_opt = ' '  # 默认绘制方式是Neutral Mode
        self.type_opt = ' '

        # 当前要绘制的网格索引列表（空 = 只渲染背景）
        self.should_draw = []
        # 缓存的网格对象列表，供 color_opt 切换时重建用
        self.current_mesh_list = []


    def on_render(self, area, contex):

        if not self.should_draw:  # 只渲染背景
            self.glareaClass.on_render_background(area, contex)

        else:
            self.glareaClass.on_render(area, contex)


    def on_realize(self, mesh_list=None, rotation_matrix=None):

        if mesh_list is not None:
            self.current_mesh_list = mesh_list
            self.glareaClass.var_opt = self.color_opt
            self.glareaClass.initialize_shared(mesh_list, rotation_matrix=rotation_matrix)
        elif rotation_matrix is not None:
            self.glareaClass.rotation_matrix = rotation_matrix.astype('float32')

    def rebuild_for_color_change(self):
        """color_opt 切换时重建所有网格的 VBO（var 数据需更新）。"""
        if self.current_mesh_list:
            self.glareaClass.var_opt = self.color_opt
            self.glareaClass.rebuild_all_bundles(self.current_mesh_list)


    def queue_draw(self):

        self.glarea.queue_draw()

    def get_last_rotation(self):

        return self.glareaClass.rotation_matrix

    def get_current_mesh(self):

        bundles = self.glareaClass.mesh_bundles
        if not bundles:
            return None
        first_idx = min(bundles.keys())
        return bundles[first_idx].get('mesh', None)
