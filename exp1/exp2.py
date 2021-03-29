import copy
import re
import pkuseg
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
                    stringrefine = str_insert(stringrefine, findinsert(stringrefine), tribe)
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


def str_insert(str_origin, pos, str_add):
    str_list = list(str_origin)  # 字符串转list
    str_list.insert(pos, str_add)  # 在指定位置插入字符串
    str_out = ''.join(str_list)  # 空字符连接
    return str_out


string = '(hello|我的+(test+(a+b)))+一个决定+(test)+nh+(a+b)'
st = stack(string)
st.part()
print(st.sub)
print(st.string)
