import logging
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from accounts.models import Customer

logger = logging.getLogger(__name__)


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs['autofocus'] = True
        self.fields['password'].label = 'Пароль'

    def clean(self):
        try:
            email = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            if email and password:
                from django.contrib.auth import authenticate
                self.user_cache = authenticate(self.request, email=email, password=password)
                if self.user_cache is None:
                    logger.warning(f"Failed login attempt for email: {email}")
                    raise forms.ValidationError(
                        self.error_messages.get('invalid_login', "Невірний email або пароль."),
                        code='invalid_login',
                    )
                else:
                    logger.info(f"Successful login for user: {email}")
                    self.confirm_login_allowed(self.user_cache)
            return self.cleaned_data
        except Exception as e:
            logger.error(f"Login form error: {e}")
            raise


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

    def save(self, commit=True):
        user = super().save(commit=False)

        user.show_email = True
        user.show_phone = False
        user.show_birth_date = False
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "first_name", 
            "last_name", 
            "email", 
            "phone_number", 
            "photo", 
            "birth_date",
            "position",
            "department",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.TextInput) or isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Поточний пароль"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Новий пароль"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Підтвердження нового пароля"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Поточний пароль введено неправильно.")
        return current_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Паролі не співпадають.")
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user