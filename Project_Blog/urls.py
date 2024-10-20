
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from App.admin import blog_site


urlpatterns = [
    path('blogadmin/', blog_site.urls),
    path('', include('App.urls')),
    # path('summernote/',include('django_summernote.urls')),
]


    
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# #  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
