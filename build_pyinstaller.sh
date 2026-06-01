#!/bin/bash
# ============================================================
# FEM/BEM 可视化平台 - PyInstaller 打包脚本 (v1.0)
# 运行: bash build_pyinstaller.sh
# 输出: dist/FEM-BEM-Viewer/
# ============================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$PROJECT_ROOT/Gtk3/bin/python3"
APP_NAME="FEM-BEM-Viewer"
ENTRY="$PROJECT_ROOT/src/GUI/main.py"
SPEC="$PROJECT_ROOT/$APP_NAME.spec"
BUILD_DIR="$PROJECT_ROOT/build_pyinstaller"
DIST_DIR="$PROJECT_ROOT/dist"

echo "============================================"
echo "  FEM/BEM 可视化平台 - PyInstaller 打包"
echo "============================================"
echo "  Python: $PYTHON"
echo "  Entry:  $ENTRY"
echo "  Output: $DIST_DIR/$APP_NAME"
echo "============================================"

# ---- 清理 ----
echo "[1/5] 清理旧构建..."
rm -rf "$BUILD_DIR" "$DIST_DIR/$APP_NAME" "$SPEC"

# ---- 安装 PyInstaller ----
echo "[2/5] 检查 PyInstaller..."
$PYTHON -m pip install pyinstaller --quiet 2>/dev/null || $PYTHON -m pip install pyinstaller
echo "  -> $($PYTHON -m PyInstaller --version)"

# ---- 生成 spec ----
echo "[3/5] 生成 spec..."
export PROJECT_ROOT APP_NAME ENTRY
$PYTHON << 'GENSPEC'
import os, sys

prj = os.environ["PROJECT_ROOT"]
app = os.environ["APP_NAME"]
entry = os.environ["ENTRY"]

def walk_files(root, rel_base, exts=None):
    """收集目录下所有文件的 (src, dst_dir) 列表"""
    result = []
    for d, _, files in os.walk(root):
        for f in files:
            if exts and not any(f.endswith(e) for e in exts):
                continue
            src = os.path.join(d, f)
            dst = os.path.join(rel_base, os.path.relpath(src, root))
            result.append((src, os.path.dirname(dst)))
    return result

icon_datas = walk_files(os.path.join(prj, "icon"), "icon")
solver_datas = walk_files(os.path.join(prj, "src", "Solve"), "src/Solve", exts=[".py", ".so"])

lines = []
lines.append('# -*- mode: python ; coding: utf-8 -*-')
lines.append('import os')
lines.append(f'prj = r"{prj}"')
lines.append(f'app = "{app}"')
lines.append('')
lines.append('a = Analysis(')
lines.append(f'    [r"{entry}"],')
lines.append(f'    pathex=[os.path.join(prj, "src")],')
lines.append('    binaries=[],')
lines.append('    datas=[')
for f in ["main.glade","solver.glade","data_box.glade","2D_mesh.glade","3D_mesh.glade","plane_equation.glade"]:
    lines.append(f'        (os.path.join(prj, "ui", "{f}"), "ui"),')

for src, dst in icon_datas:
    lines.append(f'        (r"{src}", r"{dst}"),')
for src, dst in solver_datas:
    lines.append(f'        (r"{src}", r"{dst}"),')

