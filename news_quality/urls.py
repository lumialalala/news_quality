"""news_quality URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from eval import views as eval_views

urlpatterns = [

	#path(r'', eval_views.index, name='home'),
	
	#path(r're.html',eval_views.re, name = 're'),
	#path(r'index.html', eval_views.index, name='home'),
    #path('admin/', admin.site.urls),
    #首页的路由
    path(r'',eval_views.index),
    path(r'index.html',eval_views.index),

    #单个评估框的路由
    
    path(r're/',eval_views.re ),
    path(r're.html',eval_views.re),

    #对比评估框的路由
    path(r're2.html',eval_views.compare),
    path(r're2',eval_views.ajax_list),
    
    #列表页的路由
    path(r'list.html',eval_views.getNews, name = "news_list"),
    path(r're2/delete',eval_views.deleteNews),
    path(r're2/getFB', eval_views.getFB)
    
]
