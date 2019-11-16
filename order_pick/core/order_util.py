#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/15 20:02
# @Author  : Augus710
# @File    : util
# @Software: IntelliJ IDEA
# @desc    :
import logging.config

import yaml


class LogUtil:
    # 创建一个字典，用户保存配置
    dictConf = {}

    # 构造方法
    def __init__(self):
        # logYamlPath = self.LOGGER_CONF_PATH + os.sep + self.LOGGER_CONF_NAME
        logYamlPath = 'order_pick/conf/log.yml'
        self.dictConf = yaml.load(open(logYamlPath, 'r'))

    # 获得一个logger
    LOGGER_NAME = 'Logger'

    def getLogger(self, logger_name=LOGGER_NAME):
        logging.config.dictConfig(self.dictConf)
        logger = logging.getLogger(logger_name)
        return logger


_log_util = LogUtil()
log = _log_util.getLogger()
