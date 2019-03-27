from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render
from .forms import AddForm
import numpy as np
import pandas as pd
import logging
import sys
import time
from datetime import datetime
from django.http import JsonResponse
import json
from django.shortcuts import render_to_response,HttpResponseRedirect
from django.template import RequestContext
from .models import News
import datetime


sys.path.append("/eval/interface/")
logging.debug("no no no")
logging.debug(sys.path)
from .interface.oneNews import *
# Create your views here.


def index(request):
	return render(request, 'index.html')

def compare(request):
	return render(request, 're2.html')

def re(request):
	return render(request, 're.html')

def getNews(request):
	news_size = News.objects.all().count()
	logging.debug("news_size")
	logging.debug(news_size)
	news = News.objects.all().order_by("-timeStamp")
	logging.debug(news[0])
	
	

	
	No = np.arange(1,news_size+1)
	
	result = []
	for i in range(0,len(No)):
		temp =[i+1,news[i]]
		result.append(temp)
	#result = {'No':No, 'news':news}
	# 从数据库中读文件
	return render(request, 'list.html', {"show_title": "所有新闻信息", "re": result})
	#.order_by("-news_id")


#删除内容
def deleteNews(request):
	news_id = request.GET.get('news_id','')
	news = News.objects(news_id=news_id)
	for n in news:
		n.delete()
	return HttpResponseRedirect('/list.html')
	#return render(request, 'list.html', {"show_title": "所有新闻信息", "re": News.objects.all()})


def re(request):
	if request.method == 'POST':
		form = AddForm(request.POST)

		if form.is_valid():
			logging.debug(form)
			form = form.cleaned_data['news_content']
			#form = form['news_content'].value()
	else:
		form = AddForm
	scores = newsQualityAssessment(form)[1]
	
	scores = list(scores.values())
	scores_percent = []
	for i in range(0,len(scores)):
		scores_percent.append(scores[i]/100.0)
	scores_percent = [format(each, '.1%') for each in scores_percent]
	
	
	t = time.localtime()
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S',t)
	news_id = time.strftime('%Y%m%d%H%M%S',t)
	news= News(news_id = news_id)
	#对content去掉空格		
	news.content = form.replace(" ","")
	news.timeStamp = timestamp
	news.score = scores[0]
	news.readability = scores[1]
	news.logic = scores[2]
	news.persuasive = scores[3]
	news.formality = scores[4]
	news.interactivity = scores[5]
	news.interesting = scores[6]
	news.moving = scores[7]
	news.intergrity = scores[8]
	news.save()
	logging.debug("需要存入数据库")
	logging.debug(news.content)
	logging.debug("bye")



	#return render(request,'re.html', {'result':result})

	return render(request,'re.html', {'form':form, 'scores_percent':scores_percent, 'scores':scores})


def getFB(request):
	logging.debug("收到打分消息")
	fb =request.GET.get('fb','')
	news_id = request.GET.get('news_id','')
	if(fb and news_id):
		queryset = News.objects(news_id = news_id)
		queryset[0].update(feedback = fb)
	result = fb
	return JsonResponse(json.dumps(result), content_type='application/json',safe = False)

