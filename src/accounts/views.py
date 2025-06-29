from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView
from django.shortcuts import redirect, render
from django.views import View
from django.utils import timezone
from datetime import timedelta
import logging
from django.db import models

from accounts.forms import CustomerRegistrationForm, ProfileUpdateForm, EmailLoginForm, PasswordChangeForm
from accounts.models import Customer
from wms.models import StockOperation


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailLoginForm

    def get_success_url(self):
        return reverse_lazy("wms:index")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            # Обновляем кастомные поля после успешного входа
            if hasattr(self.request.user, 'update_last_login'):
                try:
                    self.request.user.update_last_login()
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error updating last login: {e}")
            return response
        except Exception as e:
            # Логируем ошибку для отладки
            logger = logging.getLogger(__name__)
            logger.error(f"Login error: {e}")
            raise


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("wms:index")

    def form_valid(self, form):
        user = form.save()
        # Автоматический логин после регистрации
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
            # Обновляем статистику входа для нового пользователя
            if hasattr(user, 'update_last_login'):
                try:
                    user.update_last_login()
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error updating last login after registration: {e}")
        messages.success(self.request, "Registration was successful.")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Временно отключаем обновление статистики для отладки
        # if hasattr(user, 'increment_profile_views'):
        #     try:
        #         user.increment_profile_views()
        #     except Exception:
        #         pass
        
        # Статистика активности пользователя
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        # Операции пользователя
        user_operations = StockOperation.objects.filter(created_by=user)
        
        # Безопасное получение значений
        role_display = user.get_role_display()
        
        # Вычисляем длительность регистрации
        registration_duration = user.get_registration_duration()
        
        context.update({
            "user": user,
            "total_operations": user_operations.count(),
            "operations_this_week": user_operations.filter(created_at__date__gte=last_week).count(),
            "operations_this_month": user_operations.filter(created_at__date__gte=last_month).count(),
            "last_operation": user_operations.order_by('-created_at').first(),
            "role_display": role_display,
            "age": user.get_age(),
            "registration_duration": registration_duration,
        })
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile_edit.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профіль успішно оновлено!")
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, View):
    template_name = "accounts/password_change.html"

    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Пароль успішно змінено!")
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form})


class UserListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/user_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем список пользователей
        users = Customer.objects.filter(is_active=True).order_by('-date_joined')
        
        # Подсчитываем статистику
        total_users = users.count()
        week_ago = timezone.now().date() - timedelta(days=7)
        active_users = users.filter(
            models.Q(last_login_date__date__gte=week_ago) | 
            models.Q(last_login__date__gte=week_ago)
        ).count()
        
        context.update({
            "users": users,
            "total_users": total_users,
            "active_users": active_users,
        })
        return context


class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        
        try:
            user = Customer.objects.get(id=user_id, is_active=True)
            # Временно отключаем обновление статистики для отладки
            # if hasattr(user, 'increment_profile_views'):
            #     try:
            #         user.increment_profile_views()
            #     except Exception:
            #         pass
            
            # Статистика пользователя
            user_operations = StockOperation.objects.filter(created_by=user)
            
            # Безопасное получение значений
            role_display = user.get_role_display()
            
            # Вычисляем возраст и длительность регистрации
            age = user.get_age()
            registration_duration = user.get_registration_duration()
            
            context.update({
                "profile_user": user,
                "total_operations": user_operations.count(),
                "recent_operations": user_operations.order_by('-created_at')[:5],
                "role_display": role_display,
                "age": age,
                "registration_duration": registration_duration,
            })
        except Customer.DoesNotExist:
            messages.error(self.request, "Користувача не знайдено.")
            return redirect('accounts:user_list')
            
        return context
