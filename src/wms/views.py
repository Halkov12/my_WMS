from collections import defaultdict
from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render


from wms.models import StockOperation, Product, OPERATION_CHOICES, Category


def index(request):
    return render(request, "index.html")


def dashboard_view(request):
    today = datetime.today().date()
    last_7_days = [today - timedelta(days=i) for i in reversed(range(7))]

    active_products_count = Product.objects.filter(is_active=True).count()
    total_quantity = Product.objects.aggregate(total=Sum('quantity'))['total'] or 0

    categories_summary = (
        Category.objects
        .annotate(
            active_products_count=Count('product', filter=Q(product__is_active=True)),
            total_quantity=Sum('product__quantity')
        )
        .filter(
            active_products_count__gt=0,
            total_quantity__gt=0
        )
        .values('name', 'active_products_count', 'total_quantity')
    )

    operations_by_day = (
        StockOperation.objects
        .filter(created_at__date__gte=last_7_days[0])
        .annotate(day=TruncDate('created_at'))
        .values('day', 'operation_type')
        .annotate(count=Count('id'))
    )

    daily_counts = {
        int(OPERATION_CHOICES.RECEIPT): defaultdict(int),
        int(OPERATION_CHOICES.ISSUE): defaultdict(int),
        int(OPERATION_CHOICES.WRITE_OFF): defaultdict(int),
    }

    for entry in operations_by_day:
        op_type = entry['operation_type']
        day = entry['day']
        count = entry['count']
        daily_counts[op_type][day] = count

    receipt_data = [daily_counts[OPERATION_CHOICES.RECEIPT][day] for day in last_7_days]
    issue_data = [daily_counts[OPERATION_CHOICES.ISSUE][day] for day in last_7_days]
    write_off_data = [daily_counts[OPERATION_CHOICES.WRITE_OFF][day] for day in last_7_days]

    date_labels = [day.strftime('%d-%m') for day in last_7_days]

    context = {
        'active_products_count': active_products_count,
        'total_quantity': total_quantity,
        'categories_summary': categories_summary,
        'date_labels': date_labels,
        'receipt_data': receipt_data,
        'issue_data': issue_data,
        'write_off_data': write_off_data,
    }

    return render(request, 'wms/dashboard.html', context)


def product_list_view(request):
    query = request.GET.get('q', '')
    show_active_only = request.GET.get('active') == '1'

    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query)
        )

    if show_active_only:
        products = products.filter(is_active=True)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'show_active_only': show_active_only,
    }
    return render(request, 'wms/products.html', context)