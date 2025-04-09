import yaml

def parse_yaml(path):
    # 使用 PyYAML 解析 YAML 文件
    try:
        with open(path, 'r') as file:
            yaml_content = file.read()
        # 解析 YAML 内容
        data = yaml.safe_load(yaml_content)
        return data
    except Exception as e:
        # 捕获并打印任何异常
        print(f"Error reading or parsing YAML file: {e}")
        return None



if __name__ == "__main__":

    # 示例 YAML 内容
    yaml_content = """
    meshtype: surface
    var: [rho, vx, vy]
    """

    # 解析 YAML
    parsed_data = parse_yaml(yaml_content)

    # 访问参数
    # meshtype = parsed_data['config']['meshtype']
    # var_list = parsed_data['config']['var']
    #
    # print(f"Mesh Type: {meshtype}")
    # print(f"Variables: {var_list}")  # ['rho', 'vx', 'vy']
    print(parsed_data)
