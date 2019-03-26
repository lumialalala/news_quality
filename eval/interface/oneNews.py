#/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import division

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np
from datetime import datetime
import csv
import ast
from datetime import timedelta
from pyhanlp import *
import re
from .get_features_name import load_features_name
from .preprocess import load_stopwords
from .getSentimentFromTencent import get_content
from sklearn.preprocessing import MinMaxScaler

"""分词"""
def seg(data):
    Id = data.index[0]
    data['seg'] = None
    data['pos'] = None
    after_seg = HanLP.segment(data.loc[Id, 'content'])
    segs = []  # 保存所有单词
    poses = []  # 保存所有词性
    for term in after_seg:
        segs.append(term.word)
        poses.append(str(term.nature))  # 词性字段不知为何，需要先转换为str
    seg_str = " ".join(segs)  # list转str（以空格隔开）
    pos_str = " ".join(poses)
    data.loc[Id, 'seg'] = seg_str
    data.loc[Id, 'pos'] = pos_str
    return data


"""预处理：去除停用词"""
def preprocess(data):
    stopwords = load_stopwords()  # 加载停用词
    Id = data.index[0]
    text = data.loc[Id, 'seg']
    text = text.split(' ')
    # 去除停用词
    after_clean_stop = ""
    for word in text:
        if word in stopwords:
            pass
        else:
            after_clean_stop += word
            after_clean_stop += ' '
    data.loc[Id, 'after_clean_stop_words'] = after_clean_stop
    return data

"""
归一化（最大最小方法）
"""
def MaxMinNormalization(x, Max, Min):
    if Max == Min:
        return x
    else:
        x = (x - Min) / (Max - Min);
        return x


