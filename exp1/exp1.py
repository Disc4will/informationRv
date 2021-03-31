import copy
import json
import os

import numpy as np
import pandas as pd
import pkuseg
from runME import vaildcheck
from utilities import *
from collections import Counter


def cosim(a, b):
    """

    :param a: numpy array
    :param b: same
    :return: cosine simularity
    """
    f = lambda x: np.sum(np.square(x))
    return np.dot(a, b.T) / np.sqrt(f(a) * f(b))


def filiter(content):  # 停用词过滤
    global stopwords
    contentRefined = []
    for i in content:
        if i not in stopwords:
            contentRefined.append(i)
    return contentRefined


def vectorlize(vec):  # 向量化
    global bag
    vesc = []
    for j in bag:
        if j in vec:
            vesc.append(1)
        else:
            vesc.append(0)
    return vesc


# TODO:多线程实现
'''class readthread(threading.Thread):  
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        readcontent(path)'''

path = r"datawarehouse"


def getcontent():  # 获取文件内容，同时产生文件地址名称对应关系
    global filedict, vector, stopwords, wordset, searchspace, bag
    dicts = list(filedict.keys())  # 文件排序位置
    for i in range(len(dicts)):
        upper = str(dicts[i])
        for j in filedict.get(dicts[i], 'error'):
            with open(os.path.join(upper, j), encoding='utf-8') as f:
                content = f.read()
            seg = pkuseg.pkuseg()
            content = seg.cut(content)
            '''contentRefined = []
            for i in content:
                if i not in stopwords:
                    contentRefined.append(i)
            content = contentRefined  # 去除停用词'''
            content = filiter(content)
            corpose = pd.DataFrame(content, columns=['words'])
            corpose['cnt'] = 1
            g = corpose.groupby(['words']).agg({'cnt': 'count'}).sort_values('cnt', ascending=False)
            g.reset_index()
            g = pd.DataFrame(g)  # 统计词频
            if isinstance(vector, list):
                vector = copy.deepcopy(g)
            else:
                vector = pd.concat([vector, g])  # 合并词频
                vector = vector.groupby('words').sum()
            wordset.append(g.index.values)
    bag = vector.index.values
    vescset = []
    for i in wordset:
        vesc = vectorlize(i)
        '''vesc = []
        for j in bag:
            if j in i:
                vesc.append(1)
            else:
                vesc.append(np.inf)'''
        vescset.append(vesc)
    searchspace = np.array(vescset)  # 获取搜索空间向量
    # np.place(searchspace, searchspace == 0, np.inf)


def getfilename(path):
    """
    获取文件名称,递归调用
    :param path:
    :return:
    """
    global filedict
    for root, direc, files in os.walk(path):
        if len(files) != 0:
            filedict.update({root: files})
    for i in range(len(direc)):
        getfilename(direc[i])


def stopwordsHandle():
    """
    读取停止词
    :return:
    """
    global stopwords
    with open('config.json', 'r') as f:
        item = json.load(f)
    names = list(item.keys())
    print('select stop words:')
    for i in range(1, len(names)):
        print(i, names[i])
    print('0 None')
    # choice = int(input())
    choice = 0  # FIXME:等下替换
    if choice > 0:
        stopath = item.get(names[choice])
        with open(stopath, 'r', encoding='utf-8') as f:
            stopwords = f.read()
        seg = pkuseg.pkuseg()
        stopwords = seg.cut(stopwords)
    else:
        stopwords = []


def getinput():
    # condi = input('input the ')
    global bag
    condi = 'present+sociaity+i+am'
    # FIXME:替换
    condi = handler(condi, bag=bag)
    return condi


def constructor(condi):
    global wordsetq
    ori = np.array([0 for i in range(len(bag))])
    cset = []
    for i in range(len(ori)):
        if i in condi.onpos:
            ori[i] = 1
    for i in range(len(ori), -1, -1):
        if i in condi.offpos:
            if len(cset) == 0:
                a = copy.deepcopy(ori)
                a[i] = 1
                cset.append(a)
                cset.append(ori)
            else:
                tmp = []
                for j in cset:
                    tmp.append(j)
                    a = copy.deepcopy(j)
                    a[i] = 1
                    tmp.append(a)
                cset = tmp
    if len(cset) > 0:
        return cset
    else:
        return [ori]


def bool_search(request):
    global searchspace
    tmp = np.array(request)
    res = []
    searchres = []
    if tmp.shape[0] == 1:
        for i in range(searchspace.shape[0]):
            res.append((searchspace[i] == tmp).all())
        for j in range(len(res)):
            if res[j]:
                searchres.append(j)
    else:
        for k in range(tmp.shape[0]):
            for i in range(searchspace.shape[0]):
                res.append((searchspace[i] == tmp[i]).all())
            for j in range(len(res)):
                if res[j]:
                    searchres.append(j)
    if len(searchres) == 0:
        print("No result found!")
        return
    searchres = np.array(searchres)
    unik, cnt = np.unique(searchres, return_counts=True)
    resultFin = dict(zip(unik, cnt))
    resultFin = list(resultFin.keys())
    return resultFin


def sim_search(request):
    global searchspace
    totalres = []
    for SingleVECtor in request:
        tmp = np.array(SingleVECtor)
        res = []
        for rowindex in range(searchspace.shape[0]):
            sim = cosim(tmp, searchspace[rowindex])
            res.append(sim)
        totalres.append(res)
    totalres = np.array(totalres)
    final = totalres.mean(axis=0)
    final = np.argsort(final)
    final = list(final)
    final.reverse()
    return final


def getres(fin):
    global filedict
    res = []
    for i in fin:
        res.append(filedict[i])
    return res


def teardown(tak):
    res = []
    for i in tak:
        if isinstance(i, list):
            res = teardown(i)
        else:
            res.append(i)
    return res


def resprint(res):
    names = []
    for i in filedict.values():
        if isinstance(i, list):
            for j in i:
                names.append(j)
        else:
            names.append(i)
    print('bool search result:')
    for i in res[0]:
        print(names[i])
    print('sim search result:')
    for i in res[1]:
        print(names[i])


if __name__ == '__main__':
    vaildcheck()
    global stopwords, vector, wordset, searchspace, filedict, fileset
    filedict = {}
    wordset = []
    stopwordsHandle()
    vector = []
    getfilename(path)
    getcontent()
    fileset = teardown(list(filedict.values()))
    # TODO:上面为正常处理获取文件词袋
    request = getinput()
    # FIXME:要用特殊用例才有用
    request = constructor(request)
    boolres = bool_search(request)
    simres = sim_search(request)
    reset = [boolres, simres]
    resprint(reset)
