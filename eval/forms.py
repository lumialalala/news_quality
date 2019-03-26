from django import forms


class AddForm(forms.Form):
	news_content = forms.CharField(error_messages={'required':u'输入内容不能为空'})
