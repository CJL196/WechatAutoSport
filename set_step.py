#!/usr/bin/env python3
"""
微信运动步数设置脚本
使用方法: python set_step.py <步数>
例如: python set_step.py 10000
"""

import os
import sys
from dotenv import load_dotenv
from utils import load_credentials, set_step


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python set_step.py <步数>")
        print("例如: python set_step.py 10000")
        sys.exit(1)
    
    try:
        step = int(sys.argv[1])
        if step < 0:
            print("❌ 步数不能为负数")
            sys.exit(1)
        if step > 98800:
            print("❌ 步数不能超过98800")
            sys.exit(1)
    except ValueError:
        print("❌ 请输入有效的数字")
        sys.exit(1)
    
    try:
        # 加载环境变量
        load_dotenv()
        
        # 显示当前配置
        base_url = os.getenv('api_url', 'https://wzz.wangzouzou.com/motion/api/motion/Xiaomi')
        print(f"🌐 使用API地址: {base_url}")
        
        # 从.env文件加载用户名和密码
        user, password = load_credentials()
        
        print(f"👤 用户: {user}")
        print(f"🎯 目标步数: {step}")
        
        # 设置步数
        success, info = set_step(user, password, step)
        print(f"🧾 响应: {info}")
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
