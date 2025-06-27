from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from accounts.models import Customer


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs['autofocus'] = True
        self.fields['password'].label = 'Пароль'

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            from django.contrib.auth import authenticate
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages.get('invalid_login', "Невірний email або пароль."),
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


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

    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=False)

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email вже існує.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone_number", "photo", "birth_date"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }
