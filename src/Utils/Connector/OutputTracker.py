import sys
import io


class OutputTracker:
    def __init__(self):
        self.last_output = None
        self.output_buffer = io.StringIO()
        self.original_stdout = sys.stdout

    def start_tracking(self):
        # 重定向 sys.stdout 到 output_buffer
        sys.stdout = self.output_buffer

    def stop_tracking(self):
        # 恢复 sys.stdout
        sys.stdout = self.original_stdout

    def get_new_output(self):
        # 获取捕获的内容
        self.stop_tracking()
        new_output = self.output_buffer.getvalue().strip()  # 去除前后空白字符

        # 清空缓冲区
        self.output_buffer.truncate(0)
        self.output_buffer.seek(0)

        if new_output and new_output != self.last_output:
            # 有新的输出且不同于上次输出
            self.last_output = new_output  # 更新记录
            return new_output
        else:
            # 没有新的输出或内容未变
            self.last_output = None
            return None


# 使用示例
# tracker = OutputTracker()
#
# # 模拟另一个代码块的输出
# tracker.start_tracking()
# print('hello')
# content = tracker.get_new_output()  # 捕捉内容并返回
# print("Captured content:", content)  # 输出捕捉到的内容
#
# # 继续测试
# tracker.start_tracking()
# print('world')
# content = tracker.get_new_output()  # 捕捉内容并返回
# print("Captured content:", content)  # 输出捕捉到的内容