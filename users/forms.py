from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'customer_id', 'phone_number', 'email']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number.startswith('05'):
            raise forms.ValidationError("Phone number must start with '05'.")
        if len(phone_number) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        return phone_number


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