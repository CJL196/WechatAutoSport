#!/usr/bin/env python3
"""
微信运动步数设置脚本
使用方法: python set_step.py <步数>
例如: python set_step.py 10000
"""

import os
import sys
import requests
from utils import load_credentials


def set_step(user, password, step):
    """
    设置微信运动步数
    
    Args:
        user (str): 用户名/邮箱
        password (str): 密码
        step (int): 步数
    
    Returns:
        bool: 是否设置成功
    """
    url = "https://ydapi.datu520.com/"
    
    data = {
        'user': user,
        'password': password,
        'step': str(step)
    }
    
    try:
        print(f"正在为用户 {user} 设置步数: {step}")
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 步数设置成功！当前步数: {step}")
            print(f"响应内容: {response.text}")
            return True
        else:
            print(f"❌ 设置失败，HTTP状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False


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
        # 从.env文件加载用户名和密码
        user, password = load_credentials()
        
        # 设置步数
        success = set_step(user, password, step)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
