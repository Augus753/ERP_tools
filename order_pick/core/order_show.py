#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/12 11:24
# @Author  : Augus710
# @File    : order_show1
# @Software: IntelliJ IDEA
# @desc    :
from tkinter import *
# 导入ttk
from tkinter import ttk
from tkinter.ttk import Treeview

import easygui

from order_pick.core.order import parse_product, format_to_all_product, format_to_product_name, parse_order, Config
from order_pick.core.order_photo import ProductModelPhoto, ProductNumPhoto
from order_pick.core.order_util import log


def handlerAdaptor(fun, **kwds):
    '''事件处理函数的适配器，相当于中介，那个event是从那里来的呢，我也纳闷，这也许就是python的伟大之处吧'''
    return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("选单软件")
        self.root.geometry("1366x768")
        self.plain_product = None
        self.treeview = None
        self.product_model_photo = None
        self.product_ploto = None
        self.product_model_year = None
        self.order_input = [None] * 5  # 每个订单需要五条信息
        self.config_win = None
        self.config = Config()
        self._create_menu()
        self.initWidgets()

    def _create_menu(self):
        menubar = Menu(self.root)
        menubar.add_cascade(label='参数设置', command=self.config_operate)
        self.root.grid()
        self.root.config(menu=menubar)

    def initWidgets(self):

        self.frame_left_top = Frame(self.root)
        self.frame_left_top.place(x=10, y=10, width=550, height=130)
        self.frame_right_1 = Frame(self.root)
        self.frame_right_1.place(x=610, y=10, width=600, height=150)
        self.frame_order_input = Frame(self.root, background="PaleGoldenrod")
        self.frame_order_input.place(x=20, y=250, width=200, height=305)
        self.frame_right_2 = Frame(self.root)
        self.frame_right_2.place(x=400, y=150, width=950, height=270)
        self.frame_right_3 = Frame(self.root)
        self.frame_right_3.place(x=400, y=440, width=950, height=270)

        '''
            左上角文本输入框
        '''
        self.plain_product_text = Text(self.frame_left_top,
                                       width=400,
                                       height=10,
                                       font=('StSong', 10), )
        self.plain_product_text.grid(row=0, column=0, sticky=NSEW)

        self.order_button = Button(self.root, text="输入完成", font=(
            'Arial', 15), bg='GreenYellow', command=self.input_product)
        self.order_button.place(x=200, y=150, width=80, height=30)

        '''
            中间输入框
        '''
        Label(
            self.frame_order_input,
            text='输入订单信息',
            font=("Arial, 12")).place(
            x=5,
            y=5,
            width=190,
            height=40)
        Label(
            self.frame_order_input,
            text='产品',
            font=("Arial, 12")).place(
            x=5,
            y=55,
            width=45,
            height=45)
        Label(
            self.frame_order_input,
            text='数量',
            font=("Arial, 12")).place(
            x=5,
            y=105,
            width=45,
            height=45)
        Label(
            self.frame_order_input,
            text='单价',
            font=("Arial, 12")).place(
            x=5,
            y=155,
            width=45,
            height=45)
        Label(
            self.frame_order_input,
            text='交货期',
            font=("Arial, 12")).place(
            x=5,
            y=205,
            width=45,
            height=45)
        Label(
            self.frame_order_input,
            text='账期',
            font=("Arial, 12")).place(
            x=5,
            y=255,
            width=45,
            height=45)

        def input_order_text(x, y, width, height):
            order_var = StringVar()
            e = Entry(self.frame_order_input, textvariable=order_var)
            e.place(x=x, y=y, width=width, height=height)
            return order_var

        order_var_0 = input_order_text(x=50, y=55, width=150, height=45)
        order_var_1 = input_order_text(x=50, y=105, width=150, height=45)
        order_var_2 = input_order_text(x=50, y=155, width=150, height=45)
        order_var_3 = input_order_text(x=50, y=205, width=150, height=45)
        order_var_4 = input_order_text(x=50, y=255, width=150, height=45)
        '''
            按钮
        '''
        order_vars = [
            order_var_0,
            order_var_1,
            order_var_2,
            order_var_3,
            order_var_4]
        input_button = Button(self.root, text="插入\n订单",
                              font=('Arial', 15), bg='GreenYellow')
        input_button.place(x=300, y=350, width=50, height=100)
        input_button.bind(
            '<Button-1>',
            handlerAdaptor(
                self.add_order,
                order_vars=order_vars))

        Button(
            self.root,
            text="生成\n模型",
            font=('Arial', 15),
            bg='GreenYellow',
            command=self.generate_model) \
            .place(
            x=1250,
            y=50,
            width=50,
            height=80)

        Button(
            self.root,
            text="查看订单",
            font=('Arial', 15),
            bg='GreenYellow',
            command=self.show_order) \
            .place(
            x=100,
            y=600,
            width=100,
            height=50)

    def config_operate(self):
        self.config_win = ConfigWindow(self.config)
        self.config = self.config_win.config
        if self.product_model_year is not None:
            self.product_model_year.set_config(self.config)

    def delButton(self):
        if self.treeview:
            x = self.treeview.get_children()
            for item in x:
                self.treeview.delete(item)

    def input_product(self):
        text = str(
            self.plain_product_text.get(
                "0.0", "end")).replace(
            '库存', '1.01').split('\n')
        self.plain_product = []
        for i, t in enumerate(text):
            new_list = [j for j in t.split('	') if j != '']
            if len(new_list) > 0:
                self.plain_product.append(new_list)
        log.debug('解析计划产品结果：，%s' % self.plain_product)
        if self.treeview is None:
            self.treeview = ttk.Treeview(self.frame_right_1, show="headings")
            self.treeview.place(x=0, y=10, width=800, height=300)
        if len(self.plain_product) == 0:
            easygui.msgbox('请按格式输入计划产品信息')
            return
        columns = self.plain_product[0]
        self.treeview['columns'] = columns
        self.delButton()
        for col in self.plain_product[0]:
            self.treeview.column(
                '%s' %
                col,
                width=50,
                anchor='center')  # 表示列,不显示

        self.treeview.pack(side=RIGHT, fill=BOTH)
        i = 0
        for p in self.plain_product:
            i += 1
            self.treeview.insert('', i, values=p)

    def add_order(self, event, order_vars):
        order = [order_var.get()
                 for order_var in order_vars if order_var.get() is not None]
        if len(order) != 5:
            easygui.msgbox('请完善订单内容，%s' % order)
            return
        if self.product_model_year is None:
            easygui.msgbox('请完设置计划产品数')
            return

        def ckeck_order(order):
            return [str(order[0]).upper(), int(order[1]), int(
                order[2]), float(order[3]), int(order[4])]

        try:
            new_order = ckeck_order(order)
        except Exception as e:
            easygui.msgbox('输入的订单信息有误')
            log.error('输入的订单有误，%s' % e)
            return
        delivery_status = parse_order(self.product_model_year, new_order)
        if delivery_status is False:
            easygui.msgbox('交单失败，库存不足')
            return
        delivery_products = format_to_all_product(self.product_model_year)
        if self.product_model_photo is None:
            self.product_model_photo = ProductModelPhoto(self.frame_right_2)
        self.product_model_photo.draw(
            delivery_products[0], delivery_products[1])

        delivery_products = format_to_product_name(self.product_model_year)
        # delivery_products[1] 当无数据时需要初始化填充
        if self.product_ploto is None:
            self.product_ploto = ProductNumPhoto(self.frame_right_3)
        self.product_ploto.draw(delivery_products[0], delivery_products[1])
        easygui.msgbox('成功插入订单')

    def show_order(self):
        sub_win = SubWindow(self.product_model_year)
        sub_win.show_data()

    def generate_model(self):
        x = self.treeview.get_children()
        products = []
        for item in x:
            item_text = self.treeview.item(item, "values")
            products.append(item_text)
        self.product_model_year = parse_product(products, self.config)
        delivery_products = format_to_all_product(self.product_model_year)
        if self.product_model_photo is None:
            self.product_model_photo = ProductModelPhoto(self.frame_right_2)
        self.product_model_photo.draw(
            delivery_products[0], delivery_products[1])

        delivery_products = format_to_product_name(self.product_model_year)
        if self.product_ploto is None:
            self.product_ploto = ProductNumPhoto(self.frame_right_3)
        self.product_ploto.draw(delivery_products[0], delivery_products[1])


