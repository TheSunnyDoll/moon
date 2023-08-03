def find_max_min(data_list):
    if not data_list:
        return None, None

    max_val = max(data_list, key=lambda x: x[1])[1]
    min_val = min(data_list, key=lambda x: x[1])[1]

    return max_val, min_val

# 示例数据
data_list = [['reversal-bull', 29013.5, 29510.0], ['bear', 29324.5, 28695.5], ['bull', 28729.5, 29324.5], ['bull', 29162.5, 30043.5], ['bear', 29587.0, 28907.0], ['bull', 29019.5, 29266.0]]

# 调用函数并输出结果
max_val, min_val = find_max_min(data_list)
print("最大值:", max_val)
print("最小值:", min_val)
