def print_details(*args, **kwargs):
    # 打印位置参数
    if len(args) !=0:
        print(args[0])

    # print(args[0], args[1])
    # 打印关键字参数
    print("\n关键字参数:")
    for key, value in kwargs.items():
        print(f"{key}: {value}")


# 调用函数
names = ("Alice", "Bob", "Charlie")
info = {
    "age": 25,
    "city": "New York",
    "occupation": "Engineer"
}

print_details((), **info)