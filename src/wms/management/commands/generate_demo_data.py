import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import ROLE_CHOICES, Customer
from wms.models import (OPERATION_CHOICES, Category, Product, StockOperation,
                        StockOperationItem)

FIRST_NAMES = ["Олександр", "Марія", "Іван", "Олена", "Дмитро"]
LAST_NAMES = ["Шевченко", "Коваленко", "Бондаренко", "Мельник", "Кравченко"]
EMAILS = [
    "alex.shevchenko@example.com",
    "maria.koval@example.com",
    "ivan.bondar@example.com",
    "olena.melnyk@example.com",
    "dmytro.kravchenko@example.com",
]
ROLES = [
    ROLE_CHOICES.MANAGER,
    ROLE_CHOICES.SELLER,
    ROLE_CHOICES.WORKER,
    ROLE_CHOICES.MANAGER,
    ROLE_CHOICES.SELLER,
]

CATEGORY_NAMES = ["Електроніка", "Одяг", "Іграшки", "Канцелярія", "Продукти"]
PRODUCT_NAMES = [
    "Смартфон",
    "Ноутбук",
    "Планшет",
    "Навушники",
    "Монітор",
    "Клавіатура",
    "Миша",
    "Принтер",
    "Флешка",
    "Камера",
    "Футболка",
    "Джинси",
    "Куртка",
    "Сорочка",
    "Плаття",
    "Шорти",
    "Кросівки",
    "Капці",
    "Шкарпетки",
    "Шапка",
    "М'яка іграшка",
    "Конструктор",
    "Пазл",
    "Машинка",
    "Лялька",
    "Настільна гра",
    "Кубик Рубіка",
    "Пластилін",
    "Фломастери",
    "Книга",
    "Зошит",
    "Ручка",
    "Олівець",
    "Лінійка",
    "Гумка",
    "Папка",
    "Щоденник",
    "Клей",
    "Скотч",
    "Маркер",
    "Молоко",
    "Хліб",
    "Сир",
    "Ковбаса",
    "Йогурт",
    "Яблуко",
    "Банан",
    "Картопля",
    "Морква",
    "Помідор",
]
PRODUCT_DESCRIPTIONS = [
    "Високоякісний товар для щоденного використання.",
    "Новинка сезону!",
    "Надійний вибір для всієї родини.",
    "Обмежена серія, не пропустіть!",
    "Гарантія якості від виробника.",
]


class Command(BaseCommand):
    help = "Генерує 5 категорій, 100 товарів, операції і 5 користувачів з різними ролями."

    def handle(self, *args, **kwargs):
        # Создание пользователей
        users = []
        for i in range(5):
            user, created = Customer.objects.get_or_create(
                email=EMAILS[i],
                defaults={
                    "first_name": FIRST_NAMES[i],
                    "last_name": LAST_NAMES[i],
                    "role": ROLES[i],
                },
            )
            if created:
                user.set_password("demo12345")
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"Створено користувачів: {len(users)}"))

        # Создание категорий
        categories = []
        for name in CATEGORY_NAMES:
            cat, _ = Category.objects.get_or_create(name=name)
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f"Створено категорій: {len(categories)}"))

        # Создание товаров
        products = []
        for i in range(1, 101):
            cat = categories[(i - 1) // 20]
            prod_name = random.choice(PRODUCT_NAMES) + f" {i}"
            barcode = str(100000000000 + i)
            prod, _ = Product.objects.get_or_create(
                name=prod_name,
                defaults={
                    "barcode": barcode,
                    "category": cat,
                    "quantity": random.randint(10, 100),
                    "unit": 1,
                    "purchase_price": Decimal(random.uniform(10, 100)).quantize(Decimal("0.01")),
                    "selling_price": Decimal(random.uniform(120, 200)).quantize(Decimal("0.01")),
                    "description": random.choice(PRODUCT_DESCRIPTIONS),
                    "is_active": True,
                },
            )
            products.append(prod)
        self.stdout.write(self.style.SUCCESS(f"Створено товарів: {len(products)}"))

        # Операции (по 2 на товар: приход и выдача)
        reasons = [
            "Планове поповнення складу",
            "Повернення від клієнта",
            "Реалізація товару",
            "Внутрішнє переміщення",
            "Списання зіпсованого товару",
        ]
        for prod in products:
            for op_type in [OPERATION_CHOICES.RECEIPT, OPERATION_CHOICES.ISSUE]:
                op = StockOperation.objects.create(
                    operation_type=op_type,
                    created_by=random.choice(users),
                    reason=random.choice(reasons),
                    created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 60)),
                )
                StockOperationItem.objects.create(operation=op, product=prod, quantity=random.randint(1, 10))
        self.stdout.write(self.style.SUCCESS("Створено операції для товарів."))
