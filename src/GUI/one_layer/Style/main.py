import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf


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
        icon_paths = {
            "Simple": {
                "open_image": "../../images/MainPage/Simple/open.png", "download_image": "../../images/MainPage/Simple/download.png",
                "save_image": "../../images/MainPage/Simple/save.png", "reset_image": "../../images/MainPage/Simple/reset.png",
                "undo_image": "../../images/MainPage/Simple/undo.png", "redo_image": "../../images/MainPage/Simple/redo.png",
                "color_image": "../../images/MainPage/Simple/color.png", "left1_image": "../../images/MainPage/Simple/left1.png",
                "left2_image": "../../images/MainPage/Simple/left2.png", "left3_image": "../../images/MainPage/Simple/left3.png",
                "begin_stop_image": "../../images/MainPage/Simple/begin_stop.png",
                "right1_image": "../../images/MainPage/Simple/right1.png", "right2_image": "../../images/MainPage/Simple/right2.png",
                "right3_image": "../../images/MainPage/Simple/right3.png", "circle_image": "../../images/MainPage/Simple/circle.png",
                "camera_image": "../../images/MainPage/Simple/camera.png", "no_camera_image": "../../images/MainPage/Simple/no_camera.png",
                "legend_image": "../../images/MainPage/Simple/legend.png", "gmsh_image": "../../images/MainPage/Simple/gmsh.png",
                "zoomout_image": "../../images/MainPage/Simple/zoomout.png", "zoomin_image": "../../images/MainPage/Simple/zoomin.png",
                "+x_image": "../../images/MainPage/Simple/x+.png", "-x_image": "../../images/MainPage/Simple/x-.png",
                "+y_image": "../../images/MainPage/Simple/y+.png", "-y_image": "../../images/MainPage/Simple/y-.png",
                "+z_image": "../../images/MainPage/Simple/z+.png", "-z_image": "../../images/MainPage/Simple/z-.png",
                "axis_image": "../../images/MainPage/Simple/axis.png", "right_90_image": "../../images/MainPage/Simple/right_90.png",
                "left_90_image": "../../images/MainPage/Simple/left_90.png", "project_image": "../../images/MainPage/Simple/project.png",
                "var_image": "../../images/MainPage/Simple/variable.png", "plugin_image": "../../images/MainPage/Simple/plugin.png"
            },
            "Dark": {
                "open_image": "../../images/MainPage/Dark/open.png", "download_image": "../../images/MainPage/Dark/download.png",
                "save_image": "../../images/MainPage/Dark/save.png", "reset_image": "../../images/MainPage/Dark/reset.png",
                "undo_image": "../../images/MainPage/Dark/undo.png", "redo_image": "../../images/MainPage/Dark/redo.png",
                "color_image": "../../images/MainPage/Dark/color.png", "left1_image": "../../images/MainPage/Dark/left1.png",
                "left2_image": "../../images/MainPage/Dark/left2.png", "left3_image": "../../images/MainPage/Dark/left3.png",
                "begin_stop_image": "../../images/MainPage/Dark/begin_stop.png",
                "right1_image": "../../images/MainPage/Dark/right1.png", "right2_image": "../../images/MainPage/Dark/right2.png",
                "right3_image": "../../images/MainPage/Dark/right3.png", "circle_image": "../../images/MainPage/Dark/circle.png",
                "camera_image": "../../images/MainPage/Dark/camera.png", "no_camera_image": "../../images/MainPage/Dark/no_camera.png",
                "legend_image": "../../images/MainPage/Dark/legend.png", "gmsh_image": "../../images/MainPage/Dark/gmsh.png",
                "zoomout_image": "../../images/MainPage/Dark/zoomout.png", "zoomin_image": "../../images/MainPage/Dark/zoomin.png",
                "+x_image": "../../images/MainPage/Dark/x+.png", "-x_image": "../../images/MainPage/Dark/x-.png",
                "+y_image": "../../images/MainPage/Dark/y+.png", "-y_image": "../../images/MainPage/Dark/y-.png",
                "+z_image": "../../images/MainPage/Dark/z+.png", "-z_image": "../../images/MainPage/Dark/z-.png",
                "axis_image": "../../images/MainPage/Dark/axis.png", "right_90_image": "../../images/MainPage/Dark/right_90.png",
                "left_90_image": "../../images/MainPage/Dark/left_90.png", "project_image": "../../images/MainPage/Dark/project.png",
                "var_image": "../../images/MainPage/Dark/variable.png", "plugin_image": "../../images/MainPage/Dark/plugin.png"
            }
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


        # 图片路径配置
        custom_image_paths = {
            "+x_image": "../../images/MainPage/Default/x+.png", "-x_image": "../../images/MainPage/Default/x-.png",
            "+y_image": "../../images/MainPage/Default/y+.png", "-y_image": "../../images/MainPage/Default/y-.png",
            "+z_image": "../../images/MainPage/Default/z+.png", "-z_image": "../../images/MainPage/Default/z-.png",
            "axis_image": "../../images/MainPage/Default/axis.png",
            "right_90_image": "../../images/MainPage/Default/right_90.png",
            "left_90_image": "../../images/MainPage/Default/left_90.png",
            "project_image": "../../images/MainPage/Default/project.png",
            "var_image": "../../images/MainPage/Default/variable.png",
            "plugin_image": "../../images/MainPage/Default/plugin.png"
        }

        # 设置图片
        for image_name, image_path in custom_image_paths.items():
            self.icons[image_name].set_from_file(image_path)

