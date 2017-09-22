#!/usr/bin/env python
# -*-coding=utf-8-*-
import sys
import os

reload(sys)
sys.setdefaultencoding("utf-8")

PYTHON_FILE_PATH = os.path.split(os.path.realpath(__file__))[0]
PROJECT = 'step_1'
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
    repo_set = set()
    with open(os.path.join(CSV_DIR, 'Repo.csv'), 'r') as repo_file:
        for each in repo_file.readlines()[1:]:
            split_line = each.rstrip().split(',')
            name = split_line[-1]
            language = split_line[-2]
            repo_set.add(name)
            REPO_DICT[name] = {'name': name,
                               'language': language,
                               'readme': '0',
                               'sourcecode': '0'}
    with open(os.path.join(CSV_DIR, 'RepoReadme.csv'), 'r') as repo_file:
        for each in repo_file.readlines()[1:]:
            split_line = each.rstrip().split(',')
            readme = split_line[0]
            name = split_line[1]
            REPO_DICT[name]['readme'] = readme

    with open(os.path.join(CSV_DIR, 'RepoSource.csv'), 'r') as repo_file:
        for each in repo_file.readlines()[1:]:
            split_line = each.rstrip().split(',')
            source = split_line[0]
            name = split_line[1]
            REPO_DICT[name]['source'] = source
    REPO_SET = list(repo_set)

    user_set = set()
    with open(os.path.join(CSV_DIR, 'UserItem.csv'), 'r') as useritem_file:
        for each in useritem_file.readlines()[1:]:
            action, user_name, repo_name = each.rstrip().split(',')
            user_set.add(user_name)
            USER_HEHAVIOR.add((user_name, repo_name.split('/')[-1], action))
    USER_SET = list(user_set)


def make_dataset():
    print REPO_SET
    with open(os.path.join(CSV_DIR, 'ga_with_repo_{}.csv'.format(PROJECT)), 'w') as ga_file:
        for each in USER_HEHAVIOR:
            ga_file.write('{0},{1},{2}\n'.format(
                USER_SET.index(each[0]),
                REPO_SET.index(each[1]),
                each[2]
            ))
    with open(os.path.join(CSV_DIR, 'hrepo_{}.csv'.format(PROJECT)), 'w') as ga_file:
        for each in REPO_DICT.keys():
            ga_file.write('{0},{1},{2},{3}\n'.format(
                REPO_DICT[each]['name'],
                REPO_DICT[each]['language'],
                REPO_DICT[each]['readme'],
                REPO_DICT[each]['sourcecode'],
            ))


if __name__ == '__main__':
    get_users_and_repos()
    make_dataset()
    print USER_SET
    # print REPO_DICT[REPO_DICT.keys()[1]]
