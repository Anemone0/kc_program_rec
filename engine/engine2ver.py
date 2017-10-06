#!/usr/bin/env python
# coding=utf-8

# @file engine.py
# @brief engine
# @author x565178035,x565178035@126.com
# @version 2.0
# @date 2016-07-13

#  from pyspark import SparkContext,SparkConf
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import *
from pyspark.ml.feature import HashingTF, IDF, Tokenizer

import itertools
from math import sqrt
import json
import random

# import sys
# sys.path.append("/mnt/hgfs/all_my_work/KC_program_rec/src/rec_engine_exper")

import numpy as np
import time
import pdb


def nearest_neighbors(user, users_and_sims, n):
    '''
    Sort the predictions list by similarity and select the top-N neighbors
    '''
    users_and_sims = list(users_and_sims)
    users_and_sims.sort(key=lambda x: x[1], reverse=True)
    for each in users_and_sims[:n]:
        if each[0] is None:
            users_and_sims.remove(each)
    return user, list(users_and_sims[:n])


def nearest_neighbors2(user, users_and_sims, n):
    '''
    Sort the predictions list by similarity and select the top-N neighbors
    '''
    users_and_sims = list(users_and_sims)
    users_and_sims.sort(key=lambda x: x[1], reverse=True)
    users_and_sims2 = []
    for each in users_and_sims[:n]:
        if each[0] is not None:
            users_and_sims2.append((user, (each[0], each[1])))

    return users_and_sims2


def inverse(vector):
    """
    矩阵逆置
    用法:
        attr_user=user_attr.flatMap(inverse).groupByKey()
    """
    return [(each[0], (vector[0], each[1])) for each in vector[1]]


def cell_product(left, right):
    """
    左边列与右边行的外积
    """
    list = []
    for key1, val1 in left:
        for key2, val2 in right:
            list.append(((key1, key2), val1 * val2))
    return list


def half_product(in_left_g, right_g):
    """
    矩阵乘法的组成部分,不带转化操作
    [B,A]*[B,C]=>
        (A,C),val
    """
    res = in_left_g.join(right_g) \
        .flatMap(lambda e: cell_product(e[1][0], e[1][1])) \
        .reduceByKey(lambda x, y: x + y)
    return res


def product(left_g, right_g):
    """
    两个稀疏矩阵乘法,左右都为rdd矩阵
    A-B*B-C
    """
    in_left_g = left_g.flatMap(inverse).groupByKey()
    res = half_product(in_left_g, right_g)
    #  .map(pair2first)
    #  .groupByKey()
    return res


def product2(left, right):
    """
    两个稀疏矩阵乘法,左右都为rdd矩阵
    A-B*B-C
    """
    inver_left = left.map(lambda e: (e[1][0], (e[0], e[1][1])))
    res = inver_left.join(right) \
        .map(lambda e: ((e[1][0][0], e[1][1][0]), e[1][0][1] * e[1][1][1])) \
        .reduceByKey(lambda x, y: x + y)
    return res


def fast_produt_lambda(user_item_g, broadcast_dict):
    """
    矩阵相乘 以user_item为大矩阵,每行为一个处理单位,分布式计算
    user_item_g = user, ( (item1,1),(item2,1), ... )

    return { (( user,item ),val) }
    """
    user_attr_dict = {}
    for item, itval in user_item_g[1]:
        if item in broadcast_dict.value:
            for attr, attrval in broadcast_dict.value[item]:
                if attr not in user_attr_dict.keys():
                    user_attr_dict[attr] = itval * attrval
                else:
                    user_attr_dict[attr] += itval * attrval
    user_attr_pair = [((user_item_g[0], attr), user_attr_dict[attr])
                      for attr in user_attr_dict.keys()]
    return user_attr_pair


def fast_product(left_g, right_g, sc):
    """
    用广播变量实现大小矩阵相乘,左边矩阵为rdd大矩阵,右边矩阵为rdd小矩阵
    sc=SparkContext
    """
    right_g_b = sc.broadcast(right_g.collectAsMap())
    return left_g.flatMap(lambda e: fast_produt_lambda(e, right_g_b))


class RecEngine(object):
    def __init__(self, app_name="RecEngine", master=None):
        self.similar_num = int(1e4)
        self.choose_num = 5
        self.output_func = RecEngine.output
        self.para = 64
        if master:
            self.sc = SparkContext(
                conf=SparkConf().setAppName(app_name).setMaster(master).set(
                    'spark.driver.cores', 4))
        else:
            self.sc = SparkContext(
                conf=SparkConf().setAppName(app_name).set(
                    'spark.default.parallelism', str(
                        self.para)).set(
                    'spark.driver.cores', 4).set(
                    'spark.sql.shuffle.partitions', 40))

    @classmethod
    def output(cls, user_rec):
        print "WARNING:Default output func."
        for e_user_rec in user_rec.collect():
            print e_user_rec

    def set_input_func(self, func):
        """
        return user,(item,val)
        """
        self.input_func = func

    def set_output_func(self, func):
        self.output_func = func

    def set_similar_num(self, similar_num):
        self.similar_num = similar_num

    def set_choose_num(self, choose_num):
        self.choose_num = choose_num

    def launch(self):
        raise NotImplementedError


def read_words(line):
    tuple = line.split("|")
    lan, item = tuple[0].split("/")
    if len(tuple) > 2:
        md_sentence = tuple[1]
        sc_sentence = tuple[2]
    else:
        return Row(item='0', readme='0', source='0')
    return Row(item=item, lang=lan, readme=md_sentence, source=sc_sentence)


def format_item_feature(row):
    return (row.lang, row.item, row.md_features, row.sc_features)


def filter_matrix(pair):
    """
    将对称矩阵的下三角去掉,使接下来计算量减半
    pair=((user1,vector),(user2,vector))
    """
    return pair[0] < pair[1]


def calc_sim_df(row, idx=1):
    v11 = row.md1
    v12 = row.sc1
    v21 = row.md2
    v22 = row.sc2
    res = sqrt(v11.dot(v11)) * sqrt(v21.dot(v21))
    if res == 0:
        sim1 = 0
    else:
        sim1 = v11.dot(v21) / res

    res = sqrt(v12.dot(v12)) * sqrt(v22.dot(v22))
    if res == 0:
        sim2 = 0
    else:
        sim2 = v12.dot(v22) / res
    return ((row.item1, row.item2), (sim1, sim2))


def df2pair(row):
    return (row.item1, row.md1, row.sc1), (row.item2, row.md2, row.sc2)


def calc_sim(pair, idx=1):
    """
    以向量的方式计算两物品的相似度
    pair=< <user1,v1,v1>,<user2,v2,v2> >
        => < <user1,user2>,sim >
        => < <user1,user2>,sim >
           < <user2,user1>,sim >
    """

    v11 = pair[0][1]
    v12 = pair[0][2]
    v21 = pair[1][1]
    v22 = pair[1][2]
    res = sqrt(v11.dot(v11)) * sqrt(v21.dot(v21))
    if res == 0:
        sim1 = 0
    else:
        sim1 = v11.dot(v21) / res

    res = sqrt(v12.dot(v12)) * sqrt(v22.dot(v22))
    if res == 0:
        sim2 = 0
    else:
        sim2 = v12.dot(v22) / res
        #  if sim<=1e-6:
        #  return ()
    #  else:
    return ((pair[0][0], pair[1][0]), (sim1, sim2))


def sc_plus_md(pair, alpha, beta):
    sum = pair[1][0] * alpha + pair[1][1] * beta
    return (pair[0][0], (pair[0][1], sum)), (pair[0][1], (pair[0][0], sum))


def parse_line(line):
    """< user, <item,val>>"""
    list = line.split("|")
    return (int(list[0]), (int(list[1]), float(list[2])))


def unfold(row):
    return [((row[0], each[0]), each[1]) for each in row[1]]


def deadwhile(line):
    while 10000:
        pass
    return line


def duplicate(key_value, num):
    ret = [(key_value[0] + str(each), key_value[1:]) for each in range(num)]
    return ret


