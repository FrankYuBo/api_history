"""
-*- coding:utf-8 -*-
@File: log.py
@Author:frank yu
@DateTime: 2023.08.17 15:07
@Contact: frankyu112058@gmail.com
@Description:
日志封装
1. 可以多线程、多进程使用
2. 默认只有控制台handler，可以通过set_std、set_file、set_std_file设置，尤其是想保存到文件时
3. 其他地方使用只import log对象即可
"""
import functools
import logging
import os
import random
import sys
import multiprocessing
import time
from shutil import copyfile

# 获取当前执行代码的文件路径
current_file = os.path.abspath(__file__)

# 获取当前执行代码所在的目录
current_directory = os.path.dirname(current_file)

# log directory
LOG_DIR = current_directory+"/logs"
# level for stdout
STD_LEVEL = logging.DEBUG
# level for file
FILE_LEVEL = logging.DEBUG


class Log:
    def __init__(self, log_dir=LOG_DIR):
        """
        function:init create log file, judge if log file is too bigger
        :param log_dir: directory of logs
        """
        log_path = log_dir + "/log"
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
            os.chmod(log_dir, 0o777)
        if not os.path.exists(log_path):
            f = open(log_path, mode='w', encoding='utf-8')
            f.close()
            os.chmod(log_path, 0o777)
        # if log file is more than 1MB, copy to a file and clear log file
        if os.path.getsize(log_path) / 1048576 > 1:
            # print(os.path.getsize(log_path))
            copyfile(log_path, log_dir + "/log" + str(time.time()).replace(".", ""))
            with open(log_path, 'w') as f:
                f.truncate()
                f.close()
        self.logger_format = logging.Formatter('[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)-8s] %('
                                               'message)s')

        self.logger = logging.getLogger(str(random.random()))
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)

        self.filehandler = logging.FileHandler(log_path, mode='a')
        self.filehandler.setLevel(FILE_LEVEL)
        self.filehandler.setFormatter(self.logger_format)

        self.stdouthandler = logging.StreamHandler(sys.stdout)
        self.stdouthandler.setLevel(STD_LEVEL)
        self.stdouthandler.setFormatter(self.logger_format)

        self.logger.addHandler(self.stdouthandler)

        self.__lock = multiprocessing.Lock()

    def set_std_file(self):
        """
        function: set std and file handler
        return: None
        """
        self.__lock.acquire()
        self.logger.addHandler(self.stdouthandler)
        self.logger.addHandler(self.filehandler)
        self.__lock.release()

    def set_std(self):
        """
        function: set std handler
        """
        self.__lock.acquire()
        self.logger.removeHandler(self.filehandler)
        self.logger.addHandler(self.stdouthandler)
        self.__lock.release()

    def set_file(self):
        """
        function: set file handler
        """
        self.__lock.acquire()
        self.logger.removeHandler(self.stdouthandler)
        self.logger.addHandler(self.filehandler)
        self.__lock.release()

    def log_wrapper(self, func):
        """
        function: record arg and result of functions
        :param func: 自动获取名字，不需要填写
        :return: wrapper
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.debug(getattr(func, "__name__") + " call " + str(args) + str(kwargs))
            ret = func(*args, **kwargs)
            self.logger.debug(getattr(func, "__name__") + " return " + str(ret))
            return ret

        return wrapper


log = Log()