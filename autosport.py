#!/usr/bin/env python3
"""
微信运动步数自动更新脚本
按照时间表自动更新微信运动步数，模拟真实的运动轨迹
"""

import os
import sys
import time
import random
import math
from datetime import datetime, timedelta
import argparse
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from utils import load_credentials, set_step

# 时间表
TIME_SCHEDULE = [
    ("7:30", 0.0),
    ("8:30", 0.2),
    ("11:50", 0.3),
    ("13:00", 0.4),
    ("14:00", 0.45),
    ("14:40", 0.55),
    ("17:30", 0.7),
    ("19:00", 0.8),
    ("21:30", 0.85),
    ("22:30", 0.95),
    ("23:30", 1.0)
]

def parse_time(time_str):
    """解析时间字符串为分钟数"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def linear_interpolation(x, x1, y1, x2, y2):
    """线性插值"""
    if x1 == x2:
        return y1
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

def generate_daily_target_steps(base_total_step, delta):
    """
    生成每日随机化的目标步数
    
    Args:
        base_total_step: 基础目标步数
        delta: 随机偏差系数 (0-1之间的值)
    
    Returns:
        int: 随机化后的每日目标步数
    """
    # 使用正态分布生成随机偏差，范围大约在 ±delta*base_total_step 之间
    random_deviation = random.gauss(0, delta * base_total_step * 0.3)
    
    # 计算随机化后的目标步数
    randomized_total_step = base_total_step + random_deviation
    
    # 确保步数在合理范围内 (至少为基础值的50%，最多为基础值的150%)
    min_steps = int(base_total_step * 0.5)
    max_steps = int(base_total_step * 1.5)
    randomized_total_step = max(min_steps, min(max_steps, randomized_total_step))
    
    return int(randomized_total_step)

def calculate_steps_for_day(total_step, delta):
    """
    计算一天中每一分钟的步数
    
    Args:
        total_step: 每日总步数目标
        delta: 随机偏差系数
    
    Returns:
        dict: 时间点到步数的映射
    """
    # 转换时间表为分钟数
    schedule_minutes = [(parse_time(t), ratio) for t, ratio in TIME_SCHEDULE]
    
    # 创建一个字典存储每分钟的步数
    steps_dict = {}
    
    # 对于每个相邻的时间段，计算中间每分钟的步数
    for i in range(len(schedule_minutes) - 1):
        start_minutes, start_ratio = schedule_minutes[i]
        end_minutes, end_ratio = schedule_minutes[i+1]
        
        # 计算这个时间段内每分钟的步数
        for minute in range(start_minutes, end_minutes + 1):
            # 线性插值计算理论步数
            ratio = linear_interpolation(minute, start_minutes, start_ratio, end_minutes, end_ratio)
            theoretical_step = total_step * ratio
            
            # 添加随机负偏差 (-delta 到 0)
            random_deviation = random.uniform(-delta, 0) * theoretical_step
            step = max(0, theoretical_step + random_deviation)  # 确保步数非负
            
            steps_dict[minute] = step
    
    # 确保步数只增不减
    max_step = 0
    for minute in sorted(steps_dict.keys()):
        max_step = max(max_step, steps_dict[minute])
        steps_dict[minute] = max_step
    
    # 处理7:30之前的时间（步数为0）
    for minute in range(0, schedule_minutes[0][0]):
        steps_dict[minute] = 0
    
    # 处理23:30之后的时间（步数为总步数）
    for minute in range(schedule_minutes[-1][0] + 1, 24 * 60):
        steps_dict[minute] = total_step
    
    return steps_dict

def get_current_step(steps_dict, current_time):
    """
    根据当前时间获取应该设置的步数
    
    Args:
        steps_dict: 时间点到步数的映射
        current_time: 当前时间 (datetime对象)
    
    Returns:
        int: 应该设置的步数
    """
    # 获取当前时间的分钟数
    current_minutes = current_time.hour * 60 + current_time.minute
    
    # 直接从字典中获取步数
    return int(steps_dict.get(current_minutes, 0))

def plot_steps(steps_dict, total_step):
    """绘制步数随时间变化的图表"""
    # 创建时间点列表（从0:00到23:59，每10分钟一个点）
    times = []
    steps = []
    
    for hour in range(24):
        for minute in range(0, 60, 10):
            times.append(hour * 60 + minute)
            # 构造时间字符串查找对应的步数
            time_str = f"{hour:02d}:{minute:02d}"
            # 使用get_current_step函数计算该时间点的步数
            dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            step = get_current_step(steps_dict, dt)
            steps.append(step)
    
    # 绘图
    plt.figure(figsize=(12, 6))
    plt.plot(times, steps, marker='o', linewidth=2, markersize=4)
    plt.xlabel('时间 (分钟)')
    plt.ylabel('步数')
    plt.title(f'微信运动步数自动更新计划 (目标: {total_step} 步)')
    plt.grid(True, alpha=0.3)
    
    # 设置x轴标签
    x_ticks = [i * 60 for i in range(25)]  # 每小时一个刻度
    x_labels = [f"{i:02d}:00" for i in range(24)] + ["24:00"]
    plt.xticks(x_ticks, x_labels, rotation=45)
    
    # 设置y轴标签
    plt.ylim(0, total_step * 1.1)
    
    plt.tight_layout()
    plt.show()

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='微信运动步数自动更新脚本')
    parser.add_argument('--dryrun', action='store_true', help='仅显示计划不实际执行')
    args = parser.parse_args()
    
    # 加载环境变量
    load_dotenv()
    
    # 读取配置
    total_step = int(os.getenv('total_step', 7000))
    delta = float(os.getenv('delta', 0.2))
    api_url = os.getenv('api_url', 'https://wzz.wangzouzou.com/motion/api/motion/Xiaomi')
    
    print(f"🎯 基础目标步数: {total_step}")
    print(f"🎲 随机偏差系数: {delta}")
    print(f"📊 每日实际目标将在基础值的50%-150%范围内随机变化")
    print(f"🌐 API地址: {api_url}")
    
    # 加载用户凭证
    try:
        user, password = load_credentials()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)
    
    # 计算今天的步数计划
    print("📅 正在生成今天的步数计划...")
    daily_target_step = generate_daily_target_steps(total_step, delta)
    print(f"🎯 今日随机化目标步数: {daily_target_step}")
    steps_dict = calculate_steps_for_day(daily_target_step, delta)
    
    # 如果是dryrun模式，绘制图表并退出
    if args.dryrun:
        print("📊 正在绘制步数计划图表...")
        plot_steps(steps_dict, daily_target_step)
        print("✅ 图表显示完成，程序退出")
        return
    
    # 显示部分关键时间点的步数计划
    print("📋 关键时间点的步数计划:")
    schedule_minutes = [(parse_time(t), t) for t, ratio in TIME_SCHEDULE]
    for minutes, time_str in schedule_minutes:
        step = steps_dict.get(minutes, 0)
        print(f"  {time_str} -> {int(step)} 步")
    
    # 记录下一次更新的时间
    next_update = datetime.now().replace(microsecond=0)
    
    # 记录今天的日期
    today = datetime.now().date()
    
    # 记录上次成功设置的步数，用于去重
    last_set_step = None
    
    print("🏃 自动更新开始运行...")
    print("按 Ctrl+C 停止程序")
    
    try:
        while True:
            # 检查是否到了新的一天
            if datetime.now().date() > today:
                # 重新生成步数计划
                print("📆 新的一天开始，重新生成步数计划...")
                daily_target_step = generate_daily_target_steps(total_step, delta)
                print(f"🎯 今日随机化目标步数: {daily_target_step}")
                steps_dict = calculate_steps_for_day(daily_target_step, delta)
                today = datetime.now().date()
                # 新的一天重置 last_set_step
                last_set_step = None
            
            # 获取当前应该设置的步数
            current_step = get_current_step(steps_dict, datetime.now())
            
            # 如果步数未变化则跳过
            if last_set_step is not None and current_step == last_set_step:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 当前步数: {current_step}（未变化，跳过更新）")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 当前步数: {current_step}")
                success, info = set_step(user, password, current_step)
                print(f"🧾 响应: {info}")
                if success:
                    last_set_step = current_step
                else:
                    print("⚠️  步数设置失败，请检查网络连接和账户信息")
            
            # 将间隔调整为 16 分钟
            next_update += timedelta(minutes=16)
            
            # 确保等待时间是未来的
            now = datetime.now()
            if next_update < now:
                next_update = now.replace(second=0, microsecond=0) + timedelta(minutes=16)
            
            # 计算睡眠时间
            sleep_time = (next_update - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\n👋 程序已停止")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()