#!/bin/bash

# openGL(glarea)正常显示依赖
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libffi.so.7

# 获取脚本所在目录的绝对路径
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 添加 src 路径到 PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

python3 "$PROJECT_ROOT/src/GUI/main.py"