class ConfigWindow:
    def __init__(self, config):
        self.top = Toplevel()
        self.config = config
        self._create()

    def _create(self):
        self.top.title('参数设置')
        columns = ("名称", "参数")
        treeview = ttk.Treeview(self.top, height=50, show="headings", columns=columns)  # 表格
        treeview.column("名称", width=100, anchor='center')  # 表示列,不显示
        treeview.column("参数", width=300, anchor='center')
        treeview.heading("名称", text="名称")  # 显示表头
        treeview.heading("参数", text="参数")
        treeview.pack(side=LEFT, fill=BOTH)

        names = ['生产周期', '订单保存文件']
        nums = [self.config.get_production_cycle(), self.config.order_file_name]
        for i in range(min(len(names), len(nums))):  # 写入数据
            treeview.insert('', i, values=(names[i], nums[i]))

        self.treeview = treeview
        treeview.bind('<Double-1>', self.set_cell_value)  # 双击左键进入编辑
        newb = ttk.Button(self.top, text='确定', width=20, command=self.config_update)
        newb.place(x=120, y=(len(names) - 1) * 20 + 45)

    def set_cell_value(self, event):  # 双击进入编辑状态
        for item in self.treeview.selection():
            # item = I001
            item_text = self.treeview.item(item, "values")
            # print(item_text[0:2])  # 输出所选行的值
        column = self.treeview.identify_column(event.x)  # 列
        row = self.treeview.identify_row(event.y)  # 行
        cn = int(str(column).replace('#', ''))
        if cn == 1:  # 不修改配置名
            return
        rn = int(str(row).replace('I', ''))
        entryedit = Text(self.top, width=10 + (cn - 1) * 16, height=1)
        entryedit.place(x=16 + (cn - 1) * 130, y=6 + rn * 20)
        entryedit.insert(0.0, item_text[1])

        def saveedit():
            self.treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
            entryedit.destroy()
            okb.destroy()

        okb = ttk.Button(self.top, text='OK', width=4, command=saveedit)
        okb.place(x=90 + (cn - 1) * 242, y=2 + rn * 20)

    def config_update(self):
        import xlwt
        x = self.treeview.get_children()
        try:
            production_cycle = int(str(self.treeview.item(x[0], "values")[1]).replace('\n', ''))
            file_name = str(self.treeview.item(x[1], "values")[1]).replace('\n', '')
            workbook = xlwt.Workbook(encoding='utf-8')  # 新建工作簿
            sheet1 = workbook.add_sheet("测试表格")  # 新建sheet
            workbook.save(file_name)  # 保存
        except Exception as e:
            easygui.msgbox('参数配置有误')
            log.error('参数配置有误，%s' % e)
            return
        # for i,item in enumerate(x):
        #     item_text = self.treeview.item(item, "values")
        self.config.cal_first_production_cycle(production_cycle)
        self.config.order_file_name = file_name
        easygui.msgbox('修改参数成功%d' % production_cycle)


