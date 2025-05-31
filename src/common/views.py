from django.shortcuts import render  # NOQA:F401
from django.shortcuts import redirect

from common.utils.setting import get_setting, set_setting

from .forms import CurrencySettingForm


def settings_view(request):
    if request.method == "POST":
        form = CurrencySettingForm(request.POST)
        if form.is_valid():
            set_setting("default_currency", form.cleaned_data["currency"])
            return redirect("settings")
    else:
        form = CurrencySettingForm(initial={"currency": get_setting("default_currency", "UAH")})
    return render(request, "settings.html", {"form": form})
