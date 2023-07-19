high = [30058.0, 30015.5, 29943.5, 29926.0, 29797.5, 29820.0, 30053.5, 30001.0, 30058.0, 30177.0, 30093.0, 30055.0, 30006.5]
low = [29889.0, 29776.5, 29676.5, 29795.0, 29816.0, 29470.0, 29665.0, 29678.0, 29738.5, 29770.0, 29931.0, 29983.0, 30045.5, 29988.0, 29933.5, 29851.0]

# 计算 delta（max(high) 和 min(low) 的距离）
delta = max(high) - min(low)

# 计算 0.618 倍的目标距离
target_distance = delta * 0.618

# 找到与目标距离最接近的值
closest_index = None
min_diff = float('inf')  # 初始化为正无穷大，用于保存最小差值
for i in range(len(high)):
    diff = abs(target_distance - (high[i] - low[i]))
    if diff < min_diff:
        min_diff = diff
        closest_index = i

if closest_index is not None:
    closest_low_value = low[closest_index]
    closest_high_value = high[closest_index]
    print("最接近距离 max(high) 和 min(low) 的 0.618 倍的值：")
    print("Low:", closest_low_value)
    print("High:", closest_high_value)
else:
    print("没有找到最接近距离 max(high) 和 min(low) 的 0.618 倍的值。")