class SubWindow:
    def __init__(self, product_model_year):
        self.product_model_year = product_model_year
        self.top = Toplevel()
        self._create_menu()
        self.tree = self._create()

    def _create(self):
        self.top.title('订单列表')

        # 产品	数量	总额	交货期	账期	实际交货期
        tree = Treeview(
            self.top,
            columns=(
                '产品',
                '数量',
                '总额',
                '交货期',
                '账期',
                '实际交货期'),
            show='headings')  # 表格
        tree.column("产品", width=100, anchor='center')  # 表示列,不显示
        tree.column("数量", width=100, anchor='center')
        tree.column("总额", width=100, anchor='center')
        tree.column("交货期", width=100, anchor='center')
        tree.column("账期", width=100, anchor='center')
        tree.column("实际交货期", width=100, anchor='center')

        tree.heading("产品", text="产品")  # 显示表头
        tree.heading("数量", text="数量")
        tree.heading("总额", text="总额")
        tree.heading("交货期", text="交货期")
        tree.heading("账期", text="账期")
        tree.heading("实际交货期", text="实际交货期")
        tree.pack()
        return tree

    def flush_order_list(self):
        def del_button():
            x = self.tree.get_children()
            for item in x:
                self.tree.delete(item)

        del_button()
        self.show_data()
        easygui.msgbox('刷新列表成功')

    def download_order(self):
        self.product_model_year.save_to_excel()
        easygui.msgbox('下载订单成功')

    def show_data(self):
        order_list = self.product_model_year.get_success_orders()
        for i, order in enumerate(order_list):
            self.tree.insert('', i, values=order)  # 插入数据，

    def _create_menu(self):
        menubar = Menu(self.top)
        menubar.add_cascade(label='刷新列表', command=self.flush_order_list)
        menubar.add_cascade(label='下载订单', command=self.download_order)
        self.top.grid()
        self.top.config(menu=menubar)