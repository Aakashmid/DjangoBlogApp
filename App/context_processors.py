# yourapp/context_processors.py
from django.contrib.auth.models import User
from .models import BlogUser

def BlogUser_context(request):
    user = BlogUser.objects.get(user=request.user) if request.user.is_authenticated else None
    return {'User': user}