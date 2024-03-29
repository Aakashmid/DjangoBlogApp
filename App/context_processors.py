# yourapp/context_processors.py
from django.contrib.auth.models import User
from .models import BlogUser,PostCategory

def BlogUser_context(request):
    if request.user.is_authenticated:
        user = BlogUser.objects.get(user=request.user)
    else:
        user=None
    return {'User': user}

def PostCateg_context(request):  #Categories returning to templates to use 
    Categ=PostCategory.objects.all()
    return {"ForAllCategories":Categ}