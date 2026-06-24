import json
import os
from datetime import datetime

def get_log_dir():
    """获取日志目录，不存在则创建"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def get_log_filename():
    """获取当天的日志文件名"""
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(get_log_dir(), f'access_{today}.log')

def secure_log(level, message, data=None):
    """
    日志记录函数
    :param level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
    :param message: 日志消息
    :param data: 可选数据（显示原始内容）
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    if data is not None:
        if isinstance(data, dict):
            data_str = json.dumps(data, ensure_ascii=False)
        else:
            data_str = str(data)
        log_line = f"[{timestamp}] [{level}] {message} - 数据: {data_str}\n"
    else:
        log_line = f"[{timestamp}] [{level}] {message}\n"
    
    # 写入日志文件
    with open(get_log_filename(), 'a', encoding='utf-8') as f:
        f.write(log_line)
    
    # 同时输出到控制台
    print(log_line.strip())

# 便捷方法
def info(message, data=None):
    secure_log('INFO', message, data)

def warning(message, data=None):
    secure_log('WARNING', message, data)

def error(message, data=None):
    secure_log('ERROR', message, data)

def debug(message, data=None):
    secure_log('DEBUG', message, data)