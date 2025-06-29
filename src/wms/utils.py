from django.db.models import Q, Sum, Count, F
from django.core.cache import cache
from .models import Product, Category, StockOperation, StockOperationItem


def get_active_products_queryset():
    """Возвращает базовый queryset для активных товаров"""
    return Product.objects.filter(is_active=True)


def get_products_with_category():
    """Возвращает товары с предзагруженными категориями"""
    return get_active_products_queryset().select_related('category')


def check_barcode_exists(barcode):
    """Проверяет существование штрихкода с кэшированием"""
    cache_key = f'barcode_exists_{barcode}'
    result = cache.get(cache_key)
    
    if result is None:
        result = Product.objects.filter(barcode=barcode).exists()
        cache.set(cache_key, result, 300)  # кэш на 5 минут
    
    return result


def get_products_stats():
    """Возвращает статистику по товарам с кэшированием"""
    cache_key = 'products_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = Product.objects.filter(is_active=True).aggregate(
            count=Count('id'),
            total_quantity=Sum('quantity'),
            total_value=Sum(F('purchase_price') * F('quantity'))
        )
        cache.set(cache_key, stats, 600)  # кэш на 10 минут
    
    return stats


def get_categories_with_stats():
    """Возвращает категории со статистикой"""
    return Category.objects.annotate(
        active_products=Count("product", filter=Q(product__is_active=True)),
        total_quantity=Sum("product__quantity"),
    ).filter(active_products__gt=0, total_quantity__gt=0)


def get_low_stock_products(threshold=10, limit=10):
    """Возвращает товары с низким остатком"""
    return get_active_products_queryset().filter(
        quantity__lt=threshold
    ).order_by('quantity')[:limit]


def get_recent_operations(limit=10):
    """Возвращает последние операции с предзагруженными связями"""
    return StockOperationItem.objects.select_related(
        'operation', 'product'
    ).order_by('-operation__created_at')[:limit] 