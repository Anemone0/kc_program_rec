#!/usr/bin/env python
# -*-coding=utf-8-*-
def recommend(user_ranking, repository_sim, topn=5):
    predict_ranking = user_ranking * repository_sim
    matrix_results = predict_ranking - user_ranking * 987654321
    # 排序，为输出方便
    topn_results = []
    for each in matrix_results.toarray():
        sort_sims = sorted(enumerate(each), key=lambda item: -item[1])
        sort_sims = filter(lambda each: each[1] > 0, sort_sims)
        topn_results.append(sort_sims[0:topn])  # 看下前10个最相似的，第一个是基准数据自身
    return topn_results


def recommend2(user_ranking, repository_sim, topn=5):
    predict_ranking = user_ranking * repository_sim
    matrix_results = predict_ranking - user_ranking * 987654321
    # 排序，为输出方便
    topn_results = []
    for each in matrix_results.toarray():
        sort_sims = sorted(enumerate(each), key=lambda item: -item[1])
        sort_sims = filter(lambda each: each[1] > 0, sort_sims)
        topn_results.append(sort_sims[0:topn])  # 看下前10个最相似的，第一个是基准数据自身
    return topn_results
if __name__ == '__main__':
    pass
