import pandas as pd
import numpy as np
from wordcloud import WordCloud

path = r"test"


class dpack:
    def __init__(self, path):
        self.data = pd.read_csv(path, header=None)


def getsim(mood, targ):
    return np.dot(mood, targ.T)
