#!/usr/bin/env python
# -*-coding=utf-8-*-
from nltk import LancasterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

def tokenizer(courses):
    texts_lower = [[word for word in document.lower().split()] for document in courses]

    texts_tokenized = [[word.lower() for word in word_tokenize(document)] for document in courses]

    # 去除停用词
    logging.info(u"去除停用词")
    english_stopwords = stopwords.words('english')
    texts_filtered_stopwords = [[word for word in document if not word in english_stopwords] for document in
                                texts_tokenized]
    # 去除标点符号
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
    texts_filtered = [[word for word in document if not word in english_punctuations] for document in
                      texts_filtered_stopwords]

    # 词干化
    st = LancasterStemmer()
    texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]

    # 去除过低频词
    all_stems = sum(texts_stemmed, [])
    stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
    texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]
    return texts

def tokenizer2(courses):
    texts_lower=[]
    for document in courses:
        words=[]
        for word in document.split():
            if word!='0':
                words.append(word)
        texts_lower.append(words)
    return texts_lower
