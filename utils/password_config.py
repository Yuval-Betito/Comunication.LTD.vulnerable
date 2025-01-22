

PASSWORD_CONFIG = {
    'min_length': 10,
    'complexity': {
        'uppercase': True,
        'lowercase': True,
        'digits': True,
        'special_characters': True,
    },
    'history_limit': 3,
    'dictionary_check': True,
    'max_login_attempts': 3,
    'lock_duration_minutes': 10  # זמן נעילה לאחר כשלונות
}


def is_password_complex(password):
    errors = []
    if len(password) < PASSWORD_CONFIG['min_length']:
        errors.append(f"Password must be at least {PASSWORD_CONFIG['min_length']} characters long.")
    if PASSWORD_CONFIG['complexity']['uppercase'] and not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter.")
    if PASSWORD_CONFIG['complexity']['lowercase'] and not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter.")
    if PASSWORD_CONFIG['complexity']['digits'] and not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit.")
    if PASSWORD_CONFIG['complexity']['special_characters'] and not any(char in "!@#$%^&*()_+[]{}|:,.<>?" for char in password):
        errors.append("Password must contain at least one special character.")
    return errors
