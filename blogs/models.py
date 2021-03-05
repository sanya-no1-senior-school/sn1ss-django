from django.db import models
import datetime

# Create your models here.

class Blog(models.Model):
    blogid=models.IntegerField("文章ID",primary_key=True,default=1)
    author=models.ForeignKey("User",on_delete=models.CASCADE)
    title=models.CharField("标题",max_length=64)
    read=models.IntegerField("阅读量",default=0)
    star=models.IntegerField("点赞数",default=0)
    comment=models.IntegerField("评论数",default=0)
    publish_time=models.DateTimeField(auto_now_add=True)
    category=models.CharField("分类板块",max_length=128)
    digest=models.CharField("摘要",max_length=128)
    text=models.TextField("正文",max_length=50000)

    def __str__(self):
        return self.author.username+"->"+self.title

class Category(models.Model):
    categories=models.TextField("JSON格式板块数组数据",max_length=32767,default="{\"categories\":[\"默认\"]}")

class User(models.Model):
    userid=models.IntegerField(primary_key=True)
    username=models.CharField("用户名",max_length=16)
    password=models.CharField("密码",max_length=25)
    blogs=models.TextField("JSON格式作品ID数组数据",max_length=32767)

    def __str__(self):
        return str(self.userid)+"->"+self.username


