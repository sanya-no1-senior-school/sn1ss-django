from django.shortcuts import render
from .models import User,Blog,Category
import json

# Create your views here.

def index(request):
    context={}
    context['categories']=json.loads(Category.objects.all()[0].categories)['categories']
    context['blogs']=Blog.objects.all().order_by('-publish_time')
    return render(request,"index.html",context)

