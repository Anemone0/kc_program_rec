#!/usr/bin/env python
# -*-coding=utf-8-*-
import logging
import math
import random


def EzSA(x, obj_func, arrise_func, max_temperature=100, iter=10, zero=0.1, delta=0.8):
    res = []
    res.append(obj_func(x))  # 每次迭代后的结果

    best_x = x
    best_res = res[-1]
    temperature = max_temperature  # 初始温度
    # 停止迭代温度
    while temperature > zero:
        # 多次迭代扰动，一种蒙特卡洛方法，温度降低之前多次实验
        for i in range(iter):
            new_x = arrise_func(x)  # 产生随机扰动
            new_res = obj_func(new_x)  # 计算新结果

            delta_e = new_res - res[-1]  # 新老结果的差值，相当于能量
            if delta_e < 1e-8:  # 新结果好于旧结果，用新路线代替旧路线
                logging.info('Accept Good Res: {0}, Old Res: {1}'.format(new_res, res[-1]))
                x = new_x
                res.append(new_res)
                if best_res > res[-1]:
                    best_x = new_x
                    best_res = res[-1]
                print delta_e, res[-2], res[-1], best_res
            else:  # 温度越低，越不太可能接受新解；新老距离差值越大，越不太可能接受新解
                dell = math.exp(-delta_e / temperature)
                if dell > random.random():  # 以概率选择是否接受新解 p=exp(-ΔE/T)
                    logging.warning('Accept Bad Res: {0}, Old Res: {1}, Delta: {2}'.format(new_res, res[-1], dell))
                    x = new_x  # 可能得到较差的解
                    res.append(new_res)

        temperature = temperature * delta  # 温度不断下降
        process = 1 - math.log(zero / temperature) / math.log(zero / max_temperature)
        process *= 100
        logging.info('Now Temperature: {}'.format(temperature))
        logging.info('Process: {0} %'.format(process))
    logging.info("SA finish: {}".format(res))
    # print res
    if res[-1] > best_res:
        logging.warning('Final Result is NOT Good')
        logging.info('Final Result: {0}'.format(best_res))
        return best_x, best_res
    else:
        logging.info('Final Result: {0}'.format(res[-1]))
        return x, res[-1]


def obj_func(x):
    return x[0] ** 2 + x[1] ** 2


def arrise(x):
    return random.gauss(x[0],1),random.gauss(x[1],1),


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    x, res = EzSA([100, 102], obj_func, arrise, iter=10, max_temperature=100, delta=0.9)
    print x
    print res
