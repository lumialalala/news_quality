#/usr/bin/env python
# -*- coding: UTF-8 -*-

from pyhanlp import *
import pandas as pd
from gensim import corpora, models
import gensim
import os
"""加载手工特征，返回list数据（共54个特征）"""
def load_features_name():
    feature_list = []
    f = open(os.getcwd()+"/static/file/manual_feature.txt")
    #f = open("/media/Data/yangyuting/newsPopularity/data/xinhua_renmin/manual_feature.txt", "r")
    for line in f:
        feature_list.append(line.strip())
    f.close()
    return feature_list

if __name__ == '__main__':
    a = load_features_name()
    print (a)