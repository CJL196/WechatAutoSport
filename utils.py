from dotenv import load_dotenv
import os
import requests


def load_credentials():
    """从.env文件加载用户名和密码"""
    load_dotenv()
    
    email = os.getenv('email')
    password = os.getenv('password')
    
    if not email or not password:
        raise ValueError("请确保.env文件中包含email和password配置")
    
    return email, password


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
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
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