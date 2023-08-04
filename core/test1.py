def get_inside_bars(klines):
    def is_inside_bar(current_high, current_low, prev_high, prev_low):
        # 判断当前蜡烛是否是Inside Bar
        if current_high <= prev_high and current_low >= prev_low:
            return True
        else:
            return False

    inside_bars = []

    for i in range(1, len(klines)):
        current_kline = klines[i]
        prev_kline = klines[i - 1]

        current_high = current_kline['high']
        current_low = current_kline['low']
        prev_high = prev_kline['high']
        prev_low = prev_kline['low']

        if is_inside_bar(current_high, current_low, prev_high, prev_low):
            inside_bars.append(current_kline)

    return inside_bars

# 示例数据，假设这是获得的K线数据列表
klines = [
    {'high': 100, 'low': 90},
    {'high': 110, 'low': 85},
    {'high': 95, 'low': 80},
    {'high': 105, 'low': 90},
    {'high': 100, 'low': 90},
    {'high': 110, 'low': 85},
    {'high': 95, 'low': 80},
    {'high': 105, 'low': 90},]

# 调用函数获取所有的Inside Bar
inside_bars = get_inside_bars(klines)

# 输出所有的Inside Bar
for inside_bar in inside_bars:
    print("Inside Bar:", inside_bar)
