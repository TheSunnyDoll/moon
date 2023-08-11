import subprocess
import time
import argparse
from utils import *

def run_ioside(username,debug_mode, super_mode, trailing_loss,base_qty,trailing_delta_mul,rangeRate, pair,pyramid_mode):
    logger = get_logger(username+'down_error.log')

    while True:
        # 运行baseball.py命令
        try:
            command = ['python', 'in_outside.py', '-u', username]
            if debug_mode:
                command.append('-d')
            if trailing_loss:
                command.append('-tl')
            if super_mode:
                command.append('-s')
            if pyramid_mode:
                command.append('-pm')


            command.append(f'-bq={base_qty}')
            command.append(f'-tm={trailing_delta_mul}')
            command.append(f'-rr={rangeRate}')
            command.append(f'-pr={pair}')


            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            current_time = get_current_time()
            logger.error(f"Error occurred while running in_outside.py: {e} {current_time}")
        # 休眠一段时间后再次运行
        time.sleep(10)

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-s', '--super_mode', action='store_true', default=False, help='Enable super_mode')
    parser.add_argument('-tl', '--trailing_loss', action='store_true', default=False, help='Enable trailing_loss')
    parser.add_argument('-pm', '--pyramid_mode', action='store_true', default=False, help='Enable pyramid_mode')

    parser.add_argument('-pr', '--pair', default='BTCUSDT_UMCBL',help='pair')
    parser.add_argument('-bq', '--base_qty', default=0,help='base_qty')
    parser.add_argument('-tm', '--trailing_delta_mul', default=1,help='trailing_delta_mul')
    parser.add_argument('-rr', '--rangeRate', default=0.01,help='rangeRate')

    
    args = parser.parse_args()

    # 调用守护程序函数，并将命令行参数传递给它
    run_ioside(args.username, args.debug_mode, args.super_mode, args.trailing_loss,args.base_qty,args.trailing_delta_mul,args.rangeRate, args.pair,args.pyramid_mode)
