import numpy as np


# TODO:写一个获取文件中矩阵的模块，排序的模块

# 获取一个关系矩阵，这里测试来用，直接赋值返回
def prepare(matrix):  # 横入纵出
    cnt = np.sum(matrix, axis=0)
    res = np.divide(matrix, cnt)
    return res


def init_realtion_array(matrix):
    cnt = np.sum(matrix, axis=0)
    res = np.divide(matrix, cnt)
    return res


# 初始化最初的pr值
def init_first_pr(length):
    pr = np.zeros((length, 1), dtype=float)  # 构造一个存放pr值的矩阵
    for i in range(length):
        pr[i] = float(1) / length
        return pr


# 计算PageRank值
def compute_pagerankX(p, m, v):
    i = 1
    while (True):
        v = p * np.dot(m, v) + (1 - p) * v
        i = i + 1
        if i >= 10:
            break
            return v


if __name__ == '__main__':
    a = np.array([[0, 1, 1, 0],
                  [1, 0, 0, 1],
                  [1, 0, 0, 1],
                  [1, 1, 0, 0]])
    relation_array = init_realtion_array(a)
    pr = init_first_pr(relation_array.shape[0])
    p = 0.8
    print(compute_pagerankX(p, relation_array, pr))
    print(p, relation_array, pr)