"""计算各项特征值"""
def get_feature(data):
    """1. 提取特征"""
    """一些自定义的词表"""
    first_pronoun = ['我', '我们','咱','咱们']
    second_pronoun = ['你', '你们']
    third_pronoun = ['他', '他们', '她', '她们', '它', '它们']
    adversative = ['但', '但是', '然而', '却', '而', '偏偏', '只是', '不过', '至于', '致', '不料', '岂知', '可是']
    function_pos = ['d', 'p', 'c', 'u', 'e', 'o']
    question_mark = ['？']
    exclamation_mark = ['！']
    broken_point = ['，', '；', '、', '：']  # 代表句中停顿的部分
    sentence_end = ['】', '。', '？', '！', '...']
    modal_particle = ['难道', '决', '岂', '反正', '也许', '大约', '大概', '果然', '居然', '竟然', '究竟', '幸而', '幸亏', '偏偏', '明明', '恰恰',
                      '未免', '只好', '不妨', '索性', '简直', '就', '可', '难怪', '反倒', '何尝', '何必']
    adv_of_degree = ['很', '非常', '极', '十分', '最', '顶', '太', '更', '挺', '极其', '格外', '分外', '更加', '越', '越发', '有点儿', '稍', '稍微',
                     '略微', '几乎', '过于', '尤其']
    official_speech = ['通报', '称']
    uncertain_words = ['可能', '也许', '似乎', '大概', '或许']
    forward_reference = ['他', '他们', '她', '她们', '它', '它们', '那', '那些', '这', '这些']
    professional_words_pos = ['g', 'gb', 'gbc', 'gc', 'gg', 'gi', 'gm', 'gp']

    """文本特征"""
    high_features = list(['interactivity', 'interestingness', 'moving', 'persuasive', 'logic', 'readability', 'formality','Integrity1'])
    text_features = list(set(load_features_name()).difference(set(high_features)))
    text_features.remove('')

    Id = data.index[0]
    feature_temp = dict.fromkeys(text_features, 0)  # 暂时存放特征值
    feature_temp['sentences'] = 1  # 因为有的微博没有句子结束符号，而在计算句子破碎度时需要其做除数，因此，统一做加一平滑。
    """处理表情"""
    feature_temp['face_num'] = 0
    """处理图片"""
    feature_temp['hasImage'] = 0
    feature_temp['image_num'] = 9  # 接受输入：图片个数，图片特征影响较大，不宜直接置0
    """处理视频"""
    feature_temp['hasVideo'] = 0

    """处理url"""
    feature_temp['hasUrl'] = 0

    polar,confd,text = get_content(data.loc[Id, 'content'])  # 计算情感值（不用先去除停用词）
    feature_temp['sentiment_score'] = polar * confd

    segs = data.loc[Id, 'seg']
    poses = data.loc[Id, 'pos']
    segs = segs.split(' ')
    poses = poses.split(' ')

    for pos in poses:
        if pos == 'm':
            feature_temp['numerals'] += 1
        elif pos == 't':
            feature_temp['time_num'] += 1
        elif 'ns' in pos:
            feature_temp['place_num'] += 1
        elif 'nr' in pos:
            feature_temp['object_num'] += 1
        elif pos == 'a':
            feature_temp['adj_num'] += 1
        elif pos == 'y':
            feature_temp['modal_particle_num'] += 1
        elif pos == 'cc':
            feature_temp['conj_num'] += 1
        elif 'ry' in pos:
            feature_temp['Interrogative_pron_num'] += 1
        elif pos == 'i':
            feature_temp['idiom_num'] += 1
        elif re.match('p', pos) != None:  # 若pos以p开头
            feature_temp['prep_num'] += 1
        elif re.match('v', pos) != None:  # 若pos以v开头
            feature_temp['verb_num'] += 1
        elif re.match('d', pos) != None:  # 若pos以d开头
            feature_temp['adv_num'] += 1
        if pos in professional_words_pos:
            feature_temp['professional_words_num'] += 1
        if re.match('n', pos) != None:  # 若pos以n开头
            feature_temp['noun_num'] += 1
        if re.match('r', pos) != None:  # 若pos以r开头
            feature_temp['pron_num'] += 1
    characters = 0
    words = 0
    broken_nums = 0  # 停顿次数
    LW = 0  # 该微博中包含的长词个数

    for word in segs:
        characters = characters + len(word)
        words = words + 1
        if word == '#':
            feature_temp['hasTag'] = 1
        elif word == '@':
            feature_temp['@'] += 1
            feature_temp['hasAt'] = 1
        elif word in exclamation_mark:
            feature_temp['exclamation_mark_num'] += 1
        elif word in question_mark:
            feature_temp['question_mark_num'] += 1
        elif word in first_pronoun:
            feature_temp['first_pronoun_num'] += 1
        elif word in second_pronoun:
            feature_temp['second_pronoun_num'] += 1
        elif word in adversative:
            feature_temp['adversative_num'] += 1
        elif word in modal_particle:
            feature_temp['modal_particle_num'] += 1
        elif word == '”' or word == '“':
            feature_temp['rhetoric_num'] += 1
        elif word in adv_of_degree:
            feature_temp['adv_of_degree_num'] += 1
        elif word in official_speech:
            feature_temp['official_speech_num'] += 1
        elif word in uncertain_words:
            feature_temp['uncertainty'] += 1
        elif word == '【':
            feature_temp['hasHead'] = 1
        if word in forward_reference:
            feature_temp['forward_reference_num'] += 1
        if len(word) > 2:
            LW += 1
        if word in sentence_end:
            feature_temp['sentences'] += 1
        elif word in broken_point:
            broken_nums += 1

    feature_temp['LW'] = LW
    feature_temp['RIX'] = LW / feature_temp['sentences']
    feature_temp['LIX'] = words / feature_temp['sentences'] + (100 * LW) / words

    feature_temp['rhetoric_num'] = feature_temp['rhetoric_num'] / 2  # 一对“”才能表示一个引用
    feature_temp['sub_sentences'] = broken_nums + feature_temp['sentences']  # 子句个数=句中停顿次数+句子结束次数
    feature_temp['sentence_broken'] = feature_temp['sub_sentences'] / feature_temp['sentences']  # 句子破碎度=所有句子的停顿次数/句子总数
    feature_temp['characters'] = characters

    feature_temp['words'] = words
    feature_temp['average_word_length'] = characters / words

    for fea in feature_temp.keys():
        data.loc[Id, fea] = feature_temp[fea]

    """2. 对基本特征做归一化"""
    # 记录所有数据中各项特征的最大最小值(更改归一化方式前后，feature_maxmin是不变的)
    maxmin = pd.read_csv(os.getcwd()+'/static/file/feature_maxmin.csv', sep=",", header=0, encoding='UTF-8', index_col='feature')
    for fea in text_features:
        data.loc[Id, fea] = MaxMinNormalization(data.loc[Id, fea], maxmin.loc[fea, 'max'], maxmin.loc[fea, 'min'])

    """3. 计算高级特征"""
    data.loc[Id, 'interactivity'] = data.loc[Id,'question_mark_num'] + data.loc[Id,'first_pronoun_num'] + data.loc[Id,'second_pronoun_num'] + data.loc[Id,'Interrogative_pron_num']
    data.loc[Id,'interestingness'] = data.loc[Id,'rhetoric_num'] + data.loc[Id,'exclamation_mark_num'] + data.loc[Id,'face_num'] + data.loc[Id,'adj_num'] + data.loc[Id,'idiom_num'] + data.loc[Id,'adversative_num'] + data.loc[Id, 'image_num']
    data.loc[Id,'moving'] = data.loc[Id,'sentiment_score'] + data.loc[Id,'first_pronoun_num'] + data.loc[Id,'second_pronoun_num'] + data.loc[Id,'exclamation_mark_num'] + data.loc[Id,'question_mark_num'] + data.loc[Id,'adv_of_degree_num'] + data.loc[Id,'modal_particle_num']
    data.loc[Id,'persuasive'] = data.loc[Id,'image_num'] + data.loc[Id,'numerals'] + data.loc[Id,'@'] + data.loc[Id,'official_speech_num'] + data.loc[Id,'time_num'] + data.loc[Id,'place_num'] + data.loc[Id,'object_num'] - data.loc[Id,'uncertainty']
    data.loc[Id,'logic'] = data.loc[Id,'forward_reference_num'] + data.loc[Id,'conj_num']
    data.loc[Id,'readability'] = -(data.loc[Id,'sentence_broken'] + data.loc[Id,'characters'] + data.loc[Id,'words'] + data.loc[Id,'average_word_length'] + data.loc[Id,'sentences'] + data.loc[Id,'sub_sentences'] + data.loc[Id,'professional_words_num'] + data.loc[Id,'RIX'] + data.loc[Id,'LIX'] + data.loc[Id,'LW'])
    data.loc[Id,'formality'] = data.loc[Id,'noun_num'] + data.loc[Id,'adj_num'] + data.loc[Id,'prep_num'] - data.loc[Id,'pron_num'] - data.loc[Id,'verb_num'] - data.loc[Id,'adv_num'] - data.loc[Id,'sentence_broken']
    data.loc[Id,'Integrity1'] = 2 * data.loc[Id,'hasHead'] + 2 * data.loc[Id,'hasImage'] + 2 * data.loc[Id,'hasVideo'] + 2 * data.loc[Id,'hasTag'] + data.loc[Id,'hasAt'] + data.loc[Id,'hasUrl']

    """4. 对高级特征做归一化"""
    for fea in high_features:
        data.loc[Id, fea] = MaxMinNormalization(data.loc[Id,fea], maxmin.loc[fea, 'max'], maxmin.loc[fea, 'min'])

    return data


