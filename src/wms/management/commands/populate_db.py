from django.core.management.base import BaseCommand
from django.db import transaction
from wms.models import Category, Product, StockOperation, StockOperationItem, OPERATION_CHOICES, UNIT_CHOICES
from decimal import Decimal
from faker import Faker
import random
from django.utils import timezone
from datetime import timedelta

fake = Faker('ru_RU')

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing database...')
        self._clear_db()
        
        self.stdout.write('Creating categories...')
        categories = self._create_categories()
        
        self.stdout.write('Creating products...')
        products = self._create_products(categories)
        
        self.stdout.write('Creating stock operations...')
        self._create_stock_operations(products)
        
        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))

    def _clear_db(self):
        with transaction.atomic():
            StockOperationItem.objects.all().delete()
            StockOperation.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

    def _create_categories(self):
        categories = [
            "Электроника",
            "Бытовая техника",
            "Инструменты",
            "Мебель",
            "Одежда",
            "Обувь",
            "Продукты питания",
            "Напитки",
            "Канцтовары",
            "Автозапчасти"
        ]
        
        created_categories = []
        for cat_name in categories:
            category = Category.objects.create(
                name=cat_name
            )
            created_categories.append(category)
        
        return created_categories

    def _create_products(self, categories):
        products = []
        units = [UNIT_CHOICES.PIECES, UNIT_CHOICES.KILOGRAMS, UNIT_CHOICES.LITER, UNIT_CHOICES.GRAM]
        
        # Примеры продуктов для каждой категории
        category_products = {
            "Электроника": ["Смартфон", "Ноутбук", "Планшет", "Наушники", "Телевизор", "Монитор", "Клавиатура", "Мышь", "Принтер", "Сканер"],
            "Бытовая техника": ["Холодильник", "Стиральная машина", "Микроволновка", "Пылесос", "Утюг", "Чайник", "Кофеварка", "Блендер", "Тостер", "Мультиварка"],
            "Инструменты": ["Дрель", "Перфоратор", "Отвертка", "Молоток", "Пила", "Шуруповерт", "Плоскогубцы", "Рулетка", "Уровень", "Стамеска"],
            "Мебель": ["Стол", "Стул", "Диван", "Шкаф", "Кровать", "Тумба", "Комод", "Полка", "Кресло", "Вешалка"],
            "Одежда": ["Футболка", "Джинсы", "Куртка", "Рубашка", "Платье", "Свитер", "Брюки", "Юбка", "Пальто", "Шорты"],
            "Обувь": ["Кроссовки", "Ботинки", "Туфли", "Сандалии", "Сапоги", "Кеды", "Мокасины", "Тапочки", "Босоножки", "Шлепанцы"],
            "Продукты питания": ["Хлеб", "Молоко", "Сыр", "Масло", "Яйца", "Мясо", "Рыба", "Овощи", "Фрукты", "Крупы"],
            "Напитки": ["Вода", "Сок", "Чай", "Кофе", "Газировка", "Энергетик", "Квас", "Морс", "Компот", "Лимонад"],
            "Канцтовары": ["Ручка", "Карандаш", "Тетрадь", "Бумага", "Папка", "Степлер", "Ножницы", "Линейка", "Маркер", "Клей"],
            "Автозапчасти": ["Фильтр", "Масло", "Свечи", "Тормозные колодки", "Аккумулятор", "Шины", "Диски", "Фары", "Зеркала", "Щетки"]
        }
        
        # Создаем 100 продуктов
        for _ in range(100):
            category = random.choice(categories)
            unit = random.choice(units)
            
            # Выбираем базовое название из соответствующей категории
            base_name = random.choice(category_products[category.name])
            # Добавляем бренд или модификатор
            brand = fake.company()
            name = f"{brand} {base_name} {fake.word()}"
            
            purchase_price = round(random.uniform(10, 1000), 2)
            selling_price = round(purchase_price * random.uniform(1.1, 1.5), 2)
            
            product = Product.objects.create(
                name=name,
                barcode=fake.ean13(),
                purchase_price=purchase_price,
                selling_price=selling_price,
                unit=unit,
                quantity=0,  # Начальное количество
                category=category,
                is_active=random.choice([True, True, True, False])  # 75% активных
            )
            products.append(product)
        
        return products

    def _create_stock_operations(self, products):
        # Создаем операции за последние 30 дней
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Создаем 200 операций
        for _ in range(200):
            operation_type = random.choice([
                OPERATION_CHOICES.RECEIPT,
                OPERATION_CHOICES.RECEIPT,
                OPERATION_CHOICES.ISSUE,
                OPERATION_CHOICES.WRITE_OFF
            ])  # Больше приходов для наличия товара
            
            operation_date = fake.date_time_between(
                start_date=start_date,
                end_date=end_date,
                tzinfo=timezone.get_current_timezone()
            )
            
            with transaction.atomic():
                operation = StockOperation.objects.create(
                    operation_type=operation_type,
                    reason=fake.sentence(),
                    note=fake.text(max_nb_chars=100),
                    created_at=operation_date
                )
                
                # Добавляем 1-5 товаров в операцию
                for _ in range(random.randint(1, 5)):
                    product = random.choice(products)
                    quantity = round(random.uniform(1, 50), 2)
                    
                    if operation_type == OPERATION_CHOICES.RECEIPT:
                        product.quantity += quantity
                    elif operation_type in [OPERATION_CHOICES.ISSUE, OPERATION_CHOICES.WRITE_OFF]:
                        # Проверяем, достаточно ли товара
                        if product.quantity >= quantity:
                            product.quantity -= quantity
                        else:
                            quantity = product.quantity
                            product.quantity = 0
                    
                    if quantity > 0:  # Создаем запись только если есть что записать
                        StockOperationItem.objects.create(
                            operation=operation,
                            product=product,
                            quantity=quantity
                        )
                        product.save() 