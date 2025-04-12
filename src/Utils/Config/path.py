from pathlib import Path

# 当前文件路径 (__file__ 是当前文件的绝对路径)
current_file = Path(__file__)
# 获取上面两级目录
# project_dir = str(current_file.parent.parent.parent.parent)
project_dir = str(current_file.parent.parent.parent.parent.parent.parent)
# ui目录
ui_dir = project_dir+'/ui/'
# icon目录
icon_dir = project_dir+'/icon/'

# solve目录
solve_dir = project_dir+'/src/Solve/'