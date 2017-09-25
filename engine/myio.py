# coding=utf-8
import os

PYTHON_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]


def readfile():
    """
        user_item=[ {"uid":uid, "iid":iid, "ranking":ranking} ]
        repository_data=[ {"iid":iid, "lang":lang, "md":md, "sc":sc} ]
    """

    repository_data = []
    with open('../data/hrepo.csv', 'r') as hrepo_file:
        for each_line in hrepo_file:
            each_list = each_line.split('|')
            if len(each_list) == 4:
                repository_data.append({"iid": each_list[0],
                                        "lang": each_list[1],
                                        "md": each_list[2],
                                        "sc": each_list[3]})
    user_item = []
    with open('../data/ga_with_repo.csv', 'r') as ga_file:
        for each_line in ga_file:
            each_list = each_line.split('|')
            if len(each_list) == 3:
                user_item.append({"uid": each_list[0],
                                  "iid": each_list[1],
                                  "ranking": each_list[2]})

    return user_item, repository_data


def readfile2():
    """
        user_item=[ {"uid":uid, "iid":iid, "ranking":ranking} ]
        repository_data=[ {"iid":iid, "lang":lang, "md":md, "sc":sc} ]
    """

    repository_data = []
    with open('../data/hrepo2.csv', 'r') as hrepo_file:
        for each_line in hrepo_file:
            each_list = each_line.split('|')
            if len(each_list) == 3:
                repository_data.append({"iid": each_list[0].split("/")[1],
                                        "lang": each_list[0].split("/")[0],
                                        "md": each_list[1],
                                        "sc": each_list[2]})
    user_item = []
    with open('../data/ga_with_repo2.csv', 'r') as ga_file:
        for each_line in ga_file:
            each_list = each_line.split('|')
            if len(each_list) == 3:
                user_item.append({"uid": each_list[0],
                                  "iid": each_list[1],
                                  "ranking": each_list[2]})

    return user_item, repository_data


def readfile3(filename):
    """
        源文件为 id|lang|md|sc|
        user_item=[ {"uid":uid, "iid":iid, "ranking":ranking} ]
        repository_data=[ {"iid":iid, "lang":lang, "md":md, "sc":sc} ]
    """

    hrepo_path = os.path.join(PYTHON_FILE_PATH, '..', 'data', 'hrepo{}.csv'.format(filename))
    repository_data = []
    with open(hrepo_path, 'r') as hrepo_file:
        for each_line in hrepo_file:
            each_list = each_line.split('|')
            if len(each_list) == 3:
                repository_data.append({"iid": each_list[0].split("/")[1],
                                        "lang": each_list[0].split("/")[0],
                                        "md": each_list[1],
                                        "sc": each_list[2]})
    user_item = []
    with open('../data/train.data', 'r') as ga_file:
        for each_line in ga_file:
            each_list = each_line.split(',')
            if len(each_list) == 3:
                user_item.append({"uid": each_list[0],
                                  "iid": each_list[1],
                                  "ranking": each_list[2]})

    return user_item, repository_data


def readfile4(filename):
    """
        源文件为 id,lang1|lang2,md,sc
        user_item=[ {"uid":uid, "iid":iid, "ranking":ranking} ]
        repository_data=[ {"iid":iid, "lang":lang, "md":md, "sc":sc} ]
    """

    hrepo_path = os.path.join(PYTHON_FILE_PATH, '..', 'data', 'hrepo{}.csv'.format(filename))
    repository_data = []
    with open(hrepo_path, 'r') as hrepo_file:
        for each_line in hrepo_file:
            each_list = each_line.split(',')
            if len(each_list) == 4:
                repository_data.append({"iid": each_list[0],
                                        "lang": set(each_list[1].split("|")),
                                        "md": each_list[2],
                                        "sc": each_list[3]})
    user_item = []
    with open('../data/train.data', 'r') as ga_file:
        for each_line in ga_file:
            each_list = each_line.split(',')
            if len(each_list) == 3:
                user_item.append({"uid": each_list[0],
                                  "iid": each_list[1],
                                  "ranking": each_list[2]})

    return user_item, repository_data


def writefile(result):
    with open('../data/result.csv', 'w') as result_file:
        for each_result in result:
            result_file.write("{0},{1},{2}\n".format(*each_result))


if __name__ == '__main__':
    a, b = readfile()
    print b
