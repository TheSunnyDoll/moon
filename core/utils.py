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


def get_config_file():
    file_path = "../config/config.yaml"
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data

def get_logger():
    # 创建日志记录器
    logger = logging.getLogger('rbreaker_logger')

    # 创建控制台处理器
    console_handler = logging.StreamHandler()

    # 创建格式化器
    formatter = colorlog.ColoredFormatter(
        '%(asctime)s - %(log_color)s%(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'green',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_yellow',
        },
        reset=True,
        secondary_log_colors={},
        style='%'
    )
    # 将格式化器添加到处理器
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(console_handler)
    return logger