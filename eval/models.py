
from mongoengine  import *
from news_quality.settings import DBNAME

# Create your models here.
connect(DBNAME)
class News(Document):
	meta = {"collection":"news_quality"}
	#新闻ID
	news_id = IntField()
	#新闻内容
	content = StringField(max_length=200)
	#新闻发表时间
	timeStamp = StringField(null=True)
	#转发数
	forward = IntField(null=True)
	#点赞数
	praise = IntField(null=True)
	#评论数
	comment = IntField(null=True)
	#用户反馈
	feedback = IntField(null=True)
	#总体得分
	score = IntField(null=True)
	#可读性
	readability = IntField(null=True)
	#逻辑性
	logic = IntField(null=True)
	#可信性
	persuasive = IntField(null=True)
	#专业性
	formality = IntField(null=True)
	#交互性
	interactivity = IntField(null=True)
	#有趣度
	interesting = IntField(null=True)
	#动人性
	moving = IntField(null=True)
	#完整性
	intergrity = IntField(null=True)


