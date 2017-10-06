#!/usr/bin/env python
# -*-coding=utf-8-*-

import os
import random
import shutil

PYTHON_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]

PROJECT = '_step_large8000'

LIKE = 1
DISLIKE = -1


def get_path(train, test, rec):
    data_path = os.path.join(PYTHON_FILE_PATH, '..', 'data')
    train_path = os.path.join(data_path, '{}.data'.format(train))
    trainbk_path = os.path.join(data_path, '{}.data.bk'.format(train))
    test_path = os.path.join(data_path, '{}.data'.format(test))
    testbk_path = os.path.join(data_path, '{}.data.bk'.format(test))
    rec_path = os.path.join(data_path, '{}.csv'.format(rec))
    recbk_path = os.path.join(data_path, '{}.csv.bk'.format(rec))
    return train_path, trainbk_path, test_path, testbk_path, rec_path, recbk_path


def eval_feedback(train, test, rec):
    train_path, trainbk_path, test_path, testbk_path, rec_path, recbk_path = get_path(train, test, rec)
    '''处理测试集'''
    dict_test = dict()
    with open(test_path, 'r') as f:
        for each in f.readlines():
            tup = each.replace('\n', '').split(',')
            dict_test[(tup[0], tup[1])] = float(tup[2])
    '''处理推荐结果'''
    dict_rec = dict()
    with open(rec_path, 'r') as f:
        for each in f.readlines():
            tup = each.replace('\n', '').split(',')
            dict_rec[(tup[0], tup[1])] = float(tup[2])
    marks = dict()
    for key, value in dict_rec.iteritems():
        if random.random() < 0.3:
            if key in dict_test.keys():
                pass
                marks[key] = LIKE
            else:
                marks[key] = DISLIKE
    # print marks
    '''处理训练集结果'''
    shutil.copyfile(train_path, trainbk_path)
    shutil.copyfile(test_path, testbk_path)
    shutil.copyfile(rec_path, recbk_path)
    with open(train_path, 'a') as f:
        for key, value in marks.iteritems():
            f.write('{0},{1},{2}\n'.format(key[0], key[1], value))


if __name__ == '__main__':
    pass
