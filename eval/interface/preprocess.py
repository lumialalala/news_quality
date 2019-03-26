#/usr/bin/env python
# -*- coding: UTF-8 -*-

from pyhanlp import *
import pandas as pd
from gensim import corpora, models
import gensim

"""加载停用词表，返回list数据"""
def load_stopwords():
    stopwords_list = []
    f = open("/media/Data/yangyuting/newsPopularity/data/stopwords.txt", "r")
    for line in f:
        stopwords_list.append(line.strip())
    f.close()
    return stopwords_list


"""去除停用词"""
def clean_stop_words(infilepath, outfilepath):
    all_data = pd.read_csv(infilepath, sep=",", header=0, encoding='UTF-8', index_col='weiboId')

    out_data = all_data[['seg']]
    out_data = out_data.rename(columns={'seg': 'after_clean_stop_words'})

    stopwords = load_stopwords()  # 加载停用词

    for weiboId in all_data.index:
        text = all_data.loc[weiboId, 'seg']
        print (weiboId)
        text = text.split(' ')

        """去除停用词"""
        after_clean_stop = ""
        for word in text:
            if word in stopwords:
                pass
            else:
                after_clean_stop += word
                after_clean_stop += ' '

        out_data.loc[weiboId, 'after_clean_stop_words'] = after_clean_stop

    out_data.to_csv(outfilepath, sep=',', header=True, index=True, encoding='UTF-8')


if __name__ == '__main__':
    infilepath = '/media/Data/yangyuting/newsPopularity/data/xinhua_renmin/haobin/train_pos_seg.csv'
    outfilepath = '/media/Data/yangyuting/newsPopularity/data/xinhua_renmin/haobin/train_pos_seg_no_stop.csv'
    clean_stop_words(infilepath, outfilepath)




