# 有限元/边界元数据可视化平台 

本项⽬基于现代计算可视化技术，旨在开发⾼性能、实时交互、纯⾃主研发的有限元/边界元
（FEM/BEM）数据可视化平台，主要用于科学计算、工程仿真结果的实时渲染，在计算流体⼒学
（CFD）、结构⼒学、电磁场、热传导等多物理场仿真领域提供计算-可视化⼀体化解决⽅案。



从源代码启动该项目需要求在Linux(Ubuntu)上执行,如需使用solve模块需借助pybind11技术
 (详情参考https://pybind11.readthedocs.io/en/stable/basics.html)

本项目第三方图形界面采用GTK, 如在Ubuntu自带python解释器上启动该项目，无需安装GTK(PyGobject), 
在解释器环境中输入

```python
import gi
```

显示无错，则安装后续依赖后即可正常运行。

如在非原生python解释器 如在anaconda3的虚拟环境中启动时，需提前下载PyGobject依赖，
使用apt管理器安装以下依赖

```bash
sudo apt-get update
sudo apt-get install -y pkg-config libcairo2-dev
sudo apt-get install -y gobject-introspection libgirepository1.0-dev
```

安装完上述依赖后使用pip安装PyGObject即可

```shell
pip install PyGObject
```

安装其他软件包

```shell
pip install -r requirements.txt
```

启动

```bash
sh run.sh
```



注: 本项目现有的C++代码实现的求解器pymodule(动态库文件 .so)均只支持python=3.11。
如需使用现有的求解模块建议采用anaconda3的conda包管理器安装python=3.11的虚拟环境：

```bash
conda create -n GTK python=3.11
```
