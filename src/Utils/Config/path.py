from pathlib import Path
import sys

# 当前文件路径 (__file__ 是当前文件的绝对路径)
# PyInstaller 冻结环境下使用 sys._MEIPASS
if getattr(sys, 'frozen', False):
    project_dir = sys._MEIPASS
else:
    current_file = Path(__file__)
    # 获取上面四级目录到达项目根目录 (src/Utils/Config/path.py → project/)
    project_dir = str(current_file.parent.parent.parent.parent)

# ui目录
ui_dir = project_dir + '/ui/'

# icon目录
icon_dir = project_dir + '/icon/'

# solve目录
solve_dir = project_dir + '/src/Solve/'