import os
import json


def getfilename(path):
    global filename
    for root, direc, files in os.walk(path):
        if len(files) != 0:
            filename += files
    for i in range(len(direc)):
        getfilename(direc[i])


def vaildcheck():
    global filename
    filename = []
    getfilename(r'STOPwords')
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            itemcnt = json.load(f)
            itemcnt = itemcnt.get('total')
        if itemcnt != len(filename):
            path = [os.path.join('STOPwords', i) for i in filename]
            stopwords = {'total': len(filename)}
            stopwords.update(dict(zip(filename, path)))
            with open('config.json', 'w') as f:
                json.dump(stopwords, f,ensure_ascii=False)
    else:
        path = [os.path.join('STOPwords', i) for i in filename]
        stopwords = {'total': len(filename)}
        stopwords.update(dict(zip(filename, path)))
        with open('config.json', 'w') as f:
            json.dump(stopwords, f,ensure_ascii=False)


if __name__ == '__main__':
    vaildcheck()
