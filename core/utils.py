import datetime
import time
import yaml
import logging
import colorlog

def get_minute_timestamp():
    current_time = datetime.datetime.now()
    whole_minute = current_time.replace(second=0, microsecond=0)
    timestamp = int(time.mktime(whole_minute.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms

def get_previous_minute_timestamp():
    current_time = datetime.datetime.now()
    previous_minute = current_time - datetime.timedelta(minutes=1)
    whole_minute = previous_minute.replace(second=0, microsecond=0)
    timestamp = int(time.mktime(whole_minute.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms

def get_previous_hour_timestamp():
    current_time = datetime.datetime.now()
    previous_hour = current_time - datetime.timedelta(hours=1)
    whole_hour = previous_hour.replace(minute=0, second=0, microsecond=0)
    timestamp = int(time.mktime(whole_hour.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms

def get_previous_three_hour_timestamp():
    current_time = datetime.datetime.now()
    previous_hour = current_time - datetime.timedelta(hours=3)
    whole_hour = previous_hour.replace(minute=0, second=0, microsecond=0)
    timestamp = int(time.mktime(whole_hour.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms

def get_previous_eight_hour_timestamp():
    current_time = datetime.datetime.now()
    previous_hour = current_time - datetime.timedelta(hours=8)
    whole_hour = previous_hour.replace(minute=0, second=0, microsecond=0)
    timestamp = int(time.mktime(whole_hour.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms


def get_previous_day_timestamp():
    current_time = datetime.datetime.now()
    previous_day = current_time - datetime.timedelta(days=1)
    previous_day_midnight = previous_day.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(time.mktime(previous_day_midnight.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms

def get_previous_three_day_timestamp():
    current_time = datetime.datetime.now()
    previous_day = current_time - datetime.timedelta(days=3)
    previous_day_midnight = previous_day.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(time.mktime(previous_day_midnight.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms

def get_previous_month_timestamp():
    current_time = datetime.datetime.now()
    previous_day = current_time - datetime.timedelta(days=30)
    previous_day_midnight = previous_day.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(time.mktime(previous_day_midnight.timetuple()))
    timestamp_ms = timestamp * 1000
    return timestamp_ms


def timestamp_to_hour(timestamp_ms):
    timestamp_sec = timestamp_ms // 1000
    time_obj = datetime.datetime.fromtimestamp(timestamp_sec)
    hour_value = time_obj.hour
    return hour_value

def timestamp_to_time(timestamp_ms):
    timestamp_sec = timestamp_ms // 1000
    time_obj = datetime.datetime.fromtimestamp(timestamp_sec)
    return time_obj

def get_current_hour():
    return datetime.datetime.now().hour

def get_current_minute():
    return datetime.datetime.now().minute

def get_current_second():
    return datetime.datetime.now().second

def get_current_time():
    # 获取当前时间
    return datetime.datetime.now()

def get_config_file():
    file_path = "../config/config.yaml"
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data


def get_logger(logfile='app.log'):
    # 创建日志记录器
    logger = logging.getLogger('rbreaker_logger')
    logger.setLevel(logging.DEBUG)  # 设置日志记录器的级别为 DEBUG

    # 如果已经存在处理器，则直接返回
    if logger.hasHandlers():
        return logger

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 设置控制台处理器的级别为 DEBUG

    # 创建文件处理器，并指定追加模式 'a'
    file_handler = logging.FileHandler(logfile, mode='a')
    file_handler.setLevel(logging.WARNING)  # 设置文件处理器的级别为 warning

    # 创建格式化器
    formatter = colorlog.ColoredFormatter(
        '%(asctime)s - %(log_color)s%(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'green',
            'INFO': 'white',
            'WARNING': 'cyan',
            'ERROR': 'red',
            'CRITICAL': 'yellow',
        },
        reset=True,
        secondary_log_colors={},
        style='%'
    )

    # 将格式化器添加到处理器
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

def is_approximately_equal(value1, value2, tolerance=10):
    return abs(value1 - value2) <= tolerance

def is_more_than_4hours(timestamps):
# 给定的时间戳
    timestamp = float(timestamps) / 1000  # 将毫秒转换为秒

    # 获取当前时间戳
    current_timestamp = time.time()

    # 将时间戳转换为datetime对象
    given_time = datetime.datetime.fromtimestamp(timestamp)
    current_time = datetime.datetime.fromtimestamp(current_timestamp)
    # 计算时间差
    time_difference = current_time - given_time
    # 判断时间差是否大于等于8小时
    if time_difference.total_seconds() >= 4 * 3600:
        return True
    else:
        return False

def is_more_than_6hours(timestamps):
# 给定的时间戳
    timestamp = float(timestamps) / 1000  # 将毫秒转换为秒

    # 获取当前时间戳
    current_timestamp = time.time()

    # 将时间戳转换为datetime对象
    given_time = datetime.datetime.fromtimestamp(timestamp)
    current_time = datetime.datetime.fromtimestamp(current_timestamp)
    # 计算时间差
    time_difference = current_time - given_time
    # 判断时间差是否大于等于8小时
    if time_difference.total_seconds() >= 6 * 3600:
        return True
    else:
        return False


def is_more_than_8hours(timestamps):
# 给定的时间戳
    timestamp = float(timestamps) / 1000  # 将毫秒转换为秒

    # 获取当前时间戳
    current_timestamp = time.time()

    # 将时间戳转换为datetime对象
    given_time = datetime.datetime.fromtimestamp(timestamp)
    current_time = datetime.datetime.fromtimestamp(current_timestamp)
    # 计算时间差
    time_difference = current_time - given_time
    # 判断时间差是否大于等于8小时
    if time_difference.total_seconds() >= 8 * 3600:
        return True
    else:
        return False

def is_more_than_10hours(timestamps):
# 给定的时间戳
    timestamp = float(timestamps) / 1000  # 将毫秒转换为秒

    # 获取当前时间戳
    current_timestamp = time.time()

    # 将时间戳转换为datetime对象
    given_time = datetime.datetime.fromtimestamp(timestamp)
    current_time = datetime.datetime.fromtimestamp(current_timestamp)
    # 计算时间差
    time_difference = current_time - given_time
    # 判断时间差是否大于等于8小时
    if time_difference.total_seconds() >= 10 * 3600:
        return True
    else:
        return False

def time_until_8am_tomorrow():
    # 获取当前时间
    now = datetime.datetime.now()

    # 获取明天8点时间
    tomorrow_8am = now.replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    # 计算当前时间距离明天8点的时间间隔
    time_remaining = str(tomorrow_8am - now)

    return time_remaining

def parse_date(date_str):
    # 定义日期格式
    date_format = "%d%b%y"

    # 解析日期字符串为datetime对象
    return datetime.datetime.strptime(date_str, date_format)

def get_date_type(end_time):
    # 解析日期字符串
    end_date = parse_date(end_time)

    # 获取周几（0表示周一，6表示周日）
    weekday = end_date.weekday()

    # 获取月份和年份
    month = end_date.month
    year = end_date.year

    # 获取本月最后一天
    last_day_of_month = (end_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)

    # 获取本季度最后一天
    current_quarter = (month - 1) // 3 + 1
    last_day_of_quarter = datetime.datetime(year, current_quarter * 3, 1) + datetime.timedelta(days=90) - datetime.timedelta(days=1)

    # 判断日期类型
    if weekday == 4:
        if end_date == last_day_of_quarter:
            return '季末赛'
        elif end_date == last_day_of_month:
            return '月末赛'
        else:
            return '周决赛'
    else:
        return '日内赛'
    

def is_less_than_10_minutes(time_str):
    # 将时间字符串转换成datetime对象
    time_format = "%H:%M:%S.%f"
    given_time = datetime.datetime.strptime(time_str, time_format)

    # 获取当前时间
    current_time = datetime.datetime.now()

    # 计算时间差
    time_difference = current_time - given_time

    # 判断时间差是否小于10分钟
    return time_difference.total_seconds() < 600

def remaining_time_to_8_hours(stop_loss_time):
    # 将stop_loss_time转换为datetime对象
    stop_loss_time = datetime.datetime.fromtimestamp(int(stop_loss_time) / 1000)

    # 获取当前时间
    current_time = datetime.datetime.now()

    # 计算时间差
    time_difference = current_time - stop_loss_time

    # 计算距离8小时还有多久
    remaining_time = datetime.timedelta(hours=8) - time_difference

    # 将remaining_time转换为字符串格式
    remaining_time_str = str(remaining_time)

    return remaining_time_str

def remaining_time_to_4_hours(stop_loss_time):
    # 将stop_loss_time转换为datetime对象
    stop_loss_time = datetime.datetime.fromtimestamp(int(stop_loss_time) / 1000)

    # 获取当前时间
    current_time = datetime.datetime.now()

    # 计算时间差
    time_difference = current_time - stop_loss_time

    # 计算距离4小时还有多久
    remaining_time = datetime.timedelta(hours=4) - time_difference

    # 将remaining_time转换为字符串格式
    remaining_time_str = str(remaining_time)

    return remaining_time_str
