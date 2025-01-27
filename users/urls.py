from django.urls import path
from users import views  # ודא שהייבוא של views תקין

urlpatterns = [
    path('', views.home, name='home'),  # דף הבית הראשי, מציג כפתורים להרשמה והתחברות
    path('login/', views.login_user, name='login'),  # דף התחברות
    path('register/', views.register, name='register'),  # דף הרשמה
    path('user_home/', views.user_home, name='user_home'),  # דף הבית של המשתמש אחרי התחברות
    path('create_customer/', views.create_customer, name='create_customer'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('change_password/', views.change_password, name='change_password'),
    path('customer_list/', views.customer_list, name='customer_list'),

]

