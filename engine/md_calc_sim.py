#!/usr/bin/env python
# -*-coding=utf-8-*-
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
import logging


def md_calc_sim_sklearn(texts, repository_data):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(texts)
    sim_matrix = (tfidf * tfidf.T).A
    return sim_matrix

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
    index = similarities.Similarity('tmp', transformed_corpus, num_features=len(dictionary.dfs))
    # index = similarities.MatrixSimilarity(transformed_corpus)

    # row = []
    # col = []
    # data = []
    sim_matrix = []
    for i in range(len(corpus)):
        # 选择一个基准数据
        ml_bow = corpus[i]
        # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
        # ml_lsi = lsi[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
        sims = index[ml_bow]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi
        sim_matrix.append(sims)
    return sim_matrix