def ajax_list(request):
	logging.debug("跳转到ajax_list页面")
	content =request.GET.get('name','')
	news_id = request.GET.get('news_id','')
	
	result = []
	scores = newsQualityAssessment(content)[1]
	scores = list(scores.values())
	logging.debug(scores)
	scores_percent = []
	for i in range(0,len(scores)):
		scores_percent.append(scores[i]/100.0)
	scores_percent = [format(each, '.1%') for each in scores_percent]
	#logging.debug(type(scores))	
	#keys = ["整体得分","可读性","逻辑性","可信性","专业性","交互性","有趣度","动人性","结构完整性"]
	#keys_percent = ["整体得分百分比","可读性百分比","逻辑性百分比","可信性百分比","专业性百分比","交互性百分比","有趣度百分比","动人性百分比","结构完整性百分比"]
	result = []
	result.append(scores[0])
	for i in range(1,9):
		result.append(scores[i])
	for i in range(1,9):
		result.append(scores_percent[i])


	t = time.localtime()
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S',t)
	exp= "示例： #2016里约奥运#【此刻，一起传递！为中国女排！我们是冠！军！转】里约奥运会女排决赛，中国3-1战胜塞尔维亚，夺得冠军！激动人心的比赛！女排精神，就是永！不！言！败！此刻，一起为中国姑娘喝彩！为郎平喝彩！"
	if(content == exp):
		return JsonResponse(json.dumps(result), content_type='application/json',safe = False)
	# 如果news_id已经存在，则对该数据进行更新，防止某些字段不存在
	
	if(news_id):
		queryset = News.objects(news_id = news_id)
		queryset[0].update(content = content, timeStamp = timestamp, score = scores[0],readability = scores[1],logic = scores[2],
			persuasive = scores[3],formality = scores[4],interactivity = scores[5],
			interesting = scores[6],moving = scores[7],intergrity=scores[8])

	# 如果news_id不存在，则根据时间生成news_id，并存入数据库
	else:
		news_id = time.strftime('%Y%m%d%H%M%S',t)
		news= News(news_id = news_id)
		#对content去掉空格		
		news.content = content.replace(" ","")
		news.timeStamp = timestamp
		news.score = scores[0]
		news.readability = scores[1]
		news.logic = scores[2]
		news.persuasive = scores[3]
		news.formality = scores[4]
		news.interactivity = scores[5]
		news.interesting = scores[6]
		news.moving = scores[7]
		news.intergrity = scores[8]
		news.save()
		logging.debug("需要存入数据库")
		logging.debug(news.content)
		logging.debug("bye")

	result.append(news_id)

	return JsonResponse(json.dumps(result), content_type='application/json',safe = False)



	"""
	if(len(news)):
		result.append(news[0].score)
		result.append(news[0].readability)
		result.append(news[0].logic)
		result.append(news[0].persuasive)
		result.append(news[0].formality)
		result.append(news[0].interactivity)
		result.append(news[0].interesting)
		result.append(news[0].moving)
		result.append(news[0].interactivity)
		
		for i in range(1, 9):
			logging.debug(result[i])
			#score_percent = result[i]/100
			#format(score_percent,'.1%')
			#result.append(score_percent)
		logging.debug("检测到news_id, 不需要存入数据库")
		return JsonResponse(json.dumps(result), content_type='application/json',safe = False)
	else:
		
		scores = newsQualityAssessment(content)[1]
		scores = list(scores.values())
		logging.debug(scores)
		scores_percent = []
		for i in range(0,len(scores)):
			scores_percent.append(scores[i]/100.0)
		
		
		scores_percent = [format(each, '.1%') for each in scores_percent]
		#logging.debug(type(scores))	
		#keys = ["整体得分","可读性","逻辑性","可信性","专业性","交互性","有趣度","动人性","结构完整性"]
		#keys_percent = ["整体得分百分比","可读性百分比","逻辑性百分比","可信性百分比","专业性百分比","交互性百分比","有趣度百分比","动人性百分比","结构完整性百分比"]
		result = []
		result.append(scores[0])
		for i in range(1,9):
			result.append(scores[i])
		for i in range(1,9):
			result.append(scores_percent[i])

		news_id = t.strftime('%Y%m%d%H%M%S')
		timestamp = t.strftime('%Y/%m/%d,%H:%M:%S')
		news= News(news_id = news_id)
		news.content = content
		news.timeStamp = timestamp
		#评估结果总体得分
		eval_score = scores[0]
		news.score = eval_score
		news.readability = scores[1]
		news.logic = scores[2]
		news.persuasive = scores[3]
		news.formality = scores[4]
		news.interactivity = scores[5]
		news.interesting = scores[6]
		news.moving = scores[7]
		news.interactivity = scores[8]

		news.save()
		
		logging.debug("需要存入数据库")
		logging.debug(news.content)
		logging.debug("bye")

		return JsonResponse(json.dumps(result), content_type='application/json',safe = False)
	
	"""

