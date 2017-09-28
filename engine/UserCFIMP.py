import sys
import operator
import math

W = {}


def LoadData():
    test = {}
    train = {}
    TrainFile = '../data/train.data'
    TestFile = '../data/test.data'
    # TestFile = 'u.test'
    # load train file
    with open(TrainFile, 'r') as file_object:
        for line in file_object:
            (userId, itemId, rating) = line.strip().split(',')
            train.setdefault(userId, [])
            if userId not in train:
                train[userId] = itemId
            else:
                train[userId].append(itemId)
                # print("train: %s"%train)
    # load test file
    with open(TestFile, 'r') as test_object:
        for line in test_object:
            (userId, itemId, rating) = line.strip().split(',')
            test.setdefault(userId, [])
            if userId not in test:
                test[userId] = itemId
            else:
                test[userId].append(itemId)
                # print("test: %s"%test)
    return train, test


def UserSimilarityS(train):
    global W
    # build inverse table for item_users
    item_users = {}
    for u, items in train.items():
        for i in items:
            if i not in item_users.keys():
                item_users[i] = list()
            item_users[i].append(u)
    C = {}
    N = {}
    for item, users in item_users.items():
        for u in users:
            C.setdefault(u, {})
            N.setdefault(u, 0)
            N[u] += 1
            for v in users:
                if u == v:
                    continue
                C[u].setdefault(v, 0)
                C[u][v] += 1
    # calculate finial similarity matrix W
    for u, related_users in C.items():
        W.setdefault(u, {})
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])


def RecommendN(user, train, K, N):
    rank = {}
    rank.setdefault(user, {})
    interacted_items = train.get(user, [])
    for v, wuv in sorted(W.get(user, dict()).items(), key=operator.itemgetter(1), reverse=True)[0:K]:
        for i in train.get(v, dict()):
            if i in interacted_items:
                # we should filter items user interacted before
                continue
            rank[user].setdefault(i, 0)
            # TBD the rvi value represents the like degree of v to i
            rvi = 1
            rank[user][i] += wuv * rvi
    n_rank = sorted(rank[user].items(), key=operator.itemgetter(1), reverse=True)[:N]
    # print ("rank: %s"%n_rank)
    return n_rank


def Recommend(test, train, K, N):
    preds = []
    pred_user = set(test.keys())
    for user in pred_user:
        tui = test[user]
        n_rank = RecommendN(user, train, K, N)
        for iid, rank in n_rank:
            preds.append((user, iid, rank))
    with open('../data/usercf_rec.csv', 'w') as f:
        for each in preds:
            f.write('{0},{1},{2}\n'.format(*each))


if __name__ == '__main__':
    train, test = LoadData()
    UserSimilarityS(train)

    n = 5
    k = 80
    Recommend(train, train, k, n)
    #  recall = Recall(train, test, n)
    #  precision = Precision(train, test, n)
    #  coverage = Coverage(train, test, n)
    #  popularity = Popularity(train, test, n)
    #  print ('test recall: ', recall)
    #  print ('test precision: ', precision)
    #  print ('test coverage: ', coverage)
    #  print ('test popularity: ', popularity)
    #  raw_input()
