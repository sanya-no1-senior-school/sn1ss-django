from django.contrib import admin
from blogs.models import Blog,Category,User,Resource

# Register your models here.
admin.site.register(Blog)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Resource)