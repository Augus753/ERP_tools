#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/4 3:27
# @Author  : Augus710
# @File    : generater.py
# @Software: IntelliJ IDEA
# @desc    : ERP决策日历公式生成逻辑，每次可生成一年的数据。尽管该算法有4层for循环，但没有做多余的操作，总的循环了360次，还是极为高效的。
import numpy as np


def generate_fun(template):
    result = ''
    EMPTY_CELL = '	'  # 单元格，每个公式有空格
    months = np.linspace(1, 12, 12).reshape(4, 3)
    week_month = 5  # 每月算5周
    day_week = 6  # 每周算6天
    # 3*4
    for quarter in months:  # 遍历每个季度
        for week_idx in range(week_month):  # 一个月算5个周，5*6
            for month in quarter:
                result += '%s%s' % (day_week * week_idx + 1, EMPTY_CELL)
                for day in range(day_week * week_idx + 1, day_week * (week_idx + 1) + 1):
                    num = month + day * 0.01  # 生成日期
                    num = '%.2f' % num
                    result += template.replace('xxxx', num)
                    result += EMPTY_CELL
            result += '\n'
        result += '\n\n\n'
    # 去掉最后生成的四个换行符
    if len(result) > 4:
        result = result[:-4]

    with open('data/func.txt', 'w', encoding='utf-8') as f:
        f.write(result)


if __name__ == "__main__":
    template = '=CONCATENATE(IF(OR(COUNT(MATCH(xxxx,辅助表!C60:辅助表!N60,0))>0,COUNT(MATCH(xxxx,辅助表!P60:辅助表!W60,0))>0,COUNT(MATCH(xxxx,辅助表!Y60:辅助表!AB60,0))>0),\"C\",\"\"),IF(OR(COUNT(MATCH(xxxx,辅助表!AD60:辅助表!AO60,0))>0,COUNT(MATCH(xxxx,辅助表!AQ60:辅助表!BB60,0))>0,COUNT(MATCH(xxxx,辅助表!BD60:辅助表!BM60,0))>0,COUNT(MATCH(xxxx,辅助表!BO60:辅助表!BZ60,0))>0,COUNT(MATCH(xxxx,辅助表!GB60:辅助表!HK60,0))>0),\"生\",\"\"),IF(OR(COUNT(MATCH(xxxx,辅助表!CB60:辅助表!CM60,0))>0,COUNT(MATCH(xxxx,辅助表!CO60:辅助表!CZ60,0))>0,COUNT(MATCH(xxxx,辅助表!DB60:辅助表!DM60,0))>0),\"财\",\"\"),IF(OR(COUNT(MATCH(xxxx,辅助表!DO60:辅助表!DZ60,0))>0,COUNT(MATCH(xxxx,辅助表!EB60:辅助表!EM60,0))>0,COUNT(MATCH(xxxx,辅助表!EO60:辅助表!EZ60,0))>0,COUNT(MATCH(xxxx,辅助表!HM60:辅助表!IV60,0))>0,COUNT(MATCH(xxxx,辅助表!JZ60:辅助表!LU60,0))>0),\"采\",\"\"),IF(OR(COUNT(MATCH(xxxx,辅助表!FB60:辅助表!FM60,0))>0,COUNT(MATCH(xxxx,辅助表!IX60:辅助表!JX60,0))>0),\"销\",\"\"),IF(xxxx<EL1,\" \",\"\"),IF(xxxx=EL1,\"  \",\"\"))'
    '''
        修改模板的相关参数，包括，辅助表!C60，EL1，对应生成不同年份的函数
    '''
    generate_fun(template)