lines.append('    ],')
lines.append('    hiddenimports=[')
for m in [
    "gi","gi.repository.Gtk","gi.repository.Gdk","gi.repository.GLib",
    "gi.repository.GObject","gi.repository.Pango","gi.repository.cairo",
    "gi.repository.GtkSource","gi.repository.Atk","gi.repository.Gio",
    "gi.repository.GdkPixbuf","gi.repository.PangoCairo",
    "OpenGL","OpenGL.GL","OpenGL.GL.shaders",
    "OpenGL.platform","OpenGL.platform.glx",
    "OpenGL.arrays","OpenGL.arrays.ctypesarrays",
    "numpy","numpy.core","numpy.linalg",
    "scipy","scipy.sparse","scipy.sparse.linalg",
    "meshio","gmsh","pygmsh","yaml","chardet",
    "importlib.util","importlib.machinery","ctypes","pathlib","collections","threading","io",
    "Utils","Utils.Config.path","Utils.Config.ReadYml",
    "Utils.Mesh.MeshClass","Utils.Mesh.MeshReader","Utils.Mesh.GeometryUtils","Utils.Mesh.MeshSplitter",
    "Utils.OpenGL.GLShader","Utils.OpenGL.GLTransformUtils",
    "Utils.Compute.Interpolation",
    "Utils.Connector.SolverWrapper","Utils.Connector.SolverViewBoxConn","Utils.Connector.OutputTracker",
    "Post.BaseGLArea","Shell.ShellCommand","Pre.MeshGeneration",
    "GUI.main","GUI.box0.main","GUI.box0.box2",
    "GUI.one_layer.main","GUI.two_layer.main","GUI.three_layer.main",
    "GUI.three_layer.PlaneEquationInputWindow",
    "GUI.one_layer.Mesh._2D_Mesh.main","GUI.one_layer.Mesh._3D_Mesh.main",
    "GUI.one_layer.Solver.main","GUI.one_layer.Solver.Solver2D.main","GUI.one_layer.Solver.Solver3D.main",
    "GUI.one_layer.Style.main",
    "GUI.box0.paned0.main","GUI.box0.paned0.box1",
    "GUI.box0.paned0.paned1.main","GUI.box0.paned0.paned1.box3",
    "GUI.box0.paned0.paned1.paned2.main",
    "GUI.box0.paned0.paned1.paned2.shell_box",
    "GUI.box0.paned0.paned1.paned2.notebook.main",
    "GUI.box0.paned0.paned1.paned2.notebook.view_box",
    "GUI.box0.paned0.paned1.paned2.notebook.data_box",
    "GUI.box0.paned0.paned1.paned2.notebook.edit_box",
    "GUI.box0.paned0.paned1.paned2.notebook.menu_box",
    "GUI.box0.paned0.paned1.paned2.notebook.top_box_of_every_type",
    "Solve",
]:
    lines.append(f'        "{m}",')
lines.append('    ],')
lines.append(f'    runtime_hooks=[os.path.join(prj, "_pyogl_rthook.py")],')
lines.append('    excludes=["tkinter","matplotlib","pandas","PIL","IPython","jupyter","PyQt5","PySide2","PySide6","wx"],')
lines.append('    noarchive=False,')
lines.append(')')
lines.append('')
lines.append('pyz = PYZ(a.pure, a.zipped_data, cipher=None)')
lines.append('')
lines.append(f'exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=app, debug=False, strip=False, upx=False, console=False)')
lines.append('')
lines.append(f'coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name=app)')

with open(os.path.join(prj, f"{app}.spec"), "w") as f:
    f.write("\n".join(lines))
print("  -> spec 已生成")
GENSPEC

# ---- 构建 ----
echo "[4/5] 开始打包..."
$PYTHON -m PyInstaller --distpath "$DIST_DIR" --workpath "$BUILD_DIR" --noconfirm --clean "$SPEC" 2>&1 | grep -E "(INFO: Build complete|ERROR|WARNING: Library not found)" || true

# ---- 删除冲突的 GL 库（使用系统版本）----
echo "[5/5] 清理冲突库..."
find "$DIST_DIR/$APP_NAME/_internal" -name "libepoxy*" -delete
find "$DIST_DIR/$APP_NAME/_internal" -name "libGLU*" -delete
echo "  -> 已移除 bundled libepoxy / libGLU"

# ---- 启动脚本 ----
cat > "$DIST_DIR/$APP_NAME/run_$APP_NAME.sh" << 'LAUNCHER'
#!/bin/sh
DIR="$(cd "$(dirname "$0")" && pwd)"
export PYOPENGL_PLATFORM=glx
if [ -d /usr/lib/x86_64-linux-gnu/girepository-1.0 ]; then
    export GI_TYPELIB_PATH="${GI_TYPELIB_PATH}:${DIR}/_internal:/usr/lib/x86_64-linux-gnu/girepository-1.0"
fi
exec "$DIR/FEM-BEM-Viewer" "$@"
LAUNCHER
chmod +x "$DIST_DIR/$APP_NAME/run_$APP_NAME.sh"

echo ""
echo "============================================"
echo "  打包完成: $DIST_DIR/$APP_NAME/"
echo "  启动:     $DIST_DIR/$APP_NAME/run_$APP_NAME.sh"
echo "  分发:     tar -czf $APP_NAME.tar.gz -C $DIST_DIR $APP_NAME"
echo "============================================"