"""对计算出的质量分数做处理：归一化，截断，放大"""
def process(data):
    Id = data.index[0]
    score_name = ['newsQualityScore','readability_score', 'logic_score', 'persuasive_score', 'formality_score', 'interactivity_score','interestingness_score', 'moving_score', 'Integrity1_score']
    # 用作归一化
    score_maxmin = pd.read_csv(os.getcwd()+'/static/file/score_maxmin.csv', sep=",", header=0, encoding='UTF-8', index_col='score_name')
    # 用作截断
    # score_norm_maxmin = pd.read_csv('/media/Data/yangyuting/newsPopularity/data/xinhua_renmin/all_norm/score_norm_maxmin.csv', sep=",", header=0, encoding='UTF-8', index_col='score_name')
    for sn in score_name:
        # 归一化
        print(sn, score_maxmin.loc[sn, 'max'], score_maxmin.loc[sn, 'min'])
        mmax = score_maxmin.loc[sn, 'max']
        mmin = score_maxmin.loc[sn, 'min']
        data.loc[Id, sn] = MaxMinNormalization(data.loc[Id, sn], mmax, mmin)
        if data.loc[Id, sn] >1:  # 第二种截断方式
            data.loc[Id, sn] = 1
        elif data.loc[Id, sn] <0:
            data.loc[Id, sn] = 0
        # 第一种截断方式
        # if data.loc[Id, sn] > score_norm_maxmin.loc[sn, 'max']:
        #     data.loc[Id, sn] = score_norm_maxmin.loc[sn, 'max']
        # elif data.loc[Id, sn] < score_norm_maxmin.loc[sn, 'min']:
        #     data.loc[Id, sn] = score_norm_maxmin.loc[sn, 'min']
        # 放大 （放大为0-100之间的整数）
        data.loc[Id, sn] = math.ceil(data.loc[Id, sn] * 100)
    return data


