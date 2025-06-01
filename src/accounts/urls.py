from django.urls import path

from accounts.views import login_view, register_view, logout_view, profile_view, profile_edit_view

app_name = "accounts"

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
]
