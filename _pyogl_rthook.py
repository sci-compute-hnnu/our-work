# PyInstaller runtime hook: GTK GLArea 通过 libepoxy 管理 GL 上下文，
# PyOpenGL 通过 ctypes/libGL 独立查询。打包后两者 dispatch 不同，
# platform.GetCurrentContext() 返回 0，导致 "no valid context" 错误。
# 修复: 当 GetCurrentContext() 返回 0 时返回 dummy context，
# 因为 GL 状态在 C 层面是正确管理的(GTK/epoxy 已 make_current)。
import sys

def _patch():
    try:
        import OpenGL.contextdata
        _orig = OpenGL.contextdata.getContext

        class _DummyCtx:
            pass

        def _patched_getContext(context=None):
            if context is not None:
                return context
            ctx = OpenGL.contextdata.platform.GetCurrentContext()
            if ctx == 0:
                return _DummyCtx()
            return _orig(context)

        OpenGL.contextdata.getContext = _patched_getContext
        print("[pyogl] GL context patch applied", file=sys.stderr)
    except Exception as e:
        print(f"[pyogl] WARNING: {e}", file=sys.stderr)

_patch()

# --- Setup solver import path ---
# 确保 Solve.Solver_3D.DG_3D 等动态导入能在 PyInstaller 环境中找到
import sys as _sys
import os as _os
_meipass = getattr(_sys, '_MEIPASS', _os.path.dirname(_os.path.abspath(__file__)))
_src_dir = _os.path.join(_meipass, 'src')
if _os.path.isdir(_src_dir) and _src_dir not in _sys.path:
    _sys.path.insert(0, _src_dir)
