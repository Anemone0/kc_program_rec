#!/usr/bin/env python
# -*-coding=utf-8-*-

"""原始数据"""
# 缩水版的courses，实际数据的格式应该为 课程名\t课程简介\t课程详情，并已去除html等干扰因素
courses = ['Writing II: Rhetorical Composing',
           'Genetics and Society: A Course for Educators',
           'General Game Playing',
           'Genes and the Human Condition (From Behavior to Biotechnology)',
           'A Brief History of Humankind',
           'New Models of Business in Society',
           'Analyse Numrique pour Ingnieurs',
           'Evolution: A Course for Educators',
           'Coding the Matrix: Linear Algebra through Computer Science Applications',
           'The Dynamic Earth: A Course for Educators']
# 实际的 courses_name = [course.split('\t')[0] for course in courses]
courses_name = ['Writing II: Rhetorical Composing', 'Genetics and Society: A Course for Educators',
                'General Game Playing', 'Genes and the Human Condition (From Behavior to Biotechnology)',
                'A Brief History of Humankind', 'New Models of Business in Society', 'Analyse Numrique pour Ingnieurs',
                'Evolution: A Course for Educators',
                'Coding the Matrix: Linear Algebra through Computer Science Applications',
                'The Dynamic Earth: A Course for Educators']

"""预处理(easy_install nltk)"""

# 引入nltk
import nltk
# nltk.download()    #下载要用的语料库等，时间比较长，最好提前准备好

# 分词
from nltk.corpus import brown

texts_lower = [[word for word in document.lower().split()] for document in courses]
from nltk.tokenize import word_tokenize

texts_tokenized = [[word.lower() for word in word_tokenize(document)] for document in courses]

# 去除停用词
from nltk.corpus import stopwords

english_stopwords = stopwords.words('english')
texts_filtered_stopwords = [[word for word in document if not word in english_stopwords] for document in
                            texts_tokenized]
# 去除标点符号
english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
texts_filtered = [[word for word in document if not word in english_punctuations] for document in
                  texts_filtered_stopwords]

# 词干化
from nltk.stem.lancaster import LancasterStemmer

st = LancasterStemmer()
texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]

# 去除过低频词
all_stems = sum(texts_stemmed, [])
stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]

"""
注意：本例子中只用了course_name字段，大多数word频率过低，造成去除低频词后，有些document可能为空
          因此后面的处理结果只做示范
"""

"""
引入gensim，正式开始处理(easy_install gensim)

输入：
     1.去掉了停用词
     2.去掉了标点符号
     3.处理为词干
     4.去掉了低频词

"""
from gensim import corpora, models, similarities

# 为了能看到过程日志
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in
          texts]  # doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

# 拍脑袋的：训练topic数量为10的LSI模型
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
index = similarities.MatrixSimilarity(lsi[corpus])  # index 是 gensim.similarities.docsim.MatrixSimilarity 实例

"""
对具体对象相似度匹配
"""
for i in range(len(texts)):
    # 选择一个基准数据
    ml_course = texts[i]
    ml_bow = dictionary.doc2bow(ml_course)
    # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
    ml_lsi = lsi[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
    sims = index[ml_lsi]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi
    print sims
    # 排序，为输出方便
    # sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])

    # 查看结果
    # print sort_sims[0:10]  # 看下前10个最相似的，第一个是基准数据自身
    # print courses_name[0:10]  # 看下实际最相似的数据叫什么
