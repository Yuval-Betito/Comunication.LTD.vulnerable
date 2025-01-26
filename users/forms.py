from django import forms
from .models import Customer


from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'customer_id', 'phone_number', 'email']

    # הסרת הוולידציות כדי להדגים קוד פגיע

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email")

class ResetPasswordForm(forms.Form):
        token = forms.CharField(widget=forms.HiddenInput())
        new_password = forms.CharField(widget=forms.PasswordInput(), label="New Password")
        confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

        def clean(self):
            cleaned_data = super().clean()
            new_password = cleaned_data.get("new_password")
            confirm_password = cleaned_data.get("confirm_password")

            if new_password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
            return cleaned_data