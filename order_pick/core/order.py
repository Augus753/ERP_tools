#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/11 11:58
# @Author  : Augus710
# @File    : order
# @Software: IntelliJ IDEA
# @desc    :

'''
情况，1、当日订单不足，可以往前推，使用之前生产的产品
2、若之前生产的产品也不足，自动转化当日其他产品订单为所选产品，若依然不足，转化之前的其他产品订单。
'''
import copy
import random

import xlsxwriter

# from code.order_util import log
from order_pick.core.order_util import log

P1, P2, P3, P4, P5 = 'P1', 'P2', 'P3', 'P4', 'P5'
PRODUCT_NAME = (P1, P2, P3, P4, P5)
DELIVERY_SUCCESS = 0
DELIVERY_UNKNOW = 1
DELIVERY_FAIL = 2
ORDER_FILE_NAME = r'订单列表.xlsx'
DEFAULT_PRODUCTION_CYCLE = 48


class Config():
    def __init__(self, production_cycle=DEFAULT_PRODUCTION_CYCLE):
        self.first_production_cycle = None
        self.order_file_name = ORDER_FILE_NAME
        self.cal_first_production_cycle(production_cycle)

    def cal_first_production_cycle(
            self, production_cycle=DEFAULT_PRODUCTION_CYCLE):
        self.first_production_cycle = (
                                              1 + int(production_cycle / 30)) + production_cycle % 30 * 0.01
        log.info('更新配置，%s' % self)

    def get_production_cycle(self):
        return int(self.first_production_cycle - 1) * 30 + \
               int(round(self.first_production_cycle - int(self.first_production_cycle), 4) * 100)

    def __str__(self):
        return str(self.__dict__)


class Order():
    def __init__(
            self,
            product_name,
            num,
            price,
            delivery_date,
            payment_day,
            idx=None,
            first_delivery=True):
        if idx is None:
            self.idx = '%s_%d' % (product_name, random.randint(1000, 9999))
        self.delivery_date = delivery_date
        self.product_name = product_name
        self.num = num
        self.price = price
        self.payment_day = payment_day
        self.rel_delivery_date = None
        self.first_delivery = first_delivery  # 是否是完整订单
        self.delivery_status = DELIVERY_UNKNOW

    def format_to_show(self):
        return [
            self.product_name, self.num, self.num * self.price,
            self.delivery_date, self.payment_day, self.rel_delivery_date
        ]

    def __str__(self):
        # return 'delivery_date：%s，product_name：%s，num：%s' %
        # (self.delivery_date, self.product_name, self.num)
        return str(self.__dict__)


class ProductInfo():
    def __init__(self, name, num):
        self.product_name = name
        self.num = num
        # 预计剩余产品数，若交单成功，才改变self.num
        self.pre_num = num

    # 交单成功，修改产品数
    def delivery_success(self):
        self.num = self.pre_num

    # 交单前，重置预计产品数
    def start_delivery(self):
        self.pre_num = self.num

    def __str__(self):
        # return 'name：%s，num：%s' % (self.name, self.num)
        return str(self.__dict__)


