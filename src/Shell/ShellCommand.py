import re

class CommandProcessor:
    def __init__(self):
        # 存储变量的字典
        self.variables = {}

    def process_command(self, command):
        # 处理赋值命令
        if '=' in command:
            result = self.process_variable(command)

        # 处理加载插件命令
        elif command == 'load()':
            result = "Load plugin function not implemented."

        # 处理未知命令
        else:
            result = f"Command '{command}' executed."

        return result


    def process_variable(self, command):
        # 正则表达式用于捕捉赋值语句，支持变量名 = 任意有效的 Python 表达式
        match = re.match(r'(\w+)\s*=\s*(.*)', command.strip())

        if match:
            var_name = match.group(1)
            value_expression = match.group(2).strip()

            try:
                # 尝试解析并评估右侧的表达式
                value = eval(value_expression)

                # 存储变量
                self.variables[var_name] = (value, type(value))
                # print(self.variables)
                return f"Variable '{var_name}' set to {value} (type: {type(value).__name__})."

            except Exception as e:
                return f"Error in evaluating the expression: {str(e)}"
        else:
            return "Invalid assignment command."

