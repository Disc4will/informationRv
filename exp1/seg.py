import re

string = '一个决定+test+nh+(a+b)+(hello|我的+(test+(c+d)))'
logsign = ['|', '+']
signs = {'(': ')', '{': '}', '[': ']'}


class stack:
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
    st = stack()
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


subset = condisplit(string)
print(subset)


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
                # symbol = subset[subset.index(i) - 1][-1]
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


a = logconvert(subset)
sign = tuple(a.keys())

print(logconvert(subset))
a = {'and': ['e+f', 'a+b', {'and': ['c+d'], 'or': []}], 'or': []}
dic = a
condi = {}


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


dic = logconvert(subset)
dic = {'and': ['c', 'd'], 'or': []}
dic = respit(dic)
print(dic)
wordset=['a','b','c','d','e','f']
#TODO:建立搜索向量
for i in list(dic.keys()):
    for j in dic[i]:
        if  isinstance(j, dict):

        else:
            if not j.startswith('~'):
                onpos.append(wordset.index(j))
            else:
                offpos.appned(wordset.index(j[1:]))
# for i in list(dic.key+s()):
