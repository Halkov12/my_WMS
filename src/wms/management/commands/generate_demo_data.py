from django.core.management.base import BaseCommand
from wms.models import Category, Product, StockOperation, StockOperationItem, OPERATION_CHOICES
from accounts.models import Customer, ROLE_CHOICES
from django.utils.crypto import get_random_string
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Генерирует 5 категорий, 100 товаров, операции и 5 пользователей с разными ролями.'

    def handle(self, *args, **kwargs):
        # Создание пользователей
        roles = [ROLE_CHOICES.MANAGER, ROLE_CHOICES.SELLER, ROLE_CHOICES.WORKER, 4, 5]
        users = []
        for i, role in enumerate(roles, 1):
            user, created = Customer.objects.get_or_create(
                email=f'user{i}@demo.local',
                defaults={
                    'first_name': f'User{i}',
                    'last_name': f'Demo',
                    'role': role,
                }
            )
            if created:
                user.set_password('demo12345')
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS('Создано пользователей: %d' % len(users)))

        # Создание категорий
        categories = []
        for i in range(1, 6):
            cat, _ = Category.objects.get_or_create(name=f'Категорія {i}')
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS('Создано категорий: %d' % len(categories)))

        # Создание товаров
        products = []
        for i in range(1, 101):
            cat = categories[(i-1)//20]
            barcode = str(100000000000 + i)
            prod, _ = Product.objects.get_or_create(
                name=f'Товар {i}',
                defaults={
                    'barcode': barcode,
                    'category': cat,
                    'quantity': random.randint(10, 100),
                    'unit': 1,
                    'purchase_price': Decimal(random.uniform(10, 100)).quantize(Decimal('0.01')),
                    'selling_price': Decimal(random.uniform(120, 200)).quantize(Decimal('0.01')),
                    'description': f'Опис для товару {i}',
                    'is_active': True,
                }
            )
            products.append(prod)
        self.stdout.write(self.style.SUCCESS('Создано товаров: %d' % len(products)))

        # Операции (по 2 на товар: приход и выдача)
        for prod in products:
            for op_type in [OPERATION_CHOICES.RECEIPT, OPERATION_CHOICES.ISSUE]:
                op = StockOperation.objects.create(
                    operation_type=op_type,
                    created_by=random.choice(users),
                    reason=f'Тестова операція {op_type}',
                )
                StockOperationItem.objects.create(
                    operation=op,
                    product=prod,
                    quantity=random.randint(1, 10)
                )
        self.stdout.write(self.style.SUCCESS('Создано операций для товаров.')) 