import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

from Utils.Config.path import icon_dir

class Style():
    def __init__(self, builder):
        # 获取图标对象
        self.icons = {name: builder.get_object(name) for name in [
            "open_image", "download_image", "save_image", "reset_image", "undo_image",
            "redo_image", "color_image", "left1_image", "left2_image", "left3_image", "begin_stop_image",
            "right1_image", "right2_image", "right3_image", "circle_image", "camera_image",
            "no_camera_image", "legend_image", "gmsh_image", "zoomout_image", "zoomin_image",
            "+x_image", "-x_image", "+y_image", "-y_image", "+z_image", "-z_image",
            "axis_image", "right_90_image", "left_90_image", "project_image", "var_image", "plugin_image"
        ]}

    def set_icons(self, style_type):
        """ 根据样式加载图标 """

        simple_dir = icon_dir+'MainPage/Simple/'
        dark_dir = icon_dir+'MainPage/Dark/'

        # 统一的图标文件名（key 和文件名）
        icon_keys = [
            "open_image", "download_image", "save_image", "reset_image",
            "undo_image", "redo_image", "color_image",
            "left1_image", "left2_image", "left3_image",
            "begin_stop_image", "right1_image", "right2_image", "right3_image",
            "circle_image", "camera_image", "no_camera_image", "legend_image", "gmsh_image",
            "zoomout_image", "zoomin_image",
            "+x_image", "-x_image", "+y_image", "-y_image", "+z_image", "-z_image",
            "axis_image", "right_90_image", "left_90_image",
            "project_image", "var_image", "plugin_image"
        ]

        # 对应的文件名（注意顺序必须对齐 key）
        icon_files = [
            "open.png", "download.png", "save.png", "reset.png",
            "undo.png", "redo.png", "color.png",
            "left1.png", "left2.png", "left3.png",
            "begin_stop.png", "right1.png", "right2.png", "right3.png",
            "circle.png", "camera.png", "no_camera.png", "legend.png", "gmsh.png",
            "zoomout.png", "zoomin.png",
            "x+.png", "x-.png", "y+.png", "y-.png", "z+.png", "z-.png",
            "axis.png", "right_90.png", "left_90.png",
            "project.png", "variable.png", "plugin.png"
        ]

        # 构造路径字典
        icon_paths = {
            "Simple": {key: simple_dir + fname for key, fname in zip(icon_keys, icon_files)},
            "Dark": {key: dark_dir + fname for key, fname in zip(icon_keys, icon_files)},
        }

        for icon_name, path in icon_paths.get(style_type, {}).items():
            if "image" in icon_name:
                self.icons[icon_name].set_from_file(path)

    # 默认的样式 由于有内置图标单独配置
    def default_style(self):
        # 内置图标
        icon_paths_default = {
            "open_image": "document-open", "download_image": "document-save",
            "save_image": "document-save-as", "reset_image": "view-refresh",
            "undo_image": "edit-undo", "redo_image": "edit-redo", "color_image": "gtk-select-color",
            "left1_image": "media-skip-backward", "left2_image": "media-seek-backward",
            "left3_image": "pan-start-symbolic", "begin_stop_image": "media-playback-stop","right1_image": "media-skip-backward-symbolic-rtl",
            "right2_image": "media-seek-forward", "right3_image": "pan-end-symbolic",
            "circle_image": "media-playlist-repeat", "camera_image": "camera-photo-symbolic",
            "no_camera_image": "camera-disabled-symbolic", "legend_image": "image-x-generic",
            "gmsh_image": "gtk3-demo", "zoomout_image": "view-fullscreen-symbolic",
            "zoomin_image": "view-restore"
        }

        # 设置图标
        for icon_name, icon_file in icon_paths_default.items():
            if "image" in icon_name:
                self.icons[icon_name].set_from_icon_name(icon_file, Gtk.IconSize.BUTTON)


        default_dir = icon_dir + 'MainPage/Default/'

        # 图标 key 和对应文件名
        custom_icon_keys = [
            "+x_image", "-x_image", "+y_image", "-y_image",
            "+z_image", "-z_image", "axis_image",
            "right_90_image", "left_90_image",
            "project_image", "var_image", "plugin_image"
        ]

        custom_icon_files = [
            "x+.png", "x-.png", "y+.png", "y-.png",
            "z+.png", "z-.png", "axis.png",
            "right_90.png", "left_90.png",
            "project.png", "variable.png", "plugin.png"
        ]

        # 构建路径字典
        custom_image_paths = {
            key: default_dir + filename
            for key, filename in zip(custom_icon_keys, custom_icon_files)
        }

        # 设置图片
        for image_name, image_path in custom_image_paths.items():
            self.icons[image_name].set_from_file(image_path)

