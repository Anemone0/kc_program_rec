#!/usr/bin/env python
# -*-coding=utf-8-*-

from scipy.sparse import csr_matrix


def get_csr_matrix(arr, topk, repository_data):
    """
    :param arr:
        [ [(iid,ranking),] ]
    :param sim_num:
    :return:
    """
    col = []
    row = []
    val = []

    for i in range(len(arr)):
        # 排序，为输出方便
        sort_sims = sorted(enumerate(arr[i]), key=lambda item: -item[1])
        # print sort_sims
        k = 0
        n = 0
        while n < len(sort_sims):
            each_result = sort_sims[n]
            n += 1
            if repository_data[i]["lang"] == repository_data[each_result[0]]["lang"]:
                if repository_data[each_result[0]]["md"] != "0" and repository_data[each_result[0]]["sc"] != "0":
                    k += 1
                    row.append(i)
                    col.append(each_result[0])
                    val.append(each_result[1])
            if k >= topk:
                break
    ret = csr_matrix((val, (row, col)))
    return ret


def combine(md_sim, sc_sim, repository_data, sim_num=1000, alpha=0.7, beta=0.3):
    """
    :param repository_data:
    :param md_sim:
        [ [(iid,ranking),] ]
    :param sc_sim:
    :param alpha:
    :param beta:
    :return:
    """
    md_sim_csr = get_csr_matrix(md_sim, topk=sim_num, repository_data=repository_data)
    sc_sim_csr = get_csr_matrix(sc_sim, topk=sim_num, repository_data=repository_data)
    ret = alpha * md_sim_csr + beta * sc_sim_csr
    return ret


if __name__ == '__main__':
    pass
