import sys
import operator
import math

W = {}


def LoadData():
    # train = {userId:[iterm1, item2...]} the same as test dict
    # W = {u:{v:value}} the same as C
    # item_users = {item, [user1,user2...]}
    # N(u) = {u:value} The number of items user u like
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
                train[userId] = (itemId, 1 if float(rating) > 0 else -1)
            else:
                train[userId].append((itemId, 1 if float(rating) else -1))
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


def UserSimilarityC(train):
    # build inverse table for item_users
    item_users = {}
    for u, items in train.items():
        for i in items:
            id = i[0]
            if id not in item_users.keys():
                item_users[id] = list()
            item_users[id].append((u, i[1]))
    # calculate co-rated items between users
    C = {}
    N = {}
    for item, users in item_users.items():
        for u in users:
            C.setdefault(u[0], {})
            N.setdefault(u[0], 0)
            N[u[0]] += u[1] ** 2
            for v in users:
                if u == v:
                    continue
                C[u[0]].setdefault(v[0], 0)
                C[u[0]][v[0]] += u[1] * v[1]
    # print ("C[u][v]: %s"%C)
    # calculate finial similarity matrix W

    for u, related_users in C.items():
        W.setdefault(u, {})
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])
            #  W[u][v] = 0#cuv / math.sqrt(N[u] * N[v])


def UserSimilarityS(train):
    # build inverse table for item_users
    item_users = {}
    for u, items in train.items():
        for i in items:
            if i not in item_users.keys():
                item_users[i] = list()
            item_users[i].append(u)
    # print("item_users: %s"%item_users)
    # calculate co-rated items between users
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
    # print ("C[u][v]: %s"%C)
    # calculate finial similarity matrix W

    for u, related_users in C.items():
        W.setdefault(u, {})
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])
            # print ("W: %s"%W)


def RecommendN(user, train, K, N):
    rank = {}
    rank.setdefault(user, {})
    interacted_items = train.get(user, [])
    interacted_items = map(lambda e: e[0], interacted_items)
    for v, wuv in sorted(W.get(user, dict()).items(), key=operator.itemgetter(1), reverse=True)[0:K]:
        for i in train.get(v, dict()):
            if i[0] in interacted_items:
                # we should filter items user interacted before
                continue
            rank[user].setdefault(i[0], 0)
            # TBD the rvi value represents the like degree of v to i
            rvi = i[1]
            rank[user][i[0]] += wuv * rvi
    n_rank = sorted(rank[user].items(),
                    key=operator.itemgetter(1), reverse=True)[:N]
    # print ("rank: %s"%n_rank)
    return n_rank


def Recommend(test, train, K, N):
    preds = []
    pred_user = set(test.keys())
    print len(pred_user)
    for user in pred_user:
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
