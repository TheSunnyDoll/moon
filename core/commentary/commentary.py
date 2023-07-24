import os
import time
from flask import Flask, render_template
from collections import deque
from ansi2html import Ansi2HTMLConverter

app = Flask(__name__)

# 日志文件路径
log_file = '../test_record.log'
# 固定大小的队列，最多保存25行内容
log_queue = deque(maxlen=25)

@app.route('/')
def index():
    return render_template('index.html', log_content=log_queue)

@app.route('/get_log')
def get_log():
    # 读取日志文件内容
    with open(log_file, 'r') as file:
        log_lines = file.readlines()
    # 将最新的25行内容加入队列
    log_queue.extend(log_lines[-25:])
    
    # 转换ANSI颜色代码为HTML格式
    converter = Ansi2HTMLConverter()
    colored_logs = [converter.convert(line) for line in log_queue]
    
    return '\n'.join(colored_logs)

if __name__ == '__main__':
    app.run(port=8888, debug=True)