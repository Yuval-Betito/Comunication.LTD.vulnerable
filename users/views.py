# users/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerForm
from django.contrib.auth import authenticate, login
from datetime import datetime, timedelta
from django.core.mail import send_mail
from .models import PasswordResetToken, User
from .forms import ForgotPasswordForm
from django.contrib.auth import get_user_model
from .forms import ResetPasswordForm
from utils.password_utils import validate_password, hash_password, is_password_unique
from django.urls import reverse
import hashlib
import os
from .models import PasswordHistory



def home(request):
    return render(request, 'home.html')  # דף הבית הכללי


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)

            # בדיקת מספר ניסיונות
            if user.login_attempts >= 3:
                messages.error(request, "Your account is locked due to too many failed login attempts. Please try again later.")
                return redirect('login')

            if user.check_password(password):
                user.login_attempts = 0  # איפוס ניסיונות אחרי התחברות מוצלחת
                user.save()
                login(request, user)
                messages.success(request, "Logged in successfully.")
                return redirect('user_home')
            else:
                user.login_attempts += 1
                user.save()
                messages.error(request, "Invalid credentials.")

        except User.DoesNotExist:
            messages.error(request, "User not found.")
    return render(request, 'login.html')



def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # בדיקה אם הסיסמאות תואמות
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        # בדיקה אם שם המשתמש כבר תפוס
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken")
            return redirect('register')

        # בדיקה אם האימייל כבר קיים
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered")
            return redirect('register')

        # בדיקות סיסמה
        password_errors = validate_password(password)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
            return redirect('register')

        # יצירת משתמש חדש
        user = User.objects.create_user(email=email, password=password, username=username)
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html')




def user_home(request):
    # דף הבית של היוזר עם כפתור 'צור לקוח'
    return render(request, 'user_home.html')

def create_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()  # שמירת הלקוח במסד הנתונים
            messages.success(request, "Customer added successfully.")  # הודעת הצלחה
            return render(request, 'create_customer.html', {'form': CustomerForm()})  # הישארות בדף
    else:
        form = CustomerForm()
    return render(request, 'create_customer.html', {'form': form})




def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            # יצירת טוקן
            token = hashlib.sha1(os.urandom(64)).hexdigest()
            PasswordResetToken.objects.create(user=user, token=token)

            # שליחת מייל
            reset_url = request.build_absolute_uri(reverse('reset_password', args=[token]))
            user.email_user(
                subject="Password Reset",
                message=f"Click the link to reset your password: {reset_url}",
            )
            messages.success(request, "A password reset email has been sent.")
            return redirect('reset_password', token=token)  # מעבר לדף Reset Password
        except User.DoesNotExist:
            messages.error(request, "No user found with that email address.")
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')


def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, "The reset token has expired.")
            return redirect('forgot_password')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid reset token.")
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password', token=token)

        # בדיקות סיסמה
        password_errors = validate_password(password, reset_token.user)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
            return redirect('reset_password', token=token)

        # שמירת הסיסמה החדשה
        reset_token.user.set_password(password)
        reset_token.user.save()

        # שמירת הסיסמה בהיסטוריה
        PasswordHistory.objects.create(user=reset_token.user, password=reset_token.user.password)

        # מחיקת הטוקן
        reset_token.delete()

        messages.success(request, "Your password has been reset successfully.")
        return redirect('login')

    return render(request, 'reset_password.html')