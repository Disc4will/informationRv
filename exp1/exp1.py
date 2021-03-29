import pkuseg
import numpy as np
import os
import threading, copy, json, re
import pandas as pd
from runME import vaildcheck

global filedict
filedict = {}


def cosim(a, b):
    '''

    :param a: numpy array
    :param b: same
    :return: cosine simularity
    '''
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
            vesc.append(np.inf)
    return vesc


def condisplit(condi):  # TODO：在文件2/3里有一个更好的试试替换
    condiset = []
    k = 0
    for i in range(len(condi)):
        if condi[i] in ['+', '|']:
            subcondi = condi[k:i]
            k = i
            condiset.append(subcondi)
    return condiset


def parase(cmd):  # TODO：在文件2/3里有一个更好的试试替换
    logicalsign = {'+': 0, '|': 1}
    condi = cmd.replace(' and ', '+')
    condi = condi.replace('&', '+')
    condi = condi.replace(' or ', '|')
    condi = condi.replace(' not ', '~')
    explev = 0
    k = 0
    subcondiset = []
    lencondi = len(condi)
    for i in range(lencondi):
        if condi[i] == '(':
            if explev == 0:
                k = i
            explev += 1
        elif condi[i] == ')':
            explev -= 1
        elif condi[i] in list(logicalsign.keys()) or i == lencondi:
            if k != i and explev == 0:
                subcondi = condi[k:i]
                k = i
                subcondiset.append(subcondi)
    seg = pkuseg.pkuseg()
    condi = seg.cut(condi)
    print(subcondiset)
    condi = filiter(condi)
    condi = vectorlize(condi)
    return condi


'''
test part
seg = pkuseg.pkuseg()
print(seg.cut('hello ond world but not me at los anglious'))
cmd = '使用默认配置+进行分词（如果用户无法确定+分词领域，推荐||使用默认模型分词'
cmd = cmd.replace('+', ' and ')
cmd = cmd.replace('||', ' or ')
cmd = cmd.replace('~', ' not ')
print(cmd)
print(seg.cut(cmd))
'''


class readthread(threading.Thread):  # TODO:多线程实现
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        readcontent(path)


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
            if isinstance(vector, list):  # type(vector) == type([])
                vector = copy.deepcopy(g)
            else:
                vector = pd.concat([vector, g])  # 合并词频
                vector = vector.groupby('words').sum()
            wordset.append(vector.index.values)
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


'''------- another way of count
    count=Counter(content)
    print(count.most_common(2))
        words = []
    for i in content:
        words.extend(i)
'''


def getfilename(path):
    '''
    获取文件名称,递归调用
    :param path:
    :return:
    '''
    global filedict
    for root, direc, files in os.walk(path):
        if len(files) != 0:
            filedict.update({root: files})
    for i in range(len(direc)):
        getfilename(direc[i])


def stopwordsHandle():
    '''
    读取停止词
    :return:
    '''
    global stopwords
    with open('config.json', 'r') as f:
        item = json.load(f)
    names = list(item.keys())
    print('select stop words:')
    for i in range(1, len(names)):
        print(i, names[i])
    print('0 None')
    choice = int(input())
    if choice > 0:
        stopath = item.get(names[choice])
        with open(stopath, 'r', encoding='utf-8') as f:
            stopwords = f.read()
        seg = pkuseg.pkuseg()
        stopwords = seg.cut(stopwords)
    else:
        stopwords = []


'''if __name__ == '__main__':
    validcheck()
    global stopwords, vector, wordset, searchspace
    wordset = []
    stopwordsHandle()
    vector = []
    getfilename(path)
    getcontent()
'''
# TODO:上面为正常处理获取文件词袋
'''vaildcheck()
global stopwords, vector, wordset, searchspace
wordset = []
stopwordsHandle()
vector = []
getfilename(path)
getcontent()
a = parase('一个决定+(hello|我的+(test))')'''
