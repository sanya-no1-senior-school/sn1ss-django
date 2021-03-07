import base64
from django.http import response
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .models import CalcBlogHash, User, Blog, Category,Resource
import hashlib
import markdown
import re
import json
import datetime
import random
import base64

# Create your views here.
def GenerateBlogHash():
    m=hashlib.md5()
    m.update(bytes(str(random.randint(10,1000000))+str(datetime.datetime.today()),encoding='utf-8'))
    hash=m.hexdigest()[0:16]
    return hash

def GetResourceHash():
    m=hashlib.md5()
    m.update(bytes(str(random.randint(10,1000000))+str(datetime.datetime.today()),encoding='utf-8'))
    hash=m.hexdigest()[0:22]
    return hash

def isLogin(request):
    uid = request.COOKIES.get('loginauth_uid', None)
    pwd = request.COOKIES.get('loginauth_pwd', None)
    if uid is None:
        return False
    user = User.objects.get(userid=int(uid))
    if user is None:
        return False
    else:
        m = hashlib.md5()
        m.update(bytes(user.password, encoding='utf-8'))
        if m.hexdigest() == pwd:
            return True
        return False


def GetUser(request):
    uid = request.COOKIES.get('loginauth_uid', None)
    user = User.objects.get(userid=int(uid))
    return user


def index(request):
    context = {}
    logged=False
    if isLogin(request):
        logged=True

    context['categories'] = Category.objects.all()
    context['blogs'] = Blog.objects.all().order_by('-publish_time')
    hotblogs=Blog.objects.all().order_by('-read')
    context['hotblogs']=hotblogs[0:8]
    
    if logged:
        if request.GET.get('logout',None) is not None:
            response=render(request, "index.html", context)
            response.delete_cookie('loginauth_uid')
            response.delete_cookie('loginauth_pwd')
            return response
        else:
            context['username'] = GetUser(request).username
            context['uid'] = GetUser(request).userid
    return render(request, "index.html", context)


def GenerateBlogDigest(text):
    if str(text).__len__() > 120:
        return str(text)[0:125]
    else:
        return str(text)


def clean_html(html):  # 利用nltk的clean_html()函数将html文件解析为text文件
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()


def newblog(request):
    if request.method == "POST":
        if isLogin(request):
            title = request.POST.get('title', None)
            text = request.POST.get('text', None)
            category = request.POST.get('category', None)
            attachment = request.POST.get('attachment', None)
            user = GetUser(request)
            tm_text = text.replace("\"", "&quot;").replace("&", "&amp;").replace(
                "<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;").replace("\n","\n\n")
            blog_m: Blog = Blog()
            blog_m.author = user
            blog_m.category = Category.objects.get(name=category)
            blog_m.category.number = blog_m.category.number+1
            blog_m.category.save()
            blog_m.text = tm_text
            blog_m.title = title
            blog_m.digest = GenerateBlogDigest(
                clean_html(markdown.markdown(text)))
            blog_m.bloghash=CalcBlogHash()
            if attachment is not None:
                blog_m.attachment=attachment
            blog_m.save()
            return HttpResponse("{\"success\":\""+blog_m.bloghash+"\"}")
        else:
            return HttpResponse("非法提交")
    context = {}
    if isLogin(request):
        context['username'] = GetUser(request).username
        context['uid'] = GetUser(request).userid
        context['categories'] = Category.objects.all()
        return render(request, "newblog.html", context)
    else:
        return redirect("/login/")


def login(request):
    if request.method == "POST":
        uid = request.POST.get('uid', None)
        pwd = request.POST.get('password', None)
        if uid == None or pwd == None:
            return redirect("/login/?err=输入无效。")
        user = User.objects.get(userid=int(uid))
        if user is None:
            return redirect("/login/?err=此用户不存在。")
        elif user.password == pwd:
            response = redirect("/")
            m = hashlib.md5()
            m.update(bytes(pwd, encoding='utf-8'))
            response.set_cookie('loginauth_uid', uid)
            response.set_cookie('loginauth_pwd', m.hexdigest())
            return response
        else:
            return redirect("/login/?err=用户名或密码错误。")

    return render(request, "login.html", {})


