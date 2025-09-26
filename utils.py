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
        tuple[bool, dict]: (是否设置成功, 网站返回的信息字典)
    """
    # 从环境变量读取 api_url，默认使用新的 API 地址
    url = os.getenv('api_url', 'https://wzz.wangzouzou.com/motion/api/motion/Xiaomi')
    
    headers = {
        'Origin': 'https://m.cqzz.top',
        'Referer': 'https://m.cqzz.top/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    
    data = {
        'phone': user,
        'pwd': password,
        'num': str(step)
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        # 尝试解析为 JSON；若失败则构造统一的字典
        try:
            parsed = response.json()
        except ValueError:
            parsed = {
                'code': response.status_code,
                'msg': 'non_json_response',
                'data': response.text
            }
        
        if not isinstance(parsed, dict):
            parsed = {
                'code': response.status_code,
                'msg': 'ok' if response.ok else 'http_error',
                'data': parsed
            }
        
        # 根据常见字段或 HTTP 状态码判断成功与否
        success = False
        code_value = parsed.get('code') if isinstance(parsed, dict) else None
        if isinstance(code_value, int):
            success = (code_value == 200)
        elif isinstance(code_value, str):
            success = (code_value == '200')
        elif isinstance(parsed, dict) and 'success' in parsed:
            success = bool(parsed.get('success'))
        else:
            success = (response.status_code == 200)
        
        return success, parsed
            
    except requests.exceptions.RequestException as e:
        return False, {'code': -1, 'msg': 'network_error', 'data': str(e)}
    except Exception as e:
        return False, {'code': -2, 'msg': 'unexpected_error', 'data': str(e)}