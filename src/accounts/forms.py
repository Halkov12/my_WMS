# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import Customer


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "birth_date",
            "photo",
            "role",
        ]

    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email вже існує.")
        return email

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'photo', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }