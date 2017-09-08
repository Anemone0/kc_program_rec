# coding=utf8
import myio
import md_tokenizer
import logging
import md_calc_sim
import combine
import recommend

from scipy.sparse import csr_matrix


class Engine:
    choose_num = 10
    alpha = 7
    beta = 3
    similar_num = 1000

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

    def launch(self):
        """
        :type self: object
        """
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        logging.info("input func")
        user_item, repository_data = self.input_func()
        """
        md_words=[ {"iid",iid, "md_word":md_word} ]
        """
        iid2lid = dict([(each['iid'], repository_data.index(each)) for each in repository_data])

        logging.info("md tokenizer")
        md_words = self.md_tokenizer(map(lambda e: e["md"], repository_data))
        """
        sc_words=[ ["sc","word"] ]
        """
        logging.info("sc tokenizer")
        sc_words = self.sc_tokenizer(map(lambda e: e["sc"], repository_data))

        logging.info("md calculate similarity")
        md_sim = self.md_calc_sim(md_words, repository_data, self.similar_num)
        md_words=None
        logging.info("sc calculate similarity")
        sc_sim = self.sc_calc_sim(sc_words, repository_data, self.similar_num)
        md_words=None

        logging.info("add similarity")
        repository_sim = self.combine(md_sim, sc_sim, self.alpha, self.beta)
        md_sim=sc_sim=None

        """
        将用户-行为矩阵的用户, 项目id转变为数组的id
        """
        logging.info("transform id")
        user_set = set()
        for each in user_item:
            user_set.add(each["uid"])
        user_list = list(user_set)
        col = []
        row = []
        val = []
        for each in user_item:
            row.append(user_list.index(each["uid"]))
            col.append(iid2lid[each["iid"]])
            val.append(float(each["ranking"].strip()))
        user_ranking = csr_matrix((val, (row, col)),shape=(len(user_list), len(repository_data)))

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


if __name__ == '__main__':
    engine = Engine()
    engine.choose_num=5

    engine.set_input_func(myio.readfile3)
    engine.set_output_func(myio.writefile)

    engine.set_md_tokenizer(md_tokenizer.tokenizer2)
    engine.set_sc_tokenizer(md_tokenizer.tokenizer2)
    engine.set_md_calc_sim(md_calc_sim.md_calc_sim)
    engine.set_sc_calc_sim(md_calc_sim.md_calc_sim)
    engine.set_combine(combine.combine)
    engine.set_recommend(recommend.recommend)
    engine.launch()