def get_quality(data):
    feature_weight = pd.read_csv(os.getcwd()+'/static/file/feature_weight.csv', sep=",", header=0, encoding='UTF-8', index_col='feature')
    style_category = ['readability_score', 'logic_score', 'persuasive_score', 'formality_score', 'interactivity_score','interestingness_score', 'moving_score', 'Integrity1_score']
    readability_score = ['readability', 'sentence_broken', 'characters', 'words', 'average_word_length', 'sentences','sub_sentences', 'professional_words_num', 'RIX', 'LIX', 'LW']
    logic_score = ['logic', 'forward_reference_num', 'conj_num']
    persuasive_score = ['persuasive', 'numerals', '@', 'official_speech_num', 'time_num', 'place_num', 'object_num','uncertainty', 'image_num']
    formality_score = ['formality', 'noun_num', 'prep_num', 'pron_num', 'verb_num', 'adv_num', 'adj_num','sentence_broken']
    interactivity_score = ['interactivity', 'question_mark_num', 'first_pronoun_num', 'second_pronoun_num', 'Interrogative_pron_num']
    interestingness_score = ['interestingness', 'rhetoric_num', 'exclamation_mark_num', 'face_num', 'adj_num','idiom_num', 'adversative_num', 'image_num']
    moving_score = ['moving', 'sentiment_score', 'adv_of_degree_num', 'modal_particle_num', 'first_pronoun_num','second_pronoun_num', 'exclamation_mark_num', 'question_mark_num']
    Integrity1_score = ['Integrity1', 'hasHead', 'hasVideo', 'hasTag', 'hasAt', 'hasUrl']

    add_cols = style_category + ['newsQualityScore']
    data = pd.concat([data, pd.DataFrame(columns=add_cols)])
    data = data.fillna(0.0)

    Id = data.index[0]
    # 计算总的质量分数
    for fea in feature_weight.index:
        data.loc[Id, 'newsQualityScore'] += feature_weight.loc[fea, 'weight'] * data.loc[Id, fea]
    # 每一类风格特征的分数
    for style in style_category:
        # 每一类
        style_list = locals()[style]  # 将字符串转换为变量
        # 类里的每个特征
        for fea in style_list:
            data.loc[Id, style] += feature_weight.loc[fea, 'weight'] * data.loc[Id, fea]
    # 重命名，得到最终返回结果
    # 返回值1
    score = {}
    score['Writing_Score'] = data.loc[Id, 'newsQualityScore']
    score['Readability'] = data.loc[Id, 'readability_score']
    score['Logic'] = data.loc[Id, 'logic_score']
    score['Credibility'] = data.loc[Id, 'persuasive_score']
    score['Formality'] = data.loc[Id, 'formality_score']
    score['Interactivity'] = data.loc[Id, 'interactivity_score']
    score['Interestingness'] = data.loc[Id, 'interestingness_score']
    score['Sensation'] = data.loc[Id, 'moving_score']
    score['Integrity'] = data.loc[Id, 'Integrity1_score']
    # 对计算出的分数做处理（归一化，截断，放大）
    new_data = process(data)
    # 返回值2
    result = {}
    result['Writing_Score'] = new_data.loc[Id, 'newsQualityScore']
    result['Readability'] = new_data.loc[Id, 'readability_score']
    result['Logic'] = new_data.loc[Id, 'logic_score']
    result['Credibility'] = new_data.loc[Id, 'persuasive_score']
    result['Formality'] = new_data.loc[Id, 'formality_score']
    result['Interactivity'] = new_data.loc[Id, 'interactivity_score']
    result['Interestingness'] = new_data.loc[Id, 'interestingness_score']
    result['Sensation'] = new_data.loc[Id, 'moving_score']
    result['Integrity'] = new_data.loc[Id, 'Integrity1_score']

    # 返回值（返回的分别是原始计算分数和经过处理后的分数）
    return score, result


def newsQualityAssessment(news):
    """1.预处理"""
    # 将输入文本（字符串）转换为Dataframe
    data = {'weiboId':[1], 'content':[news]}
    data = pd.DataFrame(data)
    """2. 分词"""
    data = seg(data)
    """3. 去停用词+计算情感值"""
    # 用腾讯的接口，不用先去除停用词
    # no_stop = preprocess(data)
    """4. 计算各项特征"""
    feature_data = get_feature(data)
    """5. 获得质量评估结果"""
    quality_result = get_quality(feature_data)
    return quality_result


