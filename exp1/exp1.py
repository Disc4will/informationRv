import copy
import json
import os
import re
import threading

import numpy as np
import pandas as pd
import pkuseg
from runME import vaildcheck


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
    choice = int(input())
    if choice > 0:
        stopath = item.get(names[choice])
        with open(stopath, 'r', encoding='utf-8') as f:
            stopwords = f.read()
        seg = pkuseg.pkuseg()
        stopwords = seg.cut(stopwords)
    else:
        stopwords = []


global signs, logsign
signs = {'(': ')', '{': '}', '[': ']'}
logsign = ['|', '+']


class stack:
    left = []
    string = ''

    def __init__(self, string):
        self.left = []
        for i in list(signs.keys()):
            if string.count(i) != string.count(signs[i]):
                raise ValueError
        DisOrderpattn = re.compile(r'[+|]?\([^)}\]]*[\)]*[+|]?')  # 处理倒序
        res = DisOrderpattn.finditer(string)
        SameND = lambda a, b: True if a.startswith(b) and a.endswith(b) else False
        displace = []
        for i in res:
            a = list(i.span())
            if SameND(string[a[0]:a[1]], '|') or SameND(string[a[0]:a[1]], '+'):
                a[1] -= 1
            displace.append(a)
        longer = lambda a: a[1] - a[0]
        displace = sorted(displace, key=longer)
        firstelem = lambda k: k[0]
        seq = sorted(displace, key=firstelem)
        dis = []
        for i in range(len(seq) - 1):
            ans = [seq[i][1], seq[i + 1][0]]
            dis.append(ans)
        seq = dis
        stringrefine = ''
        for i in seq:
            if not (string[i[0]:i[1]].startswith('+') or string[i[0]:i[1]].startswith('|')):
                stringrefine = string[i[0]:i[1]] + stringrefine
            else:
                stringrefine = stringrefine + string[i[0]:i[1]]
        findinsert = lambda x: x.find('+') if x.find('+') else x.find('|')
        for i in displace:
            if string[i[0]:i[1]].endswith('|') or string[i[0]:i[1]].endswith('+'):
                stringrefine = stringrefine + string[i[1] - 1] + string[i[0]:i[1] - 1]
            else:
                sigle = re.compile(r'\([^\(\)+|]*\)')
                if sigle.search(string[i[0]:i[1]]):
                    tribe = string[i[0]] + string[i[0] + 2:i[1] - 1]
                    stringrefine = self.__str_insert__(stringrefine, findinsert(stringrefine), tribe)
                else:
                    stringrefine = stringrefine + string[i[0]:i[1]]
        self.string = stringrefine

    def __match__(self, sign, string):
        global signs
        for i in range(len(self.left) - 1, -1, -1):
            if sign == signs[string[self.left[i]]]:
                return copy.deepcopy(self.left[i]), i

    def parse(self, string):
        global logsign
        # sub = []
        sub = {}
        for i in range(len(string)):
            if string[i] in list(signs.keys()):  # 出现（
                if len(self.left) == 0 and i != 0:  # 无（
                    substring = string[0:i - 1]
                    # sub.append(substring)
                    sub.update({0: [substring]})
                self.left.append(i)
            elif string[i] in list(signs.values()) and len(self.left) > 0:
                l, j = self.__match__(string[i], string)
                l = self.left.pop(j)
                f = lambda x: x - 1 if x > 0 else x
                l = f(l)
                r = i
                substring = string[l:r]
                if substring[1] in list(signs.keys()):
                    substring = substring[0] + substring[2:]
                # sub.append(substring)
                condispec = re.compile(r'[+|]\(.*\)')
                substring = re.sub(condispec, '', substring)
                if len(self.left) + 1 in list(sub.keys()):
                    old = sub[len(self.left) + 1]
                    old.append(substring)
                    new = old
                    sub.update({len(self.left) + 1: new})
                else:
                    sub.update({len(self.left) + 1: [substring]})
        return sub

    def part(self):
        self.sub = self.parse(self.string)
        # self.subcheck()

    def subcheck(self):
        for i in range(len(self.sub)):
            if self.sub[i][0].find('(') >= 0:
                self.sub[i][0] = self.parse(self.sub[i])

    def __str_insert__(self, str_origin, pos, str_add):
        str_list = list(str_origin)  # 字符串转list
        str_list.insert(pos, str_add)  # 在指定位置插入字符串
        str_out = ''.join(str_list)  # 空字符连接
        return str_out


class stdstack:
    left = []

    def __init__(self):
        self.left = []

    def empty(self):
        if len(self.left) > 0:
            return False
        else:
            return True

    def push(self, item):
        self.left.append(item)

    def pop(self, pos):
        a = self.left.pop(pos)
        return a


hasLOWer = re.compile(r'\(.*\)')


