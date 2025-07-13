from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from accounts.managers import CustomerManager
class ROLE_CHOICES(models.IntegerChoices):
    WORKER = 0, "Worker"
    MANAGER = 1, "Manager"
    SELLER = 2, "Seller"
class Customer(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField("Ім'я", max_length=150, blank=True)
    last_name = models.CharField("Прізвище", max_length=150, blank=True)
    email = models.EmailField(
        "Email адреса",
        unique=True,
        error_messages={
            "unique": "Користувач з таким email вже існує.",
        },
    )
    phone_number = PhoneNumberField("Номер телефону", null=True, blank=True)
    is_staff = models.BooleanField(
        "Статус персоналу",
        default=False,
        help_text="Визначає, чи може користувач увійти в адмін-панель.",
    )
    is_active = models.BooleanField(
        "Активний",
        default=True,
        help_text=(
            "Визначає, чи слід розглядати цього користувача як активного. "
            "Зніміть цей прапорець замість видалення облікових записів."
        ),
    )
    date_joined = models.DateTimeField("Дата реєстрації", default=timezone.now)
    birth_date = models.DateTimeField("Дата народження", blank=True, null=True)
    photo = models.ImageField("Фото", upload_to="img/profiles", null=True, blank=True)
    role = models.PositiveIntegerField("Роль", choices=ROLE_CHOICES, default=ROLE_CHOICES.SELLER)
    position = models.CharField("Посада", max_length=100, blank=True)
    department = models.CharField("Департамент", max_length=100, blank=True)
    address = models.TextField("Адреса", blank=True)
    bio = models.TextField("Біографія", blank=True, help_text="Короткий опис про себе")
    website = models.URLField("Веб-сайт", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    twitter = models.URLField("Twitter", blank=True)
    facebook = models.URLField("Facebook", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    show_email = models.BooleanField("Показувати email", default=True)
    show_phone = models.BooleanField("Показувати телефон", default=False)
    show_birth_date = models.BooleanField("Показувати дату народження", default=False)
    last_login_date = models.DateTimeField("Останній вхід", null=True, blank=True)
    total_logins = models.PositiveIntegerField("Всього входів", default=0)
    profile_views = models.PositiveIntegerField("Переглядів профілю", default=0)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomerManager()
    def __str__(self):
        return self.email
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    def get_short_name(self):
        return self.first_name
    def get_registration_duration(self):
        return timezone.now() - self.date_joined
    def get_age(self):
        if self.birth_date:
            today = timezone.now().date()
            return (
                today.year
                - self.birth_date.year
                - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            )
        return None
    def get_role_display_uk(self):
        role_names = {
            ROLE_CHOICES.WORKER: "Працівник",
            ROLE_CHOICES.MANAGER: "Менеджер",
            ROLE_CHOICES.SELLER: "Продавець",
        }
        return role_names.get(self.role, "Невідомо")
    def increment_profile_views(self):
        self.profile_views += 1
        self.save(update_fields=["profile_views"])
    def update_last_login(self):
        self.last_login_date = timezone.now()
        self.total_logins += 1
        self.save(update_fields=["last_login_date", "total_logins"])
    def get_last_login_display(self):
        if self.last_login_date:
            return self.last_login_date
        elif self.last_login:
            return self.last_login
        return None
    def get_total_logins_display(self):
        if self.total_logins > 0:
            return self.total_logins
        elif self.last_login_date or self.last_login:
            return 1
        return 0
    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    def save(self, *args, **kwargs):
        if not self.pk:
            self.total_logins = 0
            self.profile_views = 0
        super().save(*args, **kwargs)