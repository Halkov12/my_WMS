from celery import shared_task

from common.utils.data_generators import (generate_categories,
                                          generate_operations,
                                          generate_products, generate_users)


@shared_task
def generate_users_task(n=5):
    users = generate_users(n)
    return f"Created {len(users)} users"


@shared_task
def generate_categories_task(n=5):
    categories = generate_categories(n)
    return f"Created {len(categories)} categories"


@shared_task
def generate_products_task(n=100):
    categories = generate_categories()
    products = generate_products(n, categories=categories)
    return f"Created {len(products)} products"


@shared_task
def generate_operations_task(n=100):
    products = generate_products()
    operations = generate_operations(n, products=products)
    return f"Created {len(operations)} operations"


@shared_task
def birthday_task():
    return "Happy birthday!"


@shared_task
def tuesday_noon_task():
    return "Tuesday noon task triggered!"


@shared_task
def leap_friday_13_task():
    return "Leap year, Friday 13th, 13th minute!"
