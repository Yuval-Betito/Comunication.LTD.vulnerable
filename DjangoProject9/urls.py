from django.contrib import admin
from django.urls import path, include  # include ייבוא

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', include('users.urls')),  # מפנה ל-urls.py של האפליקציה users
]