class ProductModelDay():
    def __init__(self, delivery_date, config: Config, products=[]):
        self.delivery_date = delivery_date
        self.products = []
        # 当前交货期所生产的产品剩余可交货数量
        self.rest_num = 0
        # 当前交货期剩余可交货数量
        self.max_rest_num = 0
        self.orders = []
        self.add_product(products)
        self.config = config

    def get_product_num(self):
        nums = [0] * len(PRODUCT_NAME)
        for p in self.products:
            idx = PRODUCT_NAME.index(p.product_name)
            nums[idx] = p.num
        return nums

    def delivery_order(self, order: Order):
        def _delivery(p, order):
            p.start_delivery()
            if p.pre_num <= 0:
                return False
                # delivery_num：剩余产品数
            rest_num = p.pre_num - order.num
            p.pre_num = max(rest_num, 0)
            log.info(
                'product_name；%s，rest_num：%d，p.pre_num：%d，order.num：%d' %
                (p.product_name, rest_num, p.pre_num, order.num))
            # 记录当前交货期库存总数
            # self.rest_num -= (order.num + min(rest_num, 0))
            if order.first_delivery:
                # 订单完整时，记录订单信息
                order.rel_delivery_date = self.delivery_date
                self.orders.append(copy.deepcopy(order))
                order.first_delivery = False  # 只要交过单，就不算完整订单
            if rest_num < 0:
                # 订单有剩余
                # self.rest_num -= (order.num + rest_num)
                order.num = abs(rest_num)
            else:
                # self.rest_num -= order.num
                # 完成交单，交单成功
                log.info('完成交单，交单成功，%d', p.pre_num)
                # p.delivery_success()
                order.num = 0
                return True
            return False

        # 优先交于计划相同产品的订单
        # 第一次占用同类别的数量
        log.info('第一次占用同类别的数量，%s' % order)
        for p in self.products:
            if p.product_name == order.product_name:
                if _delivery(p, order):
                    return
                break
        # if order.delivery_date < self.config.first_production_cycle:
        #     return
        log.info('第二次，当前类别产品没有数量了，占用其他类别的数量，%s' % order)
        # 第二次，当前类别产品没有数量了，占用其他类别的数量
        for p in self.products:
            if self.delivery_date < self.config.first_production_cycle:
                continue
            if p.product_name != order.product_name:
                if _delivery(p, order):
                    return

    def possible_order(self, order):
        return (self.delivery_date <= order.delivery_date) & \
               (self.rest_num > 0)

    def add_product(self, products):
        for product in products:
            self.rest_num += product.num
            self.products.append(product)

    def record_delivery_status(self, order: Order, delivery_status):
        for o in self.orders:
            if o.idx == order.idx:
                o.delivery_status = delivery_status
                return

    def count_rest_num(self):
        num = 0
        for product in self.products:
            num += product.num
        self.rest_num = num

    def __str__(self):
        return ' {\n delivery_date：%s，\n product：%s，\n order：%s，\nrest_num：%d \n max_rest_num：%d \n config：%s},' % \
               (self.delivery_date, [str(p) for p in self.products], [str(o) for o in self.orders], self.rest_num,
                self.max_rest_num, self.config)


class ProductModelYear():
    def __init__(self, config: Config):
        self.num = 0
        # self.product_model_days = SortedSet(key=lambda x: x.delivery_date)
        self.product_model_days = []
        self.order_pool = []
        # 生产周期
        self.config = config

    # 增加各个交货期模型
    def add_product_model(self, product_model_day: ProductModelDay):
        # 保证交货期不重复
        if self.contain(product_model_day):
            return
        product_model_day.config = self.config
        self.product_model_days.append(product_model_day)
        self.product_model_days.sort(
            key=lambda x: x.delivery_date, reverse=True)
        self.num += product_model_day.rest_num

    # 增加订单
    def add_order(self, order):
        # 加入订单
        # '''
        #     每个交货期里，优先改日期，其次改产品
        #     实时修改每个日期的产品数
        #     按日期，当天内能交完，通过。
        #     按日期，当天内不能交完，转换当天的产品，若依然不能交完，推到上一天
        #     循环词过程，直到全部交货期测试结束，若不能交完，则失败
        # '''
        self.order_pool.append(order)
        # 首次添加，寻找可能的交货期
        delivery_idx = self._get_check_day(order)
        delivery_status = DELIVERY_FAIL
        if delivery_idx < 0:
            log.info('交单失败，%s' % order)
            return delivery_status
        # product_model_days按照交货期倒叙，因此需要从第delivery_idx开始计算，跳过前面不符合要求的日期
        day_num = len(self.product_model_days)
        for i in range(delivery_idx, day_num):
            product_model = self.product_model_days[i]
            product_model.delivery_order(order)
            if order.num == 0:
                # 订单数量为0，交单结束
                delivery_status = DELIVERY_SUCCESS
                break
        for j in range(delivery_idx, day_num):
            product_model = self.product_model_days[j]
            if delivery_status == DELIVERY_SUCCESS:
                for p in product_model.products:
                    log.info('交单成功，%s' % p)
                    p.delivery_success()
            product_model.record_delivery_status(order, delivery_status)
        return delivery_status

    # 获取与订单信息相符合的最大检测范围
    def _get_check_day(self, order):
        for i in range(len(self.product_model_days)):
            product_model = self.product_model_days[i]
            if product_model.possible_order(order):
                return i
        return -1

    def __str__(self):
        a = 'num：%d，' % self.num
        for day in self.product_model_days:
            a += str(day) + "\n\n"
        return a

    def contain(self, product_model_day):
        for day in self.product_model_days:
            if day.delivery_date == product_model_day.delivery_date:
                return True
        return False

    def count_product_num(self):
        '''
            统计每期常量剩余数
            统计每期最大可交库存数
        '''
        day_num = self.count_day()
        all_product_num = 0
        for i in reversed(range(day_num)):
            product_model_day = self.product_model_days[i]
            product_model_day.count_rest_num()
            # 当前交货期生产的产品已出售，则认为当前交货期总可交货量为0（因为选单过程中，应尽量把订单往后排，
            # 在本期生产的产品已出售的情况下，后一期可以交的，那这一期就不算进去了，，减少数据量，避免干扰）
            if product_model_day.rest_num > 0:
                product_model_day.max_rest_num = product_model_day.rest_num + all_product_num
                all_product_num = product_model_day.max_rest_num
                log.debug('修改最大剩余数，%s' % product_model_day)
            else:
                product_model_day.max_rest_num = 0

    def count_day(self):
        return len(self.product_model_days)

    def get_orders(self):
        return [
            order.format_to_show() for product_model_day in self.product_model_days
            for order in product_model_day.orders
        ]

    def get_success_orders(self):
        return [
            order.format_to_show() for product_model_day in self.product_model_days
            for order in product_model_day.orders if order.delivery_status == DELIVERY_SUCCESS
        ]

    def set_config(self, config):
        self.config = config
        for day in self.product_model_days:
            day.config = config

    def save_to_excel(self):
        order_list = self.get_success_orders()
        workbook = xlsxwriter.Workbook(
            self.config.order_file_name)  # 创建一个Excel文件
        worksheet = workbook.add_worksheet()  # 创建一个sheet
        # 产品	数量	总额	交货期	账期	实际交货期
        title = [U'产品', U'数量', U'总额', U'交货期', U'账期', U'实际交货期']  # 表格title
        worksheet.write_row('A1', title)
        for i in range(1, len(order_list) + 1):
            row = 'A' + str(i + 1)
            worksheet.write_row(row, order_list[i - 1])
        workbook.close()


