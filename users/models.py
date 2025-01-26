# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from utils.password_utils import hash_password, check_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import hashlib
import os
from datetime import timedelta
from django.utils.timezone import now
from django.core.mail import send_mail

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # שימוש בפונקציה להגדיר סיסמה
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)  # ייחודי
    email = models.EmailField(unique=True)  # ייחודי
    password = models.CharField(max_length=128)  # שמירת סיסמה כטקסט גלוי
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    login_attempts = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'username'  # השדה הראשי הוא username
    REQUIRED_FIELDS = ['email']  # להשאיר email כשדה חובה

    def set_password(self, raw_password):
        # שמירת הסיסמה ללא הצפנה
        self.password = raw_password

    def check_password(self, raw_password):
        # השוואה פשוטה בין סיסמה גולמית לסיסמה שנשמרה
        return self.password == raw_password

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        שולח אימייל למשתמש זה.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.email

class PasswordHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.BinaryField()  # לאחסן את הסיסמה המוצפנת
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password history for {self.user.email} at {self.created_at}"


class LoginAttempts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Login attempts for {self.user.email} at {self.last_attempt_at}"

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=15)  # אם צריך להכליל קידומת
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.customer_id}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40, unique=True)  # מתאים ל-SHA-1
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # בדיקה אם הטוקן בתוקף (1 שעה לדוגמה)
        return now() < self.created_at + timedelta(hours=1)

    @staticmethod
    def generate_token():
        return hashlib.sha1(os.urandom(64)).hexdigest()