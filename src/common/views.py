from django.shortcuts import render  # NOQA:F401

from django.shortcuts import render, redirect
from .forms import CurrencySettingForm
from common.utils.setting import set_setting, get_setting

def settings_view(request):
    if request.method == "POST":
        form = CurrencySettingForm(request.POST)
        if form.is_valid():
            set_setting("default_currency", form.cleaned_data["currency"])
            return redirect("settings")
    else:
        form = CurrencySettingForm(initial={
            "currency": get_setting("default_currency", "UAH")
        })
    return render(request, "settings.html", {"form": form})