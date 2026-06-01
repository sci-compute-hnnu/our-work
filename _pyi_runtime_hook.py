import sys
import os

# ---------- GI (GObject Introspection) 路径 ----------
# PyInstaller 收集了 typelib 但 GI 可能找不到，手动注册
_meipass = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# typelib 搜索路径
_typelib_dirs = [
    os.path.join(_meipass, 'gi_typelibs'),
    os.path.join(_meipass, '_internal', 'gi_typelibs'),
    '/usr/lib/x86_64-linux-gnu/girepository-1.0',
    '/usr/lib/girepository-1.0',
]
for _d in _typelib_dirs:
    if os.path.isdir(_d) and _d not in os.environ.get('GI_TYPELIB_PATH', '').split(':'):
        existing = os.environ.get('GI_TYPELIB_PATH', '')
        os.environ['GI_TYPELIB_PATH'] = _d + (':' + existing if existing else '')

# ---------- 库路径 (GTK, Cairo, OpenGL 等) ----------
_lib_dirs = [
    os.path.join(_meipass, '_internal'),
    os.path.join(_meipass, 'lib'),
    '/usr/lib/x86_64-linux-gnu',
]
for _d in _lib_dirs:
    if os.path.isdir(_d):
        try:
            # 某些系统需要先加载 libffi (OpenGL+GTK 要求)
            import ctypes
            _libffi_paths = [
                '/usr/lib/x86_64-linux-gnu/libffi.so.7',
                '/usr/lib/x86_64-linux-gnu/libffi.so.8',
            ]
            for _libffi in _libffi_paths:
                if os.path.exists(_libffi) and _libffi not in os.environ.get('LD_PRELOAD', ''):
                    os.environ['LD_PRELOAD'] = _libffi
                    break
        except Exception:
            pass

# ---------- 字体 (GTK 渲染需要) ----------
_font_dirs = [
    '/usr/share/fonts',
    '/usr/local/share/fonts',
]
for _d in _font_dirs:
    if os.path.isdir(_d):
        os.environ.setdefault('FONTCONFIG_PATH', '/etc/fonts')
        break

# ---------- solvers 导入路径 ----------
_solve_dir = os.path.join(_meipass, 'src', 'Solve')
if os.path.isdir(_solve_dir) and _solve_dir not in sys.path:
    sys.path.insert(0, _solve_dir)

