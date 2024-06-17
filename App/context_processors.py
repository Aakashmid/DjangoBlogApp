# yourapp/context_processors.py
from django.contrib.auth.models import User
from .models import BlogUser

def BlogUser_context(request):
    if request.user.is_authenticated:
        try :
            user = BlogUser.objects.get(user=request.user)
        except Exception as e:
            user=None
    else:
        user=None
    return {'User': user}
