# ⚠️ Cyber Security Final Project (Vulnerable Version)

## 📌 Introduction
This repository contains a deliberately vulnerable web application developed to demonstrate common cybersecurity vulnerabilities, specifically SQL Injection and Cross-Site Scripting (XSS). It complements the secure version by highlighting security risks through practical examples.

## 🔎 Purpose
The aim of this project is educational:
- To showcase common vulnerabilities in web applications.
- To illustrate how these vulnerabilities can be exploited.
- To serve as a basis for learning and practicing secure coding practices.

## 🛠️ Technical Environment
- **Database**: MySQL
- **Web Framework**: Django
- **Language**: Python

## 🕸️ Demonstrated Vulnerabilities

### 1. SQL Injection
- Unsafely handled SQL queries that directly incorporate user input, making the database vulnerable to SQL Injection.
- Example:
```python
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
user = cursor.execute(query)
```

### 2. Cross-Site Scripting (XSS)
- Improper sanitization of user inputs, allowing attackers to inject malicious scripts executed on other users' browsers.
- Example:
```html
<div>
  User input: {{ user_input }}
</div>
```
*(Without proper escaping or validation)*

## ❌ Key Security Issues
- **No Input Validation**: Inputs from users are not validated or sanitized properly.
- **Direct Database Queries**: Using raw SQL statements instead of Django ORM exposes the application to SQL injection.
- **Insecure Rendering**: User inputs are directly rendered without encoding or escaping, leading to XSS vulnerabilities.
- **No CSRF Protection**: Forms are missing CSRF tokens, enabling Cross-Site Request Forgery attacks.


## 🚨 Warning
This project is intended solely for educational purposes. **Do NOT deploy or use this application in production environments.**

## 🚀 Setup
```bash
git clone <repository-url>
cd VulnerableCyberProject
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🛡️ Learning Recommendations
- Study how these vulnerabilities manifest and how to mitigate them.
- Refer to the secure version of this project to understand best practices for writing secure code.

## 📞 Contact
- Yuval Betito
- Email: yuval36811@gmail.com

---
**Use responsibly for educational purposes only.**

