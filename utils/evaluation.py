#!/usr/bin/env python
# coding=utf-8

# @file evaluation.py
# @brief evaluation
# @author x565178035,x565178035@126.com
# @version 1.0
# @date 2017-01-06 18:40
import logging
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
user1 = set()
item1 = set()
user2 = set()
item2 = set()
user_inc = set()
act1 = set()
act2 = set()


def get_details(train, test):
    global user1
    global item1
    global user2
    global item2
    global user_inc
    global act1
    global act2
    with open(train, 'r') as f:
        for each in f.readlines():
            e = each.split(',')
            user1.add(e[0])
            item1.add(e[1])
            act1.add((e[0], e[1]))
    logging.info('Train User:{}'.format(len(user1)))
    logging.info('Train Item:{}'.format(len(item1)))
    with open(test, 'r') as f:
        for each in f.readlines():
            e = each.split(',')
            user2.add(e[0])
            item2.add(e[1])
            act2.add((e[0], e[1]))
    user_inc = user1 & user2
    logging.info('Test User:{}'.format(len(user2)))
    logging.info('Test Item:{}'.format(len(item2)))

    logging.info('User:{}'.format(len(user1 | user2)))
    logging.info('Item:{}'.format(len(item1 | item2)))


MARK_TO_RANK = {'10': 1, '6': 2, '5': 2, '3': 2, '2': 2, '1': 3}


def crontroller(test_file, rec_file, func_list):
    test = {}
    with open(test_file, 'r') as f:
        for each in f.readlines():
            uid, iid, mark = each.replace('\r', '').replace('\n', '').split(',')
            uids = test.get(uid, {})
            uids[iid] = MARK_TO_RANK[mark]
            test[uid] = uids
    rec = {}
    with open(rec_file, 'r') as f:
        for each in f.readlines():
            uid, iid, mark = each.replace('\r', '').replace('\n', '').split(',')
            uids = rec.get(uid, [])
            uids.append((iid, float(mark)))
            rec[uid] = uids

    res = []
    for each_func in func_list:
        res += each_func(test, rec)
    return res


def accuracy(test, rec):
    hit = 0.0
    n = 0.0
    for each_u in test.keys():
        if each_u in user_inc:
            n += 1
            for each in map(lambda e: e[0], rec.get(each_u, [])):
                if each in test[each_u].keys():
                    hit += 1
                    break
    logging.info('Accuray:{}'.format(hit / n))
    return hit / n,


def user_cov(test, rec):
    user_num = 0
    hit = 0.0
    n = 0.0
    for each_u in test.keys():
        if each_u in user_inc:
            if each_u in rec.keys():
                user_num += 1
                for each in map(lambda e: e[0], rec[each_u]):
                    if each in test[each_u].keys():
                        hit += 1
                        break
    logging.info('User cov: {},{}'.format(hit, user_num))
    return hit, user_num


def precision_recall(test, rec):
    hit = 0.0
    test_num = 0.0
    rec_num = 0.0
    for each_u in test.keys():
        if each_u in user_inc:
            test_num += len(test[each_u])
            for each in map(lambda e: e[0], rec.get(each_u, [])):
                rec_num += 1
                if each in test[each_u].keys():
                    hit += 1
    p = hit / (rec_num - 1e-10)
    r = hit / (test_num - 1e-10)
    f = 2 * p * r / (p + r - 1e-10)

    logging.info('Precision:{}'.format(p))
    logging.info('Recall:{}'.format(r))
    logging.info('F-mean:{}'.format(f))
    return p, r, f


def diversity(test, rec):
    sum = 0
    n = 0
    rec_sets = {}
    for each in rec.keys():
        rec_sets[each] = set(map(lambda e: e[0], rec[each]))
    for uid1 in rec.keys():
        for uid2 in rec.keys():
            if uid1 < uid2:
                inc = float(len(rec_sets[uid1] & rec_sets[uid2]))
                sum += (1 - inc / max(len(rec_sets[uid1]), len(rec_sets[uid2])))
                n += 1
    logging.info('Diversity:{}'.format(sum / n))
    return sum / n,


def mAP_mRR(test, rec):
    sAP = 0.0
    sRR = 0.0
    n_user = 0.0
    for each_u in user_inc:
        n_user += 1
        if each_u in rec.keys():
            sorted_i = sorted(rec[each_u], key=lambda e: -e[1])
            find = False
            ap = 0.0
            son = 1
            for i in range(len(sorted_i)):
                s = test[each_u].get(sorted_i[i][0], 0)
                if s != 0:
                    ap += son / float(i + 1)
                    son += 1
                    if not find:
                        find = True
                        sRR += 1 / float(i + 1)
            sAP += ap / len(test[each_u])
    mAP = sAP / n_user
    mRR = sRR / n_user
    logging.info('mAP:{}'.format(mAP))
    logging.info('mRR:{}'.format(mRR))
    return mAP, mRR


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    get_details('../data/train.data', '../data/test.data')
    res = crontroller('../data/test.data', '../data/result.csv', [accuracy, precision_recall, diversity, mAP_mRR])
    # for each in res:
    #     print each
    # print
    res = crontroller('../data/test.data', '../data/usercf_rec.csv', [accuracy, precision_recall, diversity, mAP_mRR])
    # for each in res:
    #     print each
    # print
    res = crontroller('../data/test.data', '../data/combine.csv', [accuracy, precision_recall, diversity, mAP_mRR])
    res = crontroller('../data/test.data', '../data/rec.csv', [accuracy, precision_recall, diversity, mAP_mRR])
    # for each in res:
    #     print each
    # print
    #  p_r_f('./usercf_rec.csv','./test.data')
    #  p_r_f('./itemcf_rec.csv','./test.data')
    #  p_r_f('./rec.csv','./test.data')
    #  p_r_f('./svd_rec.csv','./test.data')
    #  p_r_f2('./res.csv','./test.data')
    #  p_r_f('./1.csv','./2.csv')
    #  raw_input()
