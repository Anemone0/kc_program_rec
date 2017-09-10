# coding=utf8
import os

import time

import myio
import md_tokenizer
import logging
import md_calc_sim
import combine
import recommend
import pickle

from scipy.sparse import csr_matrix

PYTHON_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]


def cache(file_path):
    def handle_func(func):
        def handle_args(*args, **kwargs):
            if os.path.exists(file_path):
                with open(file_path, 'r') as pickle_file:
                    cache_data = pickle.load(pickle_file)
            else:
                cache_data = func(*args, **kwargs)
                with open(file_path, 'w') as pickle_file:
                    pickle.dump(cache_data, pickle_file)
            return cache_data

        return handle_args

    return handle_func


class Engine:
    project_name = '_Mid'

    def __init__(self):
        self.choose_num = 10
        self.alpha = 7
        self.beta = 3
        self.similar_num = 1000

    @staticmethod
    def set_project_name(name):
        Engine.project_name = name

    # 每种行为的权值
    ranking_map = {"10": 10.0, "6": 6.0, "5": 5.0, "3": 3.0, "1": 1.0}

    @cache(os.path.join(PYTHON_FILE_PATH, 'tmp', 'user_list{}.pkl'.format(project_name)))
    def get_user_list(self, user_item):
        user_set = set()
        for each in user_item:
            user_set.add(each["uid"])
        user_list = list(user_set)
        return user_list

    @cache(os.path.join(PYTHON_FILE_PATH, 'tmp', 'user_ranking{}.pkl'.format(project_name)))
    def get_user_ranking(self, user_item, user_list, iid2lid, n):
        logging.info("transform id")
        col = []
        row = []
        val = []
        for each in user_item:
            row.append(user_list.index(each["uid"]))
            col.append(iid2lid[each["iid"]])
            val.append(self.ranking_map[each["ranking"].strip()])
        user_ranking = csr_matrix((val, (row, col)), shape=(len(user_list), n))
        return user_ranking

    @cache(os.path.join(PYTHON_FILE_PATH, 'tmp', 'iid2lid{}.pkl'.format(project_name)))
    def get_iid2lid(self, repository_data):
        iid2lid = dict([(each['iid'], repository_data.index(each)) for each in repository_data])
        return iid2lid

    @cache(os.path.join(PYTHON_FILE_PATH, 'tmp', 'sc_similarity{}.pkl'.format(project_name)))
    def get_sc_similarity(self, repository_data):
        logging.info("sc tokenizer")
        sc_words = self.sc_tokenizer(map(lambda e: e["sc"], repository_data))
        logging.info("sc calculate similarity")
        sc_sim = self.sc_calc_sim(sc_words, repository_data)
        return sc_sim

    @cache(os.path.join(PYTHON_FILE_PATH, 'tmp', 'md_similarity{}.pkl'.format(project_name)))
    def get_md_similarity(self, repository_data):
        logging.info("md tokenizer")
        md_words = self.md_tokenizer(map(lambda e: e["md"], repository_data))
        logging.info("md calculate similarity")
        md_sim = self.md_calc_sim(md_words, repository_data)
        return md_sim

    def launch(self):
        """
        :type self: object
        """
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        logging.info("input func")
        user_item, repository_data = self.input_func(self.project_name)
        iid2lid = self.get_iid2lid(repository_data)

        md_sim = self.get_md_similarity(repository_data)

        sc_sim = self.get_sc_similarity(repository_data)

        logging.info("add similarity")
        repository_sim = self.combine(md_sim, sc_sim, repository_data, alpha=self.alpha, beta=self.beta, sim_num=self.similar_num)
        md_sim = sc_sim = None

        """
        将用户-行为矩阵的用户, 项目id转变为数组的id
        """
        user_list = self.get_user_list(user_item)
        user_ranking = self.get_user_ranking(user_item, user_list, iid2lid, len(repository_data))

        logging.info("Top N recommendation")
        results = self.recommend(user_ranking, repository_sim, self.choose_num)

        # :return:results=[ [ (lid,ranking) ] ]
        triple = []
        for i in range(len(results)):
            for each_recommends in results[i]:
                triple.append((user_list[i],
                               repository_data[each_recommends[0]]["iid"],
                               each_recommends[1]))
        logging.info("Output func")
        self.output_func(triple)

    def clear_cache(self):
        cache_dir = os.path.join(PYTHON_FILE_PATH, 'tmp')
        for root, dirs, files in os.walk(cache_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

    def set_input_func(self, func):
        """
        output:
        user_item=[ {"uid":uid, "iid":iid, "ranking":ranking} ]
        repository_data=[ {"iid":iid, "lang":lang, "md":md, "sc":sc} ]
        """
        self.input_func = func

    def set_output_func(self, func):
        """
        :param results=[ [ (lid,ranking) ] ]
        :return: results=[ [ (lid,ranking) ] ]
        """
        self.output_func = func

    def set_md_tokenizer(self, md_tokenizer):
        """
        :param ["md sentence",]
        :return: ["md", "sentence",]
        """
        self.md_tokenizer = md_tokenizer

    def set_sc_tokenizer(self, sc_tokenizer):
        self.sc_tokenizer = sc_tokenizer

    def set_md_calc_sim(self, md_calc_sim):
        self.md_calc_sim = md_calc_sim

    def set_sc_calc_sim(self, sc_calc_sim):
        self.sc_calc_sim = sc_calc_sim

    def set_combine(self, combine):
        self.combine = combine

    def set_recommend(self, recommend):
        """
        :param user_item user_item matrix
        :param repository_sim repository_sim matrix
        :return:results=[ [ (lid,ranking) ] ]
        """
        self.recommend = recommend


if __name__ == '__main__':
    t1 = time.time()
    engine = Engine()
    engine.choose_num = 5

    engine.set_input_func(myio.readfile3)
    engine.set_output_func(myio.writefile)

    engine.set_md_tokenizer(md_tokenizer.tokenizer_sklearn)
    engine.set_sc_tokenizer(md_tokenizer.tokenizer_sklearn)
    engine.set_md_calc_sim(md_calc_sim.md_calc_sim_sklearn)
    engine.set_sc_calc_sim(md_calc_sim.md_calc_sim_sklearn)
    engine.set_combine(combine.combine)
    engine.set_recommend(recommend.recommend)
    engine.clear_cache()
    engine.launch()
    t2 = time.time()
    print t2 - t1