def viewBlog(request, bloghash):
    context = {}
    blog_m:Blog = Blog.objects.get(bloghash=bloghash)
    logged=False
    if isLogin(request):
        context['username'] = GetUser(request).username
        context['uid'] = GetUser(request).userid
        if context['uid']==blog_m.author.userid:
            context['del_enable']=True
        logged=True

    if blog_m is None:
        context['title'] = "404"
        return render(request, "blog.html", context)
    else:
        if logged:
            user=GetUser(request)
            history=json.loads(user.viewhistory)
            history[str(datetime.datetime.today())]=[blog_m.bloghash,blog_m.title]
            user.viewhistory=json.dumps(history)
            user.save()
            blog_m.read=blog_m.read+1
            blog_m.save()
        context['bl'] = blog_m
        context['htmlcontent'] = markdown.markdown(blog_m.text)
        if blog_m.attachment.__len__()>16:
            attachs=json.loads(blog_m.attachment)
            got_img=False
            got_other=False
            attach_image=[]
            attach_audio=[]
            attach_video=[]
            attach_other=[]
            for i in attachs:
                k=json.loads(i)
                if k[0].__contains__("image"):
                    attach_image.append(k[1])
                    got_img=True
                elif k[0].__contains__("audio"):
                    attach_audio.append(k[1])
                    got_other=True
                elif k[0].__contains__("video"):
                    attach_video.append(k[1])
                    got_other=True
                else:
                    attach_other.append(k[1])
                    got_other=True
            if got_img:
                context["attach_image"]=attach_image
                context["got_img"]=got_img
            elif got_other:
                context["attach_audio"]=attach_audio
                context["attach_video"]=attach_video
                context["attach_other"]=attach_other
                context["got_other"]=got_other

    return render(request, "blog.html", context)

def userSpace(request,uid):
    context={}
    person=User.objects.get(userid=uid)
    if isLogin(request):
        uid=GetUser(request).userid
        if uid==person.userid:
            context['viewmyself']=True
    if person is None:
        context["person"]["username"]="查无此人"
        return render(request,"user.html",context)
    context["person"]=person
    context["pblogs"]=person.blog_set.all().order_by('-publish_time')
    pub=0
    read=0
    star=0
    for i in context["pblogs"]:
        pub=pub+1
        read=read+i.read
        star=star+i.star
    context["totalpost"]=pub
    context["totalvisit"]=read
    context["totalstar"]=star
    history:dict=json.loads(person.viewhistory)
    history_list=[]
    for i in history.keys():
        if history[i] not in history_list:
            history_list.append(history[i])
    history_list.reverse()
    context["vblogs"]=history_list[0:10]
    return render(request,"user.html",context)

def attachRev(request):
    data = request.POST.get('base64', None)
    if data is None or data=="":
        return HttpResponse("failed")
    datatype=data.split(';')[0].split(':')[1]
    data_real=data.split(';')[1].split(',')[1]
    res:Resource=Resource()
    res.data_type=datatype
    res.data=base64.decodebytes(bytes(data_real,encoding="utf-8"))
    res.hashid=GetResourceHash()
    res.save()
    predata=[res.data_type,res.hashid]
    return HttpResponse(json.dumps(predata))

def getAttach(request,attach_hash):
    resource:Resource=Resource.objects.get(hashid=attach_hash)
    if resource is None:
        return HttpResponse("No such Data.")
    else:
        response=HttpResponse(resource.data)
        response["content-type"]=resource.data_type
        response["content-length"]=resource.data.__len__()
        print("请求的附件大小："+str(resource.data.__len__()))
        return response

def removeBlog(request,bloghash):
    context={}
    if isLogin(request):
        context['username'] = GetUser(request).username
        context['uid'] = GetUser(request).userid
        context['bloghash'] = bloghash
    else:
        return render(request,"removeblog.html",{})
    
    if request.method=="POST":
        blog_m:Blog=Blog.objects.get(bloghash=bloghash)
        if blog_m.attachment.__len__()>16:
            attachs=json.loads(blog_m.attachment)
            for i in attachs:
                k=json.loads(i)
                res:Resource=Resource.objects.get(hashid=k[1])
                res.delete()
        blog_m.delete()
        return redirect("/")
    
    return render(request,"removeblog.html",context)