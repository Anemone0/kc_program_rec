#!/usr/bin/env python
# -*-coding=utf-8-*-
import logging
import math
import random


def EzSA(x, obj_func, arrise_func, iter=10, zero=1):
    res = []
    res.append(obj_func(x))  # 每次迭代后的结果
    temperature = 100.0  # 初始温度
    delta = 0.9
    # 停止迭代温度
    while temperature > zero:
        # 多次迭代扰动，一种蒙特卡洛方法，温度降低之前多次实验
        for i in range(iter):
            new_x = arrise_func(x)  # 产生随机扰动
            new_res = obj_func(new_x)  # 计算新结果

            delta_e = new_res - res[-1]  # 新老结果的差值，相当于能量
            if delta_e < 0:  # 新结果好于旧结果，用新路线代替旧路线
                x = new_x
                res.append(new_res)
            else:  # 温度越低，越不太可能接受新解；新老距离差值越大，越不太可能接受新解
                if math.exp(-delta_e / temperature) > random.random():  # 以概率选择是否接受新解 p=exp(-ΔE/T)
                    x = new_x  # 可能得到较差的解
                    res.append(new_res)

        temperature = temperature * delta  # 温度不断下降
        print 'Now Temperature: ', temperature
        print 'Process: ', math.log(temperature / temperature) / math.log(delta) / (
        math.log(zero / temperature) / math.log(delta))
    logging.info("SA finish: ", res)
    return x, res[-1]


def obj_func(x):
    return x[0] ** 2 + x[1] ** 2


def arrise(x):
    return random.gauss(x[0],1),random.gauss(x[1],1),


if __name__ == '__main__':
    x,res=EzSA([100, 102], obj_func, arrise,iter=1000)
    print x
    print res
