#!/usr/bin/env python
#coding=utf-8

# @file executezip.py
# @brief executezip
# @author x565178035,x565178035@126.com
# @version 1.0
# @date 2016-07-20 14:26

import sys
import os
import zipfile
import re
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer

reload(sys)
sys.setdefaultencoding("utf-8")

support_language=['rb','c','cpp','java','vim','js','html','css','php','cs','cr','go','m','groovy','pl','sh','mm']

PYTHON_FILE_PATH=os.path.split(os.path.realpath(__file__))[0]

codeblock=re.compile(ur'`.*`', re.S)
unuseful=re.compile(ur'[^\w]|\\_')
useful=re.compile(ur'\w[a-z0-9]{2,}')

english_stopwords = stopwords.words('english')

SC_STOPWORDS=[]
def sc_stopwords(file_name):
    global SC_STOPWORDS
    with open(file_name, 'r') as f:
        for each in f.readlines():
            SC_STOPWORDS+=each.replace('\n',' ').replace('\r',' ').split()
sc_stopwords(os.path.join(PYTHON_FILE_PATH,'sc_stopwords.txt'))

def analyse(path):
    zfile = zipfile.ZipFile(path, 'r')
    md_words=[]
    sc_words=[]
    for each_file in zfile.namelist():
        content=zfile.read(each_file)
        filename=each_file.lower()
        #分析README文档
        if 'readme' in filename or 'md' in filename and ('LICENSE' not in filename and 'license' not in filename):
            md_words+=parse_readme(content)
        #分析源代码
        elif filename.split('.')[-1] in support_language:
            sc_words+=parse_code(content)
    if len(md_words)==0:
        md_words='0'
    if len(sc_words)==0:
        sc_words='0'
    return ' '.join(md_words[:100000]),' '.join(sc_words[:100000])

def parse_readme(sentence):
    #TODO 使用更科学的自然语义分析

    sentence=codeblock.sub(' ',sentence)
    sentence=unuseful.sub(' ',sentence)
    sentence_words=useful.findall(sentence)
    sentence_words=[word.lower() for word in sentence_words if word not in english_stopwords]
    st=LancasterStemmer()
    sentence_words=[st.stem(word) for word in sentence_words]
    return sentence_words

def parse_code(code):
    #TODO 使用更科学的自然语义分析

    code=unuseful.sub(' ',code)
    code=code.replace('_',' ')
    code_words=useful.findall(code)
    code_words=map(lambda e:e.lower(),code_words)
    code_words=filter(lambda e:e not in SC_STOPWORDS,code_words)
    return code_words[:4000]

if __name__ == '__main__':
    md_words,sc_words=analyse('temp/7429.zip')
    with open('temp/md_words.txt', 'w+') as file:
        file.write(md_words)
    with open('temp/sc_words.txt', 'w+') as file:
        file.write(sc_words)

