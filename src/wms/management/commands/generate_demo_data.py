from django.core.management.base import BaseCommand
from wms.models import Category, Product, StockOperation, StockOperationItem, OPERATION_CHOICES
import random
from django.contrib.auth import get_user_model
from faker import Faker

PRODUCT_NAMES = [
    "iPhone 14 Pro", "Samsung Galaxy S23", "Xiaomi Mi 13", "MacBook Air M2", "Dell XPS 13",
    "Sony WH-1000XM5", "Apple Watch Series 8", "Canon EOS R6", "GoPro Hero 11", "Nintendo Switch OLED",
    "Dyson V15 Detect", "Bose QuietComfort 45", "Logitech MX Master 3S", "Kindle Paperwhite",
    "Philips Hue Starter Kit", "Samsung QLED TV", "Apple iPad Pro", "Lenovo ThinkPad X1", "JBL Charge 5",
    "Garmin Fenix 7", "Razer DeathAdder V2", "Google Pixel 7", "OnePlus 11 Pro", "Asus ROG Phone 6",
    "HP Envy 15", "Microsoft Surface Pro 9", "DJI Mini 3 Pro", "Fitbit Versa 4", "Canon Pixma G6020",
    "Brother HL-L2350DW", "TP-Link Archer AX50", "Xiaomi Roborock S7", "Samsung Galaxy Tab S8",
    "Apple AirPods Pro 2", "Sony PlayStation 5", "Xbox Series X", "LG UltraFine 5K", "BenQ GW2780",
    "Acer Predator Helios 300", "MSI GeForce RTX 4070", "Kingston NV2 SSD", "WD My Passport 2TB",
    "SanDisk Extreme Pro", "Seagate IronWolf 8TB", "Corsair Vengeance 32GB", "G.Skill Trident Z5",
    "Asus TUF Gaming B660M", "Gigabyte Z690 Aorus", "Intel Core i9-13900K", "AMD Ryzen 9 7950X"
]

CATEGORY_NAMES = [
    "Смартфони",
    "Ноутбуки",
    "Аудіотехніка",
    "Побутова техніка",
    "Гаджети"
]

class Command(BaseCommand):
    help = "Генерує 5 категорій, по 20 продуктів з реальними назвами і штрихкодами, і до кожного продукту по 2-3 операції."

    def handle(self, *args, **options):
        # Очищаем только связанные с товарами и операциями данные, не трогая пользователей
        from wms.models import ChangeLog, StockOperationItem
        ChangeLog.objects.all().delete()
        StockOperationItem.objects.all().delete()
        StockOperation.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        fake = Faker("uk_UA")

        categories = []
        for name in CATEGORY_NAMES:
            cat = Category.objects.create(name=name)
            categories.append(cat)

        products = []
        used_barcodes = set()
        for cat in categories:
            for _ in range(20):
                name = random.choice(PRODUCT_NAMES)
                # Генерируем уникальный штрихкод (13 цифр)
                while True:
                    barcode = str(random.randint(10**12, 10**13-1))
                    if barcode not in used_barcodes:
                        used_barcodes.add(barcode)
                        break
                selling_price = random.randint(1000, 100000)
                purchase_price = random.randint(500, selling_price)
                quantity = random.randint(1, 200)
                description = fake.sentence(nb_words=8)
                prod = Product.objects.create(
                    name=name,
                    barcode=barcode,
                    selling_price=selling_price,
                    purchase_price=purchase_price,
                    quantity=quantity,
                    category=cat,
                    description=description
                )
                products.append(prod)

        User = get_user_model()
        user = User.objects.first()

        operations = []
        op_types = [OPERATION_CHOICES.RECEIPT, OPERATION_CHOICES.ISSUE, OPERATION_CHOICES.WRITE_OFF]
        for prod in products:
            for _ in range(random.randint(2, 3)):
                op_type = random.choice(op_types)
                operation = StockOperation.objects.create(
                    operation_type=op_type,
                    created_by=user,
                    reason=f"Демо операція {op_type.label}",
                    note="Автоматично згенеровано"
                )
                StockOperationItem.objects.create(
                    operation=operation,
                    product=prod,
                    quantity=random.randint(1, 50)
                )
                operations.append(operation)

        self.stdout.write(self.style.SUCCESS(
            f"Створено {len(categories)} категорій, {len(products)} продуктів, {len(operations)} операцій."
        )) 