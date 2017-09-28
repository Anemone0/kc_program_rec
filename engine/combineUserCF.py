#!/usr/bin/env python
# -*-coding=utf-8-*-

rec_dict = {}
alpha = 200
beta = 1


def combineUserCF(alpha, beta, k):
    global rec_dict
    with open('../data/usercf_rec.csv', 'r') as f:
        for each_line in f.readlines():
            user, item, rank = each_line.rstrip().split(',')
            user_dict = rec_dict.get(user, {})
            user_dict[item] = alpha * float(rank)
            rec_dict[user] = user_dict

    with open('../data/result.csv', 'r') as f:
        for each_line in f.readlines():
            user, item, rank = each_line.rstrip().split(',')
            user_dict = rec_dict.get(user, {})
            if item in user_dict.keys():
                user_dict[item] += beta * float(rank)
            else:
                user_dict[item] = beta * float(rank)
            rec_dict[user] = user_dict

    with open('../data/combine.csv', 'w') as f:
        for user, user_dict in rec_dict.iteritems():
            sorted_list = sorted(user_dict.iteritems(),
                                 key=lambda d: d[1],
                                 reverse=True)
            for item, rank in sorted_list[:k]:
                f.write('{0},{1},{2}\n'.format(user, item, rank))


if __name__ == '__main__':
    combineUserCF(alpha, beta, k=5)
