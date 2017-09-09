#!/usr/bin/env python
# -*-coding=utf-8-*-
from gensim import corpora, models, similarities
from scipy.sparse import csr_matrix
import logging


def md_calc_sim(texts, repository_data, topk=10000):
    """
    :param md_words:
        md_words=[ {"iid",iid, "md_word":md_word} ]
    :return:
        sim=[(iid,iid,sim)]
    """
    dictionary = corpora.Dictionary(texts)
    # doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
    corpus = [dictionary.doc2bow(text) for text in texts]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    # # 拍脑袋的：训练topic数量为10的LSI模型
    # lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
    # transformed_corpus = lsi[corpus]

    transformed_corpus = corpus_tfidf
    # index 是 gensim.similarities.docsim.MatrixSimilarity 实例
    # print len(dictionary)
    index = similarities.Similarity('tmp', transformed_corpus, num_features=len(dictionary))

    row = []
    col = []
    data = []
    for i in range(len(corpus)):
        # 选择一个基准数据
        ml_bow = corpus[i]
        # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
        # ml_lsi = lsi[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
        sims = index[ml_bow]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi

        # 排序，为输出方便
        sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])

        # 查看结果
        # 看下前10个最相似的，第一个是基准数据自身
        k = 0
        n = 0
        while n < len(sort_sims):
            each_result = sort_sims[n]
            n += 1
            if repository_data[i]["lang"] == repository_data[each_result[0]]["lang"]:
                if repository_data[i]["md"] != "0" and repository_data[i]["sc"] != 0:
                    k += 1
                    row.append(i)
                    col.append(each_result[0])
                    data.append(each_result[1])
            if k >= topk:
                break
    sim_matrix = csr_matrix((data, (row, col)))
    return sim_matrix
