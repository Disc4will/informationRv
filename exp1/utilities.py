import copy
import re
import pkuseg

global signs, logsign
signs = {'(': ')', '{': '}', '[': ']'}
logsign = ['|', '+']


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


'''def findend(string):
    st = stdstack()
    for i in range(len(string)):
        if string[i] in list(signs.keys()):
            st.push(i)
        elif string[i] in list(signs.values()):
            for j in range(len(st.left) - 1, -1, -1):
                if signs[string[st.left[j]]] == string[i]:
                    st.pop(j)
                    break
        if st.empty() and i != 0:
            return i


def handle(string, index):
    for i in range(string, index + 1):
        if i == '+' :
            string[i] = '|'
'''


class stack:
    left = []
    string = ''


    def __init__(self, string):
        string.replace(' and ', '+')
        string.replace('or', '|')
        for i in list(signs.keys()):
            if string.count(i) != string.count(signs[i]):
                raise ValueError
        DisOrderpattn = re.compile(r'[+|]?\([^)}\]]*[\)]*[+|]?')  # ε€ηεεΊ
        res = DisOrderpattn.finditer(string)
        if len(list(res)) > 0:
            SameND = lambda a, b: True if a.startswith(b) and a.endswith(b) else False
            displace = []
            for i in res:
                a = list(i.span())
                if SameND(string[a[0]:a[1]], '|') or SameND(string[a[0]:a[1]], '+'):
                    a[1] -= 1
                displace.append(a)
            displace = sorted(displace, key=lambda x: x[1] - x[0])
            seq = sorted(displace, key=lambda k: k[0])
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
            for j in range(len(stringrefine) - 1):
                if stringrefine[j] in logsign and stringrefine[j + 1] in logsign:
                    stringrefine = stringrefine[:j] + stringrefine[j + 1:]
        else:
            stringrefine = string
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
            if string[i] in list(signs.keys()):  # εΊη°οΌ
                if len(self.left) == 0 and i != 0:  # ζ οΌ
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
        str_list = list(str_origin)  # ε­η¬¦δΈ²θ½¬list
        str_list.insert(pos, str_add)  # ε¨ζε?δ½η½?ζε₯ε­η¬¦δΈ²
        str_out = ''.join(str_list)  # η©Ίε­η¬¦θΏζ₯
        return str_out


hasLOWer = re.compile(r'\(.*\)')


def condisplit(string):  # εει»θΎεΌ
    st = stdstack()
    oriplace = 0
    subset = []
    for i in range(len(string)):
        if string[i] in logsign and st.empty():  # ιε°ι»θΎη¬¦εζΆη©Ίζ 
            sub = string[oriplace:i + 1]  # ζ·»ε ζ‘δ»Ά
            subset.append(sub)
            oriplace = i + 1
        elif string[i] in list(signs.keys()):  # ε·¦ζ¬ε·
            st.push(i)
        elif string[i] in list(signs.values()):
            for j in range(len(st.left) - 1, -1, -1):
                if signs[string[st.left[j]]] == string[i]:  # εΉιζ¬ε·
                    st.pop(j)
        if i == len(string) - 1:
            sub = string[oriplace:i + 1]
            subset.append(sub)
    nxlv = []
    for i in subset:
        if i.startswith('(') and (i[-2] == ')' or i[-1] == ')'):  # δΈδΈηΊ§θ½¬ζ’
            nxlv.append(i)
    for i in nxlv:  # η§»ι€δΈδΈηΊ§
        subset.remove(i)
    for i in range(len(nxlv)):
        if nxlv[i].startswith('(') and nxlv[i].endswith(')'):  # εε
            nxlv[i] = nxlv[i][1:len(nxlv[i]) - 1]
    if len(nxlv) > 0:
        subset.append(nxlv)  # θΏζ₯
    return subset


def logconvert(subset):  # εεεηι»θΎεΌθ½¬ζ’
    condi = {'and': [], 'or': []}
    for i in subset:
        if not isinstance(i, list):  # ζι»θΎη¬¦ε½ε₯ε―ΉεΊε­εΈ
            if i[-1] == '+':
                oldcondi = list(condi['and'])
                oldcondi.append(i[0:-1])
                condi.update({'and': oldcondi})
            elif i[-1] == '|':
                oldcondi = list(condi['or'])
                oldcondi.append(i[0:-1])
                condi.update({'or': oldcondi})
            else:  # ζζ«ε°Ύζ‘δ»Ά
                count = i.count('+')
                count += i.count('|')
                sub = condisplit(i)
                if len(sub) > 1:
                    symbol = sub[-2][-1]
                else:
                    symbol = subset[-2][-1]
                if count == 1 or count == 0:  # ζ ιε±
                    if symbol == '+':
                        oldcondi = list(condi['and'])
                        oldcondi.append(i)
                        condi.update({'and': oldcondi})
                    elif symbol == '|':
                        oldcondi = list(condi['or'])
                        oldcondi.append(i)
                        condi.update({'or': oldcondi})
                else:  # ζιε±
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
        else:  # εθ‘¨οΌεδΈδΈηΊ§ιε½θ°η¨
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
    θ?‘η?εΊη°ηι»θΎε­η¬¦ζ°
    :param string:
    :return:
    """
    cout = 0
    for i in logsign:
        cout += string.count(i)
    return cout


def respit(dic):  # ιε½ε€ηζͺεε²ζ‘δ»Ά
    for i in list(dic.keys()):
        for j in list(dic[i]):
            if not isinstance(j, dict):  # ιζ¬‘ηΊ§
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


def nextLV(dic, vector, wordset):
    bag = list(wordset)
    for i in list(dic.keys()):
        for j in dic[i]:
            if isinstance(j, dict):
                vector = nextLV(j, vector)
            else:
                if i == 'and':
                    if not j.startswith('~'):
                        vector.onpos.append(bag.index(j))
                    else:
                        vector.onpos.appned(bag.index(j[1:]))
                elif i == 'or':
                    if not j.startswith('~'):
                        vector.offpos.append(bag.index(j))
                    else:
                        vector.offpos.appned(bag.index(j[1:]))
    return vector


def handler(string, bag):
    st = stack(string)
    vector = vec()
    tmp = condisplit(st.string)
    tmp = logconvert(tmp)
    tmp = respit(tmp)
    res = nextLV(tmp, vector, bag)
    return res


'''wordset = ['hello', 'ζη', 'test', 'a', 'b', 'δΈδΈͺε³ε?', 'test', 'nh']
string = 'nh+(a+b)+(hello|ζη+(test+(a+b)))+δΈδΈͺε³ε?+(test)'#
st = stack(string)
print(st.string)
st.part()
# print(st.string)
c = handler(string)
print(c.onpos)
print(c.offpos)'''
