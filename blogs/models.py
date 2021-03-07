from django.db import models
import datetime
import hashlib
import random
import datetime

# Create your models here.
def CalcBlogHash():
    m=hashlib.md5()
    m.update(bytes(str(random.randint(10,1000000))+str(datetime.datetime.today()),encoding='utf-8'))
    hash=m.hexdigest()[0:16]
    return hash

def GenerateBlogDigest(text):
    if str(text).__len__()>120:
        return str(text)[0:125]
    else:
        return str(text)

class User(models.Model):
    userid=models.IntegerField(primary_key=True,auto_created=True)
    username=models.CharField("用户名",max_length=16)
    password=models.CharField("密码",max_length=25)
    avatarimg=models.CharField("头像图片数据HASH",max_length=16,null=True)
    viewhistory=models.TextField("阅读过的数据的历史记录，JSON格式",default="{}")
    history_unseen=models.BooleanField("禁止游客查看历史记录",default=False)
    lastest_login=models.DateTimeField("最近上线",auto_now=True)
    def __str__(self):
        return str(self.userid)+"->"+self.username

class Category(models.Model):
    name=models.CharField("分类名称",max_length=16)
    number=models.IntegerField("总文章数")
    def __str__(self):
        return self.name

class Blog(models.Model):
    blogid=models.IntegerField("博客主键",auto_created=True,primary_key=True)
    bloghash=models.CharField("文章Hash",max_length=16,default=CalcBlogHash())
    author=models.ForeignKey(to=User,on_delete=models.CASCADE)
    title=models.CharField("标题",max_length=64)
    read=models.IntegerField("阅读量",default=0)
    star=models.IntegerField("点赞数",default=0)
    comment=models.IntegerField("评论数",default=0)
    publish_time=models.DateTimeField(auto_now_add=True)
    category=models.ForeignKey(to=Category,on_delete=models.CASCADE)
    text=models.TextField("正文",max_length=50000)
    digest=models.CharField('摘要',max_length=128,default=GenerateBlogDigest(text))
    attachment=models.TextField('JSON格式类型资源Hash数组',default="{}")

    def __str__(self):
        return self.author.username+"->"+self.title

def GetResourceHash():
    m=hashlib.md5()
    m.update(bytes(str(random.randint(10,1000000))+str(datetime.datetime.today()),encoding='utf-8'))
    hash=m.hexdigest()[0:22]
    return hash

class Resource(models.Model):
    rid=models.IntegerField("主键",primary_key=True,auto_created=True)
    data_type=models.CharField("数据类型",max_length=16)
    data=models.BinaryField("二进制数据")
    hashid=models.CharField("资源HASH",max_length=22,default=GetResourceHash())

    def __str__(self):
        return str(self.rid)+" "+self.data_type



