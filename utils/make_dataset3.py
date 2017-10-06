#!/usr/bin/env python
# -*-coding=utf-8-*-
# 只考虑用户自己创建的项目
# 考虑到数据量大的问题
import sys
import os

reload(sys)
sys.setdefaultencoding("utf-8")

PYTHON_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]
PROJECT = 'step_3'
CSV_DIR = os.path.join(PYTHON_FILE_PATH, '..', 'crawl_github', 'csv', PROJECT)

REPO_SET = []
USER_SET = []
REPO_DICT = {}
USER_HEHAVIOR = set()


def get_users_and_repos():
    global REPO_SET
    global USER_SET
    global REPO_DICT
    global USER_HEHAVIOR

    # 先挑选一定数量的repo
    repo_set_prev = set()
    with open(os.path.join(CSV_DIR, 'Repo.csv'), 'r') as repo_file:
        for each in repo_file.readlines()[1:]:
            split_line = each.rstrip().split(',')
            name = split_line[-1]
            language = split_line[-2]
            repo_set_prev.add(name)

    user_set = set()
    repo_set = set()
    with open(os.path.join(CSV_DIR, 'UserItem.csv'), 'r') as useritem_file:
        for each in useritem_file.readlines()[1:]:
            action, user_name, repo_name = each.rstrip().split(',')
            repo_name = repo_name.split('/')[-1]
            if repo_name in repo_set_prev:
                user_set.add(user_name)
                USER_HEHAVIOR.add((user_name, repo_name, action))
                if int(action) == 10:
                    repo_set.add(repo_name)
    USER_SET = list(user_set)
    REPO_SET = list(repo_set)

    with open(os.path.join(CSV_DIR, 'Repo.csv'), 'r') as repo_file:
        for each in repo_file.readlines()[1:]:
            split_line = each.rstrip().split(',')
            name = split_line[-1]
            language = split_line[-2]
            if name in repo_set:
                REPO_DICT[name] = {'name': name,
                                   'language': language,
                                   'readme': '0',
                                   'source': '0'}
    with open(os.path.join(CSV_DIR, 'RepoReadme.csv'), 'r') as repo_file:
        for each in repo_file.readlines()[1:]:
            split_line = each.rstrip().split(',')
            if len(split_line) == 2:
                readme = split_line[0]
                name = split_line[1]
                if name in repo_set:
                    REPO_DICT[name]['readme'] = readme

    with open(os.path.join(CSV_DIR, 'RepoSource.csv'), 'r') as repo_file:
        for each in repo_file.readlines()[1:]:
            split_line = each.rstrip().split(',')
            if len(split_line) == 2:
                source = split_line[0]
                name = split_line[1]
                if name in repo_set:
                    REPO_DICT[name]['source'] = source


def make_dataset():
    with open(os.path.join(CSV_DIR, 'ga_with_repo_{}.csv'.format(PROJECT)), 'w') as ga_file:
        for each in USER_HEHAVIOR:
            if each[1] in REPO_DICT.keys():
                ga_file.write('{0},{1},{2}\n'.format(
                    USER_SET.index(each[0]),
                    REPO_SET.index(each[1]),
                    each[2]
                ))

    with open(os.path.join(CSV_DIR, 'hrepo_{}.csv'.format(PROJECT)), 'w') as ga_file:
        for each in REPO_DICT.keys():
            ga_file.write('{0},{1},{2},{3}\n'.format(
                REPO_SET.index(REPO_DICT[each]['name']),
                REPO_DICT[each]['language'],
                REPO_DICT[each]['readme'],
                REPO_DICT[each]['source'],
            ))


if __name__ == '__main__':
    get_users_and_repos()
    make_dataset()
    print len(USER_SET)
    print len(REPO_SET)
    # print REPO_DICT[REPO_DICT.keys()[1]]