# ('日期', '1.01', '6.29', '8.17', '10.05', '11.23', '5.29', '4.17', '3.05', '2.23', '1.23', '5.23')
# ('P1', '2', '3', '7', '7', '7', '2', '3', '7', '7', '7', '3')
def parse_product(products, config: Config):
    # 按照
    delivery_dates = products[0]
    products = products[1:]
    product_model_year = ProductModelYear(config)
    for i in range(1, len(delivery_dates)):
        delivery_date = delivery_dates[i]
        p = [ProductInfo(str(nums[0]).upper(), int(nums[i]))
             for nums in products]
        product_model_day = ProductModelDay(float(delivery_date), config, p)
        product_model_year.add_product_model(product_model_day)
    product_model_year.count_product_num()
    return product_model_year


def parse_order(product_model_year: ProductModelYear, order_text):
    delivery_status = product_model_year.add_order(
        Order(
            order_text[0],
            order_text[1],
            order_text[2],
            order_text[3],
            order_text[4]))
    log.info('交单状态，%s' % (delivery_status is DELIVERY_SUCCESS))
    if delivery_status != DELIVERY_SUCCESS:
        return False
    product_model_year.count_product_num()
    return True


def format_to_all_product(product_model_year: ProductModelYear):
    products = ([], [])
    rest_flag = False
    for i in reversed(range(len(product_model_year.product_model_days))):
        product_model_day = product_model_year.product_model_days[i]
        if product_model_day.max_rest_num > 0:
            rest_flag = True
            products[0].append('%s ' % product_model_day.delivery_date)
            products[1].append(product_model_day.max_rest_num)
    # 交完所有订单，添加默认值0
    if rest_flag is False:
        products[0].append(0)
        products[1].append(0)
    return products


def format_to_product_name(product_model_year: ProductModelYear):
    num = 0
    new_day = []
    for product_model_day in product_model_year.product_model_days:
        if product_model_day.max_rest_num > 0:
            num += 1
            new_day.append(product_model_day)
    if num == 0:
        num = 1

    all_data = []
    for i in range(len(PRODUCT_NAME)):
        data = [0 for j in range(num)]
        all_data.append(data)
    products = ([], all_data)
    rest_flag = False
    new_day_len = len(new_day)
    for i in reversed(range(len(new_day))):
        product_model_day = new_day[i]
        if product_model_day.max_rest_num > 0:
            rest_flag = True
            products[0].append('%s ' % product_model_day.delivery_date)
            for p in product_model_day.products:
                if p.num == 0:
                    continue
                idx = PRODUCT_NAME.index(p.product_name)
                products[1][idx][new_day_len - 1 - i] = p.num
    if rest_flag is False:
        products[0].append(0)
    return products
