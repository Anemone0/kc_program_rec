#!/usr/bin/env python
# coding=utf-8

# @file div.py
# @brief div
# @author x565178035,x565178035@126.com
# @version 1.0
# @date 2016-09-15 23:27

import sys
import os
import random

reload(sys)
sys.setdefaultencoding("utf-8")

PYTHON_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]


def div(li, ga_file, filename1, filename2):
    train = set()
    test = set()
    with open(os.path.join(PYTHON_FILE_PATH, '..', 'data', ga_file), 'r') as f:
        for line in f.readlines():
            each1 = line.replace('\r', '').replace('\n', '').split(',')
            each = [each1[0], each1[1], float(each1[2])]
            if len(each1[0]) != 0 and len(each1[1]) != 0:
                # if random.randint(0, 10) <= 6 or each[2]==10:
                if random.randint(0, 10) <= 6:
                    if line not in test:
                        train.add(line)
                else:
                    test.add(line)
    print train & test
    with open(filename1, 'w') as ff:
        for line in train:
            ff.write('{0},{1},{2}'.format(*line.split(',')))
    with open(filename2, 'w') as ff:
        for line in test:
            ff.write('{0},{1},{2}'.format(*line.split(',')))


if __name__ == '__main__':
    ga_file = "ga_with_repo_step_large_noten.csv"
    div([1, 2], ga_file, '../data/train.data', '../data/test.data')
    div([1, 2], ga_file, '../data/train1.data', '../data/test1.data')
    div([3, 4], ga_file, '../data/train2.data', '../data/test2.data')
    div([6, 7], ga_file, '../data/train3.data', '../data/test3.data')
