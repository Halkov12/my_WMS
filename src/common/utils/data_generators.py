import random

from django.contrib.auth import get_user_model
from faker import Faker

from wms.models import (OPERATION_CHOICES, Category, Product, StockOperation,
                        StockOperationItem)

fake = Faker("uk_UA")
User = get_user_model()


def generate_users(n=5):
    users = []
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        user = User.objects.create_user(email=email, password="Test1234", first_name=first_name, last_name=last_name)
        users.append(user)
    return users


def generate_categories(n=5):
    category_names = ["Електроніка", "Одяг", "Іграшки", "Канцелярія", "Продукти"]
    categories = []
    for i in range(n):
        name = category_names[i] if i < len(category_names) else fake.word().capitalize()
        category, _ = Category.objects.get_or_create(name=name)
        categories.append(category)
    return categories


def generate_products(n=100, categories=None):
    if categories is None:
        categories = list(Category.objects.all())
    products = []
    for _ in range(n):
        name = fake.unique.word().capitalize() + " " + fake.word().capitalize()
        description = fake.sentence(nb_words=8)
        price = round(random.uniform(10, 10000), 2)
        category = random.choice(categories)
        quantity = round(random.uniform(1, 100), 2)
        barcode = ""
        for attempt in range(10):
            try:
                barcode = fake.unique.ean13()
            except Exception:
                try:
                    barcode = fake.unique.numerify(text="#############")
                except Exception:
                    barcode = ""
            if not barcode or barcode == "":
                barcode = str(random.randint(10**12, 10**13 - 1))
            if not Product.objects.filter(barcode=barcode).exists():
                break
            else:
                barcode = ""
        if not barcode:
            raise Exception("ПОМИЛКА: Не вдалося згенерувати унікальний штрихкод за 10 спроб!")
        product = Product.objects.create(
            name=name,
            description=description,
            selling_price=price,
            purchase_price=price,
            category=category,
            barcode=barcode,
            quantity=quantity,
        )
        products.append(product)
    return products


def generate_operations(n=100, products=None, user=None):
    if products is None:
        products = list(Product.objects.all())
    if not products:
        return []
    if user is None:
        user = User.objects.filter(is_staff=True).first() or User.objects.first()
    operations = []
    operation_types = [
        OPERATION_CHOICES.RECEIPT,
        OPERATION_CHOICES.ISSUE,
        OPERATION_CHOICES.WRITE_OFF,
    ]
    for _ in range(n):
        op_type = random.choice(operation_types)
        operation = StockOperation.objects.create(
            operation_type=op_type,
            created_by=user,
            reason=fake.sentence(nb_words=4),
            note=fake.sentence(nb_words=8),
        )
        for _ in range(random.randint(1, 3)):
            product = random.choice(products)
            quantity = random.randint(1, 50)
            StockOperationItem.objects.create(operation=operation, product=product, quantity=quantity)
        operations.append(operation)
    return operations
