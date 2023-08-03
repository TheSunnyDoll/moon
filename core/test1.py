def find_index(element, lst):
    if element in lst:
        return lst.index(element)+1
    else:
        return -1

# 示例数据
data_list = [29587.0, 29593, 29695, 29767, 30004, 30333.5, 30588, 31036.0, 31140]

# 要查找的元素
element_to_find = 29767

# 调用函数并输出结果
index = find_index(element_to_find, data_list)
print(f"The element {element_to_find} is at index: {index}")
