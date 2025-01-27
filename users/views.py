# users/views.py
from .models import PasswordResetToken, User
from utils.password_utils import validate_password, hash_password, is_password_unique, check_password
from django.urls import reverse
import hashlib
import os
from .models import PasswordHistory
from django.contrib.auth import login
from users.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection


def home(request):
    return render(request, 'home.html')  # דף הבית הכללי

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

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        # בדיקת סיסמה נוכחית
        if not request.user.check_password(current_password):
            messages.error(request, "The current password is incorrect.")
            return redirect('change_password')

        # בדיקת התאמת סיסמאות
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('change_password')

        # בדיקת הסיסמה החדשה לפי כל הדרישות (כולל היסטוריה)
        password_errors = validate_password(new_password, user=request.user)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
            return redirect('change_password')

        # שמירת הסיסמה החדשה
        request.user.set_password(new_password)
        request.user.save()

        # עדכון היסטוריית סיסמאות
        from users.models import PasswordHistory
        PasswordHistory.objects.create(user=request.user, password=hash_password(new_password))

        messages.success(request, "Password changed successfully.")
        return redirect('user_home')

    return render(request, 'change_password.html')

@login_required
def user_home(request):
    print("Entered user_home view")  # הודעת דיבוג
    return render(request, 'user_home.html')


# פונקציה לכניסת משתמשים (פגיעה ל-SQL Injection)
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # שאילתת SQL פגיעה
        query = f"SELECT * FROM users_user WHERE username = '{username}' AND password = '{password}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            user_data = cursor.fetchone()

        if user_data:
            # יצירת אובייקט משתמש חוקי והתחברות למערכת
            user = User.objects.get(id=user_data[0])  # איתור המשתמש לפי ID
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # הגדרת backend
            login(request, user)  # התחברות המשתמש

            messages.success(request, "Logged in successfully.")
            return redirect('user_home')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')

# פונקציה להרשמת משתמשים (פגיעה ל-SQL Injection)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from utils.password_utils import validate_password

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

        # בדיקות סיסמה לפי תנאי הקונפיגורציה
        password_errors = validate_password(password)
        if password_errors:
            for error in password_errors:
                messages.error(request, error)
            return redirect('register')

        # קוד פגיע ל-SQL Injection
        user_exists_query = f"SELECT * FROM users_user WHERE username = '{username}' OR email = '{email}'"
        print(f"Executing user_exists_query: {user_exists_query}")
        with connection.cursor() as cursor:
            try:
                cursor.execute(user_exists_query)
                existing_users = cursor.fetchall()
            except Exception as e:
                print(f"Error executing user_exists_query: {e}")
                messages.error(request, "Error checking existing users.")
                return redirect('register')

        if existing_users:
            messages.error(request, "This username or email is already taken")
            return redirect('register')

        # יצירת משתמש חדש עם ערכי ברירת מחדל לעמודות NOT NULL
        query = f"INSERT INTO users_user (username, email, password, is_active, is_staff, is_superuser, login_attempts) VALUES ('{username}', '{email}', '{password}', 1, 0, 0, 0)"
        print(f"Executing query: {query}")
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                messages.success(request, "Registration successful. Please login.")
                return redirect('login')
            except Exception as e:
                print(f"Error executing query: {e}")
                messages.error(request, "Error creating user.")
                return redirect('register')

    return render(request, 'register.html')




# פונקציה ליצירת לקוח חדש (פגיעה ל-SQL Injection)
@login_required
def create_customer(request):
    if request.method == 'POST':
        # קבלת הקלטים מהטופס
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        customer_id = request.POST.get('customer_id', '')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', '')

        # שימוש בכתיב שונה למניעת בעיות תחביר
        insert_query = f"""
            INSERT INTO users_customer (first_name, last_name, customer_id, phone_number, email)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            # ביצוע השאילתה עם פרמטרים כדי להימנע מבעיות תחביר
            with connection.cursor() as cursor:
                cursor.execute(insert_query, [first_name, last_name, customer_id, phone_number, email])
            # הודעת הצלחה
            messages.success(request, "Customer added successfully.")
            # הצגת פרטי הלקוח בדף עם אפשרות ל-XSS
            return render(request, 'create_customer.html', {
                'customer': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'customer_id': customer_id,
                    'phone_number': phone_number,
                    'email': email
                }
            })
        except Exception as e:
            # טיפול בשגיאות
            messages.error(request, f"Error creating customer: {e}")

    # הצגת טופס ריק
    return render(request, 'create_customer.html')




















