from django import forms


class CurrencySettingForm(forms.Form):
    currency = forms.ChoiceField(choices=[("UAH", "₴ UAH"), ("USD", "$ USD"), ("EUR", "€ EUR")])