class ProEngine(RecEngine):
    """

    engine=ProEngine()
    engine.set_input_func(input)
    engine.set_output_func(output)
    engine.launch()

    input_func提供一个user_item的RDD,和一个包含sentence列的DataFrame
    """

    def load_settings(self):
        with open('engine.json', 'r') as config:
            conf = json.loads(config.readline())

        self.choose_num = conf["choose_num"]
        self.similar_num = conf["similar_num"]
        self.alpha = conf["alpha"]
        self.beta = conf["beta"]
        self.md_features = conf["md_feature"]
        self.sc_features = conf["sc_feature"]

    def save_settings(self):
        settings = dict(
            choose_num=self.choose_num,
            similar_num=self.similar_num,
        )
        file = open("pro_engine.conf", "w")
        file.write(json.dumps(settings))
        file.close()

    def launch(self):
        """
        input_func提供一个user_item的RDD,和一个包含sentence的DataFrame
        """

        spark = SparkSession \
            .builder \
            .getOrCreate()
        self.user_item, self.sentence_data = self.input_func(self.sc, spark)
        t1 = time.time()
        self.user_item.repartition(64)
        self.sentence_data.repartition(64)
        self.user_item.cache()
        """
        切词
        words_data中的words保存单词
        """
        md_tokenizer = Tokenizer(inputCol="readme", outputCol="md_words")
        md_words_data = md_tokenizer.transform(
            self.sentence_data)  # 将句子的DataFrame导入

        """
        计算每一条的TF值
        featurized_data 中 rawFeatures 一列保存结果
        """
        md_hashingTF = HashingTF(
            inputCol="md_words",
            outputCol="md_raw_features",
            numFeatures=self.md_features)
        md_featurized_data = md_hashingTF.transform(md_words_data)

        """
        计算每一条的tf-idf值
        featurized_data 中 rawFeatures 一列保存结果
        """
        md_idf = IDF(inputCol="md_raw_features", outputCol="md_features")
        md_idf_model = md_idf.fit(md_featurized_data)
        md_item_feature = md_idf_model.transform(md_featurized_data)

        """
        计算源代码的TF-IDF
        """
        sc_tokenizer = Tokenizer(inputCol="source", outputCol="sc_words")
        sc_words_data = sc_tokenizer.transform(
            md_item_feature)  # 将句子的DataFrame导入

        sc_hashingTF = HashingTF(
            inputCol="sc_words",
            outputCol="sc_raw_features",
            numFeatures=self.sc_features)
        sc_featurized_data = sc_hashingTF.transform(sc_words_data)

        sc_idf = IDF(inputCol="sc_raw_features", outputCol="sc_features")
        sc_idf_model = sc_idf.fit(sc_featurized_data)
        sc_item_feature = sc_idf_model.transform(sc_featurized_data)

        """
        计算物品与物品之间的相似度
        """
        '''join'''
        item_feature = sc_item_feature.rdd.map(format_item_feature).cache()

        item_feature_left = item_feature.map(
            lambda e: (e[0] + str(random.randint(0, 19)), e[1:]))
        item_feature_right = item_feature.flatMap(lambda e: duplicate(e, 20))

        item_pair = item_feature_right.join(item_feature_left) \
            .filter(lambda e: filter_matrix(e[1]))

        num = self.similar_num
        alpha = self.alpha
        beta = self.beta
        item_sims = item_pair.map(lambda e: calc_sim(e[1])) \
            .flatMap(lambda e: sc_plus_md(e, alpha, beta)) \
            .groupByKey(self.para) \
            .flatMap(lambda e: nearest_neighbors2(e[0], e[1], num)) \
            .cache()

        """
        用户-物品矩阵相乘,得到用户物品推荐矩阵
        < user,<item,val> >
            => < user,{ <item,val> } >  * <item,{<item,val>}>
            => < <user,item>,val >
        """

        pair_itemcf_res = product2(self.user_item, item_sims)

        """
        读取user-item数据
        rating_user_item=< user,item,val >
        """
        pair_user_item = self.user_item.map(
            lambda e: ((e[0], e[1][0]), e[1][1]))
        self.pair_res = pair_itemcf_res.subtractByKey(
            pair_user_item)  # .cache()
        num = self.choose_num
        self.user_rec = self.pair_res.map(
            lambda e: (
                e[0][0], (e[0][1], e[1]))).groupByKey(
            self.para).map(
            lambda e: nearest_neighbors(
                e[0], e[1], num))

        self.output_func(self.user_rec, self.sc)
        t2 = time.time()
        print t2 - t1
        self.sc.stop()
        return


"""Example"""


def input(sc, spark):
    item_words = sc.textFile("file:///data/hrepo.csv")
    # .filter(lambda e:( e.item!=-1 and e.item >7000 and e.item!=None ))
    item_words = item_words.map(read_words)
    sentence_data = spark.createDataFrame(item_words)
    user_item = sc.textFile("file:///data/ga_with_repo.csv")
    # .filter( lambda e: ( e[0]+e[1][0] )%10<=5 )
    user_item = user_item.map(parse_line)
    return user_item, sentence_data


def output(rdd, sc):
    li = rdd.count()


def input_test(sc, spark):
    item_words = sc.textFile("test/hrepo.csv")
    # .filter(lambda e:( e.item!=-1 and e.item >7000 and e.item!=None ))
    item_words = item_words.map(read_words)
    sentence_data = spark.createDataFrame(item_words)
    user_item = sc.textFile("test/ga_with_repo.csv")
    user_item = user_item.map(parse_line).filter(
        lambda e: (e[0] + e[1][0]) % 10 <= 5)
    return user_item, sentence_data


def output_test(rec, sc):
    user_item = sc.textFile("test/ga_with_repo.csv")
    user_item_true = user_item.map(parse_line).filter(
        lambda e: (
                      e[0] + e[1][0]) %
                  10 > 5).map(
        lambda e: (
            (e[0], e[1][0]), e[1][1]))

    user_rec = rec.flatMap(unfold)
    intersect = user_item_true.join(user_rec).map(lambda e: e[0]).distinct()

    items_rec = user_rec.map(lambda e: e[0]).distinct().count()
    items_true = user_item_true.map(lambda e: e[0]).distinct().count()
    in_num = intersect.count()
    true_num = user_item_true.count()
    rec_num = user_rec.count()
    #  print in_num,true_num
    recall = float(in_num) / float(true_num)
    pre = float(in_num) / float(rec_num)
    f1 = (2 * recall * pre) / (recall + pre)
    print "Recall:{}".format(recall)
    print "Precision:{}".format(pre)
    print "F1:{}".format(f1)
    print "Coverage:{}".format(float(items_rec) / float(items_true))


score_to_score = {'10': 10.0, '6': 6.0, '5': 6.0, '3': 1.0, '1': 1, '-1': -1, '-3': -3}


#  score_to_score = {'10': 10.0, '5': 5.0, '3': 3.0}


def parse_line2(line):
    """< user, <item,val>>"""
    li = line.split(",")
    return (li[0], (li[1], score_to_score[li[2]]))


def inputu(sc, spark):
    item_words = sc.textFile("rec_alg/hrepo.csv")
    item_words = item_words.map(read_words)  # .filter(lambda e: e.readme != '0' and e.source != '0')
    sentence_data = spark.createDataFrame(item_words)
    user_item = sc.textFile("rec_alg/train.data")
    # .filter( lambda e: ( e[0]+e[1][0] )%10<=5 )
    user_item = user_item.map(parse_line2)
    return user_item, sentence_data


def outputu(rdd, sc):
    user_rec = rdd.flatMap(unfold)
    cnt = 0
    with open('./rec_alg/rec.csv', 'w') as fle:
        for each in user_rec.collect():
            cnt += 1
            if cnt % 100 == 0:
                print 'writing'
            fle.write('{0},{1},{2}\n'.format(each[0][0], each[0][1], each[1]))


def read_words_idea(line):
    tuple = line.split(",")
    if len(tuple) > 2:
        item = tuple[0]
        lan = tuple[1].split('|')[0]
        md_sentence = tuple[2]
        sc_sentence = tuple[3]
    else:
        return Row(item='0', lang='0', readme='0', source='0')
    return Row(item=item, lang=lan, readme=md_sentence, source=sc_sentence)


def input_idea(sc, spark):
    item_words = sc.textFile("./data/hrepo.csv")
    item_words = item_words.map(read_words_idea)  # .filter(lambda e: e.readme != '0' and e.source != '0')
    sentence_data = spark.createDataFrame(item_words)
    user_item = sc.textFile("./data/train.data")
    # .filter( lambda e: ( e[0]+e[1][0] )%10<=5 )
    user_item = user_item.map(parse_line2)
    return user_item, sentence_data


def output_idea(rdd, sc):
    user_rec = rdd.flatMap(unfold)
    cnt = 0
    with open('./data/rec.csv', 'w') as fle:
        for each in user_rec.collect():
            cnt += 1
            if cnt % 100 == 0:
                print 'writing'
            fle.write('{0},{1},{2}\n'.format(each[0][0], each[0][1], each[1]))


if __name__ == '__main__':
    engine = ProEngine()
    engine.set_input_func(input_idea)
    engine.set_output_func(outputu)
    engine.load_settings()
    engine.launch()