def condisplit(string):  # 切分逻辑式
    st = stdstack()
    oriplace = 0
    subset = []
    for i in range(len(string)):
        if string[i] in logsign and st.empty():  # 遇到逻辑符同时空栈
            sub = string[oriplace:i + 1]  # 添加条件
            subset.append(sub)
            oriplace = i + 1
        elif string[i] in list(signs.keys()):  # 左括号
            st.push(i)
        elif string[i] in list(signs.values()):
            for j in range(len(st.left) - 1, -1, -1):
                if signs[string[st.left[j]]] == string[i]:  # 匹配括号
                    st.pop(j)
        if i == len(string) - 1:
            sub = string[oriplace:i + 1]
            subset.append(sub)
    nxlv = []
    for i in subset:
        if i.startswith('(') and (i[-2] == ')' or i[-1] == ')'):  # 下一级转换
            nxlv.append(i)
    for i in nxlv:  # 移除下一级
        subset.remove(i)
    for i in range(len(nxlv)):
        if nxlv[i].startswith('(') and nxlv[i].endswith(')'):  # 切分
            nxlv[i] = nxlv[i][1:len(nxlv[i]) - 1]
    if len(nxlv) > 0:
        subset.append(nxlv)  # 连接
    return subset


def logconvert(subset):  # 切分后的逻辑式转换
    condi = {'and': [], 'or': []}
    for i in subset:
        if not isinstance(i, list):  # 按逻辑符归入对应字典
            if i[-1] == '+':
                oldcondi = list(condi['and'])
                oldcondi.append(i[0:-1])
                condi.update({'and': oldcondi})
            elif i[-1] == '|':
                oldcondi = list(condi['or'])
                oldcondi.append(i[0:-1])
                condi.update({'or': oldcondi})
            else:  # 最末尾条件
                count = i.count('+')
                count += i.count('|')
                sub = condisplit(i)
                symbol = sub[-2][-1]
                if count == 1 or count == 0:  # 无附属
                    if symbol == '+':
                        oldcondi = list(condi['and'])
                        oldcondi.append(i)
                        condi.update({'and': oldcondi})
                    elif symbol == '|':
                        oldcondi = list(condi['or'])
                        oldcondi.append(i)
                        condi.update({'or': oldcondi})
                else:  # 有附属
                    neosub = condisplit(i)
                    neosub = logconvert(neosub)
                    if symbol == '+':
                        oldcondi = list(condi['and'])
                        oldcondi.append(neosub)
                        condi.update({'and': oldcondi})
                    elif symbol == '|':
                        oldcondi = list(condi['or'])
                        oldcondi.append(neosub)
                        condi.update({'or': oldcondi})
        else:  # 列表，向下一级递归调用
            count = i.count('+')
            count += i.count('|')
            if len(subset) > 1:
                symbol = subset[subset.index(i) - 1][-1]
            else:
                symbol = '+'
            if symbol == '+':
                oldcondi = list(condi['and'])
                oldcondi.append(logconvert(i))
                condi.update({'and': oldcondi})
            elif symbol == '|':
                oldcondi = list(condi['or'])
                oldcondi.append(logconvert(i))
                condi.update({'or': oldcondi})
    return condi


def countsign(string):
    """
    计算出现的逻辑字符数
    :param string:
    :return:
    """
    cout = 0
    for i in logsign:
        cout += string.count(i)
    return cout


def respit(dic):  # 递归处理未分割条件
    for i in list(dic.keys()):
        for j in list(dic[i]):
            if not isinstance(j, dict):  # 非次级
                if j.startswith('(') and j.endswith(')'):
                    tmp = j[1:-1]
                else:
                    tmp = j
                for k in tmp:
                    if k in logsign:
                        index = tmp.index(k)
                        con1 = tmp[0:index]
                        con2 = tmp[index + 1:]
                        neo = [con1, con2]
                        if tmp[index] == '+':
                            oldcondi = list(dic['and'])
                            oldcondi.append({'and': neo, 'or': []})
                            oldcondi.remove(j)
                            dic.update({'and': oldcondi})
                        elif tmp[index] == '|':
                            oldcondi = list(dic['or'])
                            oldcondi.append({'and': [], 'or': neo})
                            oldcondi.remove(j)
                            dic.update({'or': oldcondi})
            else:
                respit(j)
    return dic


class vec:
    onpos = []
    offpos = []

    def __init__(self):
        self.onpos = []
        self.offpos = []

    def test(self):
        print(self.onpos)
        print(self.offpos)


def nextLV(dic, vector):
    global wordset
    for i in list(dic.keys()):
        for j in dic[i]:
            if isinstance(j, dict):
                vector = nextLV(j, vector)
            else:
                if i == 'and':
                    if not j.startswith('~'):
                        vector.onpos.append(wordset.index(j))
                    else:
                        vector.onpos.appned(wordset.index(j[1:]))
                elif i == 'or':
                    if not j.startswith('~'):
                        vector.offpos.append(wordset.index(j))
                    else:
                        vector.offpos.appned(wordset.index(j[1:]))
    return vector


def handler(string):
    st = stack(string)
    st.part()
    vector = vec
    tmp = condisplit(st.string)
    tmp = logconvert(tmp)
    tmp = respit(tmp)
    res = nextLV(tmp, vector)
    return res


if __name__ == '__main__':
    vaildcheck()
    global stopwords, vector, wordset, searchspace, filedict
    filedict = {}
    wordset = []
    stopwordsHandle()
    vector = []
    getfilename(path)
    getcontent()

# TODO:上面为正常处理获取文件词袋
'''vaildcheck()
global stopwords, vector, wordset, searchspace
wordset = []
stopwordsHandle()
vector = []
getfilename(path)
getcontent()
a = parase('一个决定+(hello|我的+(test))')'''
