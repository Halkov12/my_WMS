from django.urls import path

from .views import (CustomLoginView, CustomLogoutView, ProfileEditView,
                    ProfileView, RegisterView, PasswordChangeView, UserListView, UserDetailView)

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
    path("profile/password/", PasswordChangeView.as_view(), name="password_change"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user_detail"),
]
