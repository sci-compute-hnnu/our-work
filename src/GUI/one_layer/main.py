import gi
import numpy as np
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

from GUI.one_layer.Mesh._2D_Mesh.main import _2DMeshWindow
from GUI.one_layer.Mesh._3D_Mesh.main import _3DMeshWindow
from GUI.one_layer.Solver.BEM.main import BEMSolverWindow

class one_layer():

    def __init__(self, builder):


        self.file_button = builder.get_object("File")  # 获取对象id
        self.edit_button = builder.get_object("Edit")
        self.view_button = builder.get_object("View")
        self.sources_button = builder.get_object("Sources")
        self.mesh_button = builder.get_object("Mesh")
        self.solver_button = builder.get_object("Solver")
        self.file_button.set_active(False)  # 取消按钮的激活状态
        self.edit_button.set_active(False)
        self.view_button.set_active(False)
        self.sources_button.set_active(False)
        self.mesh_button.set_active(False)
        self.solver_button.set_active(False)


        """File下拉菜单"""
        # FileExit
        self.exit_item = builder.get_object("FileExit")
        self.open_button = builder.get_object("open")

        # recent file
        self.selected_list = []
        self.recent_File_button = builder.get_object("recentFile")
        self.options_menu = Gtk.Menu()
        self.recent_File_button.set_submenu(self.options_menu)


        '''View下拉菜单'''
        self.PB = builder.get_object("PB")
        self.PB.set_active(True)

        self.information = builder.get_object("information")
        self.information.set_active(True)


        """Edit下拉菜单"""
        '''edit--apply'''
        self.apply_button = builder.get_object("Apply")

        '''edit--reset'''
        self.reset_hide_button = builder.get_object("Reset")

        '''edit--delete'''
        self.delete_hide_button = builder.get_object("Delete")


        """Mesh下拉菜单"""
        self._2DMesh = builder.get_object("2Dmesh")
        self._3DMesh = builder.get_object("3Dmesh")

        """Solver下拉菜单"""
        self.BEM = builder.get_object('BEM')


        """其他需要使用的部件"""
        self.box1 = None
        self.noteboox = None
        self.two_layer = None
        self.three_layer = None


    # 加载其他需要使用的部件
    def loadWidget(self, box1, notebook, two_layer, three_layer):

        self.box1 = box1
        self.noteboox = notebook
        self.two_layer = two_layer
        self.three_layer = three_layer


    def information_active(self, button, box1):
        if self.information.get_active():
            box1.information_box.show()
        else:
            box1.information_box.hide()
        box1.box1_show()


    def PB_active(self, button, box1):
        if self.PB.get_active():
            box1.PB_box.show()
        else:
            box1.PB_box.hide()
        box1.box1_show()


    def delete_clicked(self, button, showbox,  box1):
        if showbox.should_draw and box1.Pp_box.get_property("visible"):
            showbox.should_draw = False
            showbox.glarea.queue_draw()
        if box1.PB_box.get_property("visible"):
            # 获取选中项的路径
            selection = box1.treeview.get_selection()
            model, path_list = selection.get_selected_rows()
            # 删除选中的项
            for path in reversed(path_list):
                iter = model.get_iter(path)
                model.remove(iter)


    def apply_clicked(self, button, showbox,  box1):
        if showbox.selected_file is not None and box1.Pp_box.get_property("visible"):
            showbox.should_draw = True
            showbox.glarea.queue_draw()
            if box1.PB_box.get_property("visible"):
                # 自动选中复选框按钮
                model = box1.treeview.get_model()
                model.foreach(lambda model, path, iter: self.on_checkbox_toggled(model, iter, True))

    def reset_clicked(self, button, showbox, box1):
        if box1.Pp_box.get_property("visible"):
            showbox.should_draw = False
            showbox.glarea.queue_draw()
            if box1.PB_box.get_property("visible"):
                # 自动选中复选框按钮
                model = box1.treeview.get_model()
                model.foreach(lambda model, path, iter: self.on_checkbox_toggled(model, iter, False))


    def on_checkbox_toggled(self, model, iter, is_checked):
        model.set_value(iter, 2, is_checked)

    # 第一层的open按钮(打开文件按钮)
    def open_clicked(self, button, filebutton):
        filebutton.clicked()



    " ---------- Mesh -----------"
    def open_2d_mesh_widonw(self, button):


        # 获取Mesh name 的默认名字

        _2DMeshWin = _2DMeshWindow()
        _2DMeshWin.loadWidget(self.box1)
        _2DMeshWin.run()

    def open_3d_mesh_widonw(self, button):

        _3DMeshWin = _3DMeshWindow()
        _3DMeshWin.run()


    " -----------Solver-----------"
    def open_BEM_solver_window(self, button):

        BEMSolverWin = BEMSolverWindow(self.box1, self.noteboox, self.two_layer, self.three_layer)
        BEMSolverWin.run()


