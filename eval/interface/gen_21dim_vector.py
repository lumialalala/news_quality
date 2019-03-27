# -*- coding: utf-8 -*-
from __future__ import division
"""
@author: RMSnow
@file: gen_21dim_vector.py
@time: 18-12-24 下午9:57
@contact: xueyao_98@foxmail.com

# 根据情感词典的匹配结果，生成对应的21维情感向量
"""

import pandas as pd
import numpy as np
from sklearn.externals import joblib
import io

# 加载情感词典
def _emotion_vocabulary():
    negative_words = []
    with io.open('./doc/negationWords.txt', 'r',encoding='UTF-8') as src:
        lines = src.readlines()
        for line in lines:
            negative_words.append(line.strip())

    how_words = dict()
    with io.open('./doc/intensifierWords.txt', 'r',encoding='UTF-8') as src:
        lines = src.readlines()
        for line in lines:
            how_word = line.strip().split()
            if len(how_word) != 2:
                # print(line)
                pass
            else:
                how_words[how_word[0]] = float(how_word[1])

    return negative_words, how_words

negative_words, how_words = _emotion_vocabulary()

def _get_negative_and_how_value(emotion_word, words, k_window=3):
    negative_num = 0
    how_value = 1
    end = words.index(emotion_word)
    start = (end - k_window) if (end - k_window) >= 0 else 0
    for word in words[start:end]:
        if word in negative_words:
            negative_num += 1
        if word in how_words.keys():
            how_value *= how_words[word]

    return (-1) ** negative_num, how_value

# 输入分完词的句子，输出情感值
def get_emotion_value(words):
    positive_words = {}
    passive_words = {}
    with io.open('./doc/negativeWords.txt', 'r',encoding='UTF-8') as src:
        lines = src.readlines()
        for line in lines:
            aline = line.strip().split()
            passive_words[aline[0]] = aline[1]
    with io.open('./doc/positiveWords.txt', 'r',encoding='UTF-8') as src:
        lines = src.readlines()
        for line in lines:
            aline = line.strip().split()
            positive_words[aline[0]] = aline[1]
    emotion_val = 0
    emotion_word_cnt = 0
    for word in words:
        n_value, how_value = _get_negative_and_how_value(word, words)
        word = word.decode('utf8') # 将word由utf-8解码为Unicode
        if word in positive_words.keys():
            emotion_val += n_value * how_value * int(positive_words[word])/9
            emotion_word_cnt += 1
        elif word in passive_words.keys():
            emotion_val += n_value * how_value * (-1.2) * int(passive_words[word])/9
            emotion_word_cnt += 1
    if emotion_word_cnt == 0:
        return 0
    else:
        return emotion_val/emotion_word_cnt



if __name__ == '__main__':
    sentence = ['我','深爱', '北京', '天安门']
    # sentence = ['【',' 权威',' 发布',' ：',' 载人',' 航天',' 工程',' 和',' 交会',' 对接',' 任务',' 主要',' 负责人',' 】',' O ','网页',' 链接']
    emotion_val = get_emotion_value(sentence)
    print(emotion_val)