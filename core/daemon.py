import subprocess
import time
import argparse
from utils import *

def run_baseball(username, debug_mode, fix_tp_mode, super_mode, fix_tp_point, base_sl, base_qty, max_qty,lever_mark_mode,init_fund,loss_ratio,AUM,balance_rate):
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
            if lever_mark_mode:
                command.append('-lm')

            command.append(f'-fp={fix_tp_point}')
            command.append(f'-bsl={base_sl}')
            command.append(f'-bq={base_qty}')
            command.append(f'-mxq={max_qty}')
            command.append(f'-if={init_fund}')
            command.append(f'-lr={loss_ratio}')
            command.append(f'-aum={AUM}')
            command.append(f'-br={balance_rate}')


            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            current_time = get_current_time()
            logger.error(f"Error occurred while running baseball.py: {e} {current_time}")
        # 休眠一段时间后再次运行
        time.sleep(10)

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-d', '--debug_mode', action='store_true', default=False, help='Enable debug mode')
    parser.add_argument('-f', '--fix_tp_mode', action='store_true', default=False, help='Enable fix_tp mode')
    parser.add_argument('-s', '--super_mode', action='store_true', default=False, help='Enable super_mode')
    parser.add_argument('-lm', '--lever_mark_mode', action='store_true', default=True, help='Enable lever_mark_mode')


    parser.add_argument('-fp', '--fix_tp_point', default=88,help='fix_tp_point')
    parser.add_argument('-bsl', '--base_sl', default=88,help='base_sl')
    parser.add_argument('-bq', '--base_qty', default=0.05,help='base_qty')
    parser.add_argument('-mxq', '--max_qty', default=1.5,help='max_qty')
    parser.add_argument('-if', '--init_fund', default=5000,help='init_fund')
    parser.add_argument('-lr', '--loss_ratio', default=0.01,help='loss_ratio')
    parser.add_argument('-aum', '--AUM', default=0.2,help='AUM')
    parser.add_argument('-br', '--balance_rate', default=0.5,help='balance_rate')

    args = parser.parse_args()

    # 调用守护程序函数，并将命令行参数传递给它
    run_baseball(args.username, args.debug_mode, args.fix_tp_mode, args.super_mode, args.fix_tp_point, args.base_sl, args.base_qty, args.max_qty,args.lever_mark_mode,args.init_fund,args.loss_ratio,args.AUM,args.balance_rate)
