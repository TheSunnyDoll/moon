import subprocess
import time
import argparse
from utils import *

def run_baseball(username, debug_mode, fix_tp_mode, super_mode, fix_tp_point, base_sl, base_qty, max_qty):
    logger = get_logger(username+'down_error.log')

    while True:
        # 运行baseball.py命令
        try:
            command = ['python', 'baseball.py', '-u', username]
            if debug_mode:
                command.append('-d')
            if fix_tp_mode:
                command.append('-f')
            if super_mode:
                command.append('-s')
            command.append(f'-fp={fix_tp_point}')
            command.append(f'-bsl={base_sl}')
            command.append(f'-bq={base_qty}')
            command.append(f'-mxq={max_qty}')
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            current_time = get_current_time()
            logger.error(f"Error occurred while running baseball.py: {e} {current_time}")
        # 休眠一段时间后再次运行
        time.sleep(10)

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True, help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-f', '--fix_tp_mode', action='store_true', default=False, help='Enable fix_tp mode')
    parser.add_argument('-s', '--super_mode', action='store_true', default=False, help='Enable super_mode')
    parser.add_argument('-fp', '--fix_tp_point', type=int, default=88, help='fix_tp_point')
    parser.add_argument('-bsl', '--base_sl', type=int, default=88, help='base_sl')
    parser.add_argument('-bq', '--base_qty', type=float, default=0.2, help='base_qty')
    parser.add_argument('-mxq', '--max_qty', type=float, default=1.2, help='max_qty')

    args = parser.parse_args()

    # 调用守护程序函数，并将命令行参数传递给它
    run_baseball(args.username, args.debug_mode, args.fix_tp_mode, args.super_mode, args.fix_tp_point, args.base_sl, args.base_qty, args.max_qty)
