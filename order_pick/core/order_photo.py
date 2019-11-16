#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/13 0:37
# @Author  : Augus710
# @File    : order_photo
# @Software: IntelliJ IDEA
# @desc    :
import matplotlib
from matplotlib.backends._backend_tk import NavigationToolbar2Tk

#
# def order_table():
#     plt.figure(figsize=(10, 4))
#     # plt.axis('off')
#     # 解决中文显示问题
#     plt.rcParams['font.sans-serif'] = ['KaiTi']  # 指定默认字体
#     plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
#
#     # col_labels = ['', '库存', '', '计划产能', '', '订单', '', '']
#     col_labels = ['实际交货期', '累积库存', '本期库存', '产品', '数量', '产品', '数量', '交货期']
#     table_vals = [[1.01, 2, 2, P1, 2, '', 0, 0]]
#     # row_colors = ['red', 'gold', 'green']
#     # colColours=row_colors,
#     # plt.subplot(221)
#     plt.axis('off')
#     my_table = plt.table(cellText=table_vals, colWidths=[0.12] * 8, colLabels=col_labels,
#                          loc='best')
#     my_table.auto_set_font_size(False)
#     my_table.set_fontsize(8)
#     my_table.scale(1, 1)
#
#     # plt.subplot(222)
#     # plt.table(cellText=table_vals, colWidths=[0.1] * 8, colLabels=col_labels,
#     #           loc='best', fontsize=12)
#     # plt.axis('off')
#     plt.show()
#
# def delivery_product_bar(delivery_data, max_product_num):
#     fig = plt.figure(figsize=(12, 6))
#     plt.cla()
#     plt.barh(delivery_data, max_product_num)
#     plt.tick_params(labelsize=14)
#     font1 = {'family': 'simhei',
#              'weight': 'normal',
#              'size': 15, }
#     plt.xlabel('交货期', font1)
#     plt.ylabel('最大可交产品数', font1)
#     plt.title('xxxx', font1)
#     plt.show()
#     return fig
from order_pick.core.order import PRODUCT_NAME

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import tkinter as tk


class ProductModelPhoto():
    '''
    文件夹选择程序
        界面与逻辑分离
    '''

    def __init__(self, _from):
        '''初始化'''
        self._from = _from
        self.createWidgets()

    def createWidgets(self):
        '''界面'''
        fig = plt.figure(num=2, figsize=(8, 6), facecolor="pink", edgecolor='green', frameon=True)
        # 创建一副子图
        self.ax = plt.subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(fig, master=self._from)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(self.canvas, self._from)
        toolbar.update()
        # footframe = tk.Frame(master=self).pack(side=tk.BOTTOM)

        # self.draw()  # 绘图

    def draw(self, x, y):
        '''绘图逻辑'''
        # self.fig.clf()                  # 方式一：①清除整个Figure区域
        # self.ax = self.fig.add_subplot(111)    # ②重新分配Axes区域
        # self.ax.clear()                  # 方式二：①清除原来的Axes区域
        plt.cla()
        # 设置字体大小
        font1 = {'family': 'simhei',
                 'weight': 'normal',
                 'size': 15}
        # self.ax.scatter(x, y, s=3)  # 重新画

        bar = plt.bar(x, y, color='dodgerblue', width=0.4)
        bar[0].set_color('green')
        # 给条形图添加数据标注
        for x, y in enumerate(y):
            plt.text(x - 0.1, y + 0.2, "%s" % y)
        # 删除所有边框
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        # self.ax.spines['bottom'].set_visible(False)
        # self.ax.spines['left'].set_visible(False)
        plt.tick_params(labelsize=12)
        plt.xlabel('交货期', font1)
        plt.ylabel('产品数', font1)
        plt.title('单日最大可交产品数', font1)
        plt.grid(True, axis='both', ls=':', color='r', alpha=0.3)
        self.canvas.draw()

    # def _quit(self):
    #     '''退出'''
    #     self.quit()  # 停止 mainloop
    #     self.destroy()  # 销毁所有部件


import numpy as np


class ProductNumPhoto():
    def __init__(self, _from):
        '''初始化'''
        self._from = _from
        self._createWidgets()

    def _createWidgets(self):
        '''界面'''
        fig = plt.figure(num=2, figsize=(10, 6), edgecolor='green', frameon=True)  # facecolor="pink",
        # 创建一副子图
        self.ax = plt.subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(fig, master=self._from)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(self.canvas, self._from)
        toolbar.update()

    def draw(self, x, nums):
        '''绘图逻辑'''
        # self.fig.clf()                  # 方式一：①清除整个Figure区域
        # self.ax = self.fig.add_subplot(111)    # ②重新分配Axes区域
        # self.ax.clear()                  # 方式二：①清除原来的Axes区域
        plt.cla()
        # 设置字体大小
        font1 = {'family': 'simhei',
                 'weight': 'normal',
                 'size': 15}
        # 画堆叠柱状图
        color_list = plt.get_cmap('RdYlGn')(np.linspace(0, 1.0, len(nums)))
        for i in range(len(nums)):  # i表示list的索引值
            bottom = np.sum(nums[:i], axis=0)
            plt.bar(x, height=nums[i],
                    width=0.4,
                    bottom=bottom,
                    color=color_list[i], label=PRODUCT_NAME[i]
                    # alpha=0.5
                    )
            # 给条形图添加数据标注
        for i in range(len(nums[0])):
            for j in range(len(nums)):
                if nums[j][i] == 0:
                    continue
                bottom = np.sum(nums[:j], axis=0)
                if type(bottom) is np.ndarray:
                    bottom = bottom[i]
                bottom = int(bottom)
                k = nums[j][i]
                plt.text(i - 0.1, bottom + k, "%s %s" % (PRODUCT_NAME[j], k))
        # 删除所有边框
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        # self.ax.spines['bottom'].set_visible(False)
        # self.ax.spines['left'].set_visible(False)
        plt.tick_params(labelsize=12)
        plt.xlabel('交货期', font1)
        plt.ylabel('产品数', font1)
        plt.title('单日产品构成表', font1)
        # plt.grid(True, axis='both', ls=':', color='r', alpha=0.3)
        # plt.show()
        plt.legend(loc='best')
        self.canvas.draw()