if __name__ == '__main__':
    # news = '#2016里约奥运#【此刻，一起传递！为中国女排！我们是>冠！军！转】里约奥运会女排决赛，中国3-1战胜塞尔维亚，夺得冠军！激动人心的比赛！女排精神，就是永！不！言！败！此刻，一起为中国姑娘喝彩！为郎平喝彩！'
    # news='【羊！年！到！啦！ 】0:00，又是一年！这一年，有收获，也有失落，有甜蜜，也有忧伤；这一>年，踮起脚尖，有的梦想实现了，有的梦想还有些远…新一年，新开始！这一刻，旧的自我离开！新的自我诞生！新的一年，每当不自信，不勇敢时，告诉自己，再来一次！[推荐]此刻，为自己转发！为自己加油！'
    # news = '【三月，再见！】过完今>天，三月不再，一年四分之一将逝！有遗憾？没有人能重返过去。不甘心？你所站立之处即起点！告别三月、迎>接四月最好的仪式：不再赖在安逸的被窝，不再捧着手机刷个不停，不再追随错误的想法，不再选择阻力最小的>人生道路，趁春光美好，去追寻那个更非凡的自己！出发，就现在！'
    # news = '【辽宁-北京 CBA总决赛第六场 你支持谁？转发为他加油！】今晚19:35，CBA总决赛第六场比赛移师辽宁主场进行，辽宁目前大比分2-3落>后，本场不容有失！北京若能客场告捷，将成功卫冕！微调查：谁能获胜？你支持谁？转！为他们加油！'
    # news = '#2016里约奥运#【网友说：净胜4分，姑娘们拼的就是意志！】@郎朗：幸福的眼泪！@Merida_da ：真的让人感动、震撼！@-wuuuuuu ：女排姑娘们真的好棒！个个都是最美的！太感动了！@小晖1222 ：你们是最棒哒！决赛加油！对女排姑娘，你想说？ \\ #2016里约奥运#【强者不是没有眼泪，只是含着眼泪向前奔跑！】刚刚结束的女排半决赛，中国队3-1战胜荷兰队（27-25\/23-25\/29-27\/25-23），晋级决赛！赛后，姑娘们和主教练郎平相拥，喜极而泣。“我们的姑娘很棒，是最坚>强的！”为她们鼓掌，转起支持！' # 85
    news = '【昨晚315重磅曝光汇总！都在坑咱！转！】①东风日产、上海大众、奔驰4S店，小病大修！没病也大修！就为收钱！②路虎倒挡失灵，路虎竟称，因中国人开车太着急；③D&amp;G、H&amp;M、ZARA等服装上黑榜；④移动、铁通为骚扰电话提供各种支持！⑤联通用你的身份证办手机卡，然后卖给骗子！扩散！别被坑！' # 70,74
    # news = '【315曝光企业名单】今年3·15主题是“消费在阳光下”，>本次3·15除晚会 曝光品牌外，网上也开辟了曝光台，包括路虎、京东等知名企业均被消费者曝光。了解更多侵权行为，维护消费者合法权益，看看这份详尽曝光名单。' # 50,53
    # news="【今天，你愿为人类的朋友转发吗？】非洲是地球上为数不多还能看到很多大型哺乳动物可以自由生存的地方。保护非洲的生态环境和野生动植物不仅是非洲国家的责任，更是国际社会的责任。#2018中非合作论坛#即将召开，野生动物保护是中非合作重点领域之一。我们同属一个地球，转发微博，你可以影响更多人！"
    # news="【又有两名南京大屠杀幸存者去世…[蜡烛]】@侵华日军南京大屠杀遇难同胞纪念馆 ：南京大屠杀幸存者赵金华，12月2日凌晨去世，享年94岁。南京大屠杀幸存者陈广顺，3日凌晨去世，享年94岁。今年已有20位幸存者去世。两位老人没能见到第五次国家公祭，没能等到加害者的那一句道歉。转发，送别老人！" # 45
    # news = "【两位94岁南京大屠杀幸存者去世[蜡烛] 转发送别】南京大屠杀幸存者赵金华，于2日凌晨12点30分去世，享年94岁。南京大屠杀幸存者陈广顺，于3日凌晨1点20分去世，享年94岁。至此，今年已有20位幸存者去世。转发，送别老人[蜡烛] @侵华日军南京大屠杀遇难同胞纪念馆 ​​​​" # 41
    origin_score, score = newsQualityAssessment(news)  # 返回的分别是原始计算分数和经过处理后的分数
    print(origin_score, score)
