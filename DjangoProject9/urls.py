from django.contrib import admin
from django.urls import path
from users import views  # ודא שיש ייבוא של views

urlpatterns = [
    #path('admin/', admin.site.urls),

    path('register/', views.register, name='register'),
    path('', views.home, name='home'),  # דף הבית
    path('user_home/', views.user_home, name='user_home'),
    path('create_customer/', views.create_customer, name='create_customer'),
    path('login/', views.login_user, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
]