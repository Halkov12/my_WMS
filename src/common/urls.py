from django.urls import path

from common.views import settings_view

app_name = "common"

urlpatterns = [
    path("settings/", settings_view, name="settings"),

]
