import os
import time
from flask import Flask, render_template

app = Flask(__name__)

# 日志文件路径
log_file = 'test_record.log'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_log')
def get_log():
    # 读取日志文件内容
    with open(log_file, 'r') as file:
        log_content = file.read()
    return log_content

if __name__ == '__main__':
    app.run(debug=True)
