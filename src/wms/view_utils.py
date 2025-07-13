from decimal import Decimal, InvalidOperation
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from wms.models import Product, StockOperation, StockOperationItem, OPERATION_CHOICES
from wms.utils import process_stock_operation
def get_filtered_products(request):
    queryset = Product.objects.all()
    query = request.GET.get("q", "")
    category_id = request.GET.get("category")
    stock_status = request.GET.get("stock_status")
    price_range = request.GET.get("price_range")
    sort = request.GET.get("sort", "name")
    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if stock_status:
        if stock_status == "in_stock":
            queryset = queryset.filter(quantity__gt=0)
        elif stock_status == "low_stock":
            queryset = queryset.filter(quantity__lt=5, quantity__gt=0)
        elif stock_status == "out_of_stock":
            queryset = queryset.filter(quantity=0)
    if price_range:
        if price_range == "0-1000":
            queryset = queryset.filter(selling_price__lte=1000)
        elif price_range == "1000-10000":
            queryset = queryset.filter(selling_price__gt=1000, selling_price__lte=10000)
        elif price_range == "10000-50000":
            queryset = queryset.filter(selling_price__gt=10000, selling_price__lte=50000)
        elif price_range == "50000+":
            queryset = queryset.filter(selling_price__gt=50000)
    if sort == "name":
        queryset = queryset.order_by("name")
    elif sort == "-name":
        queryset = queryset.order_by("-name")
    elif sort == "quantity":
        queryset = queryset.order_by("quantity")
    elif sort == "-quantity":
        queryset = queryset.order_by("-quantity")
    elif sort == "selling_price":
        queryset = queryset.order_by("selling_price")
    elif sort == "-selling_price":
        queryset = queryset.order_by("-selling_price")
    elif sort == "created_at":
        queryset = queryset.order_by("created_at")
    elif sort == "-created_at":
        queryset = queryset.order_by("-created_at")
    else:
        queryset = queryset.order_by("name")
    return queryset
def get_filtered_operations(request):
    queryset = StockOperation.objects.select_related("created_by").prefetch_related("items__product")
    operation_type = request.GET.get("operation_type")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    user_id = request.GET.get("user")
    sort = request.GET.get("sort", "-created_at")
    if operation_type:
        queryset = queryset.filter(operation_type=operation_type)
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
    if user_id:
        queryset = queryset.filter(created_by_id=user_id)
    if sort == "created_at":
        queryset = queryset.order_by("created_at")
    elif sort == "-created_at":
        queryset = queryset.order_by("-created_at")
    elif sort == "operation_type":
        queryset = queryset.order_by("operation_type")
    elif sort == "-operation_type":
        queryset = queryset.order_by("-operation_type")
    else:
        queryset = queryset.order_by("-created_at")
    return queryset
def get_filtered_stock_operations(request, user=None):
    from accounts.models import ROLE_CHOICES
    queryset = StockOperation.objects.all()
    if user and hasattr(user, 'role') and user.role == ROLE_CHOICES.SELLER:
        queryset = queryset.filter(created_by=user)
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    operation_type = request.GET.get("operation_type")
    sort = request.GET.get("sort", "-created_at")
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)
    if operation_type:
        queryset = queryset.filter(operation_type=operation_type)
    if sort == "created_at":
        queryset = queryset.order_by("created_at")
    elif sort == "-created_at":
        queryset = queryset.order_by("-created_at")
    elif sort == "operation_type":
        queryset = queryset.order_by("operation_type")
    elif sort == "-operation_type":
        queryset = queryset.order_by("-operation_type")
    elif sort == "created_by":
        queryset = queryset.order_by("created_by__first_name", "created_by__last_name")
    elif sort == "-created_by":
        queryset = queryset.order_by("-created_by__first_name", "-created_by__last_name")
    else:
        queryset = queryset.order_by("-created_at")
    return queryset
def process_stock_operation_view(request, operation_type, increase=True):
    if request.method == "POST":
        cart_data = request.POST.get("cart", "")
        reason = request.POST.get("reason", "")
        note = request.POST.get("note", "")
        if not cart_data:
            return JsonResponse({"success": False, "message": "Cart is empty"})
        try:
            cart = eval(cart_data)
        except:
            return JsonResponse({"success": False, "message": "Invalid cart data"})
        if not cart:
            return JsonResponse({"success": False, "message": "Cart is empty"})
        success, message, operation = process_stock_operation(
            cart, request.user, operation_type, reason, note, 
            notification_type=operation_type, increase=increase
        )
        if success:
            return JsonResponse({
                "success": True, 
                "message": f"Operation completed successfully. ID: {operation.id}",
                "operation_id": operation.id
            })
        else:
            return JsonResponse({"success": False, "message": message})
    return JsonResponse({"success": False, "message": "Invalid request method"})
def validate_product_quantity(product_id, quantity, increase=False):
    try:
        product = get_object_or_404(Product, id=product_id)
        qty = Decimal(quantity)
        if not increase and product.quantity < qty:
            return False, f"Insufficient stock. Available: {product.quantity}"
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid quantity"
    except Product.DoesNotExist:
        return False, "Product not found"
def get_dashboard_context():
    from datetime import datetime, timedelta
    from django.db.models import Count, F, Q, Sum
    from django.db.models.functions import TruncDate
    import json
    from wms.models import Category, Notification
    from wms.utils import get_products_stats, get_categories_with_stats, get_low_stock_products, get_recent_operations
    today = datetime.today().date()
    last_7_days = [today - timedelta(days=i) for i in reversed(range(7))]
    products_stats = get_products_stats()
    context = {
        "active_products_count": products_stats["count"] or 0,
        "total_quantity": products_stats["total_quantity"] or 0,
        "total_products_count": products_stats["count"] or 0,
        "total_stock_value": float(products_stats["total_value"] or 0),
    }
    usd_rate = 40.0
    context["total_stock_value_usd"] = context["total_stock_value"] / usd_rate if usd_rate else 0
    context["categories_data"] = get_categories_with_stats().values("name", "active_products", "total_quantity")
    category_stock_data = (
        Category.objects.annotate(total_quantity=Sum("product__quantity", filter=Q(product__is_active=True)))
        .filter(total_quantity__gt=0)
        .values("name", "total_quantity")
        .order_by("-total_quantity")
    )
    context["category_chart_labels"] = json.dumps([cat["name"] for cat in category_stock_data])
    context["category_chart_data"] = json.dumps([float(cat["total_quantity"]) for cat in category_stock_data])
    top_products_by_quantity = (
        Product.objects.filter(is_active=True, quantity__gt=0).order_by("-quantity").values("name", "quantity")[:5]
    )
    context["top_products_labels"] = json.dumps([prod["name"] for prod in top_products_by_quantity])
    context["top_products_data"] = json.dumps([float(prod["quantity"]) for prod in top_products_by_quantity])
    operations_by_day = (
        StockOperation.objects.filter(created_at__date__gte=last_7_days[0])
        .annotate(day=TruncDate("created_at"))
        .values("day", "operation_type")
        .annotate(count=Count("id"))
    )
    from collections import defaultdict
    daily_counts = {
        1: defaultdict(int),
        2: defaultdict(int),
        3: defaultdict(int),
    }
    for entry in operations_by_day:
        daily_counts[entry["operation_type"]][entry["day"]] = entry["count"]
    date_labels = [day.strftime("%d-%m") for day in last_7_days]
    context["date_labels"] = json.dumps(date_labels)
    context["receipt_data"] = json.dumps([daily_counts[1][day] for day in last_7_days])
    context["issue_data"] = json.dumps([daily_counts[2][day] for day in last_7_days])
    context["write_off_data"] = json.dumps([daily_counts[3][day] for day in last_7_days])
    context["recent_operations"] = [
        {
            "date": op.operation.created_at,
            "type": op.operation.operation_type,
            "product": op.product.name,
            "quantity": op.quantity,
        }
        for op in get_recent_operations(6)
    ]
    context["low_stock_products"] = get_low_stock_products(10, 10)
    context["notifications"] = Notification.objects.all()[:5]
    return context 
def handle_operation_cart(request, operation_type, cart_key, success_message, error_message):
    cart = request.session.get(cart_key, [])
    if "add_product" in request.POST:
        product_id = request.POST.get("product_id") or request.POST.get("product")
        quantity_str = request.POST.get("quantity", "0")
        if not product_id:
            return False, "Please select a product from the list."
        try:
            product = Product.objects.get(id=product_id)
            quantity = Decimal(quantity_str)
            if quantity <= 0:
                raise InvalidOperation
        except (Product.DoesNotExist, InvalidOperation):
            return False, "Invalid quantity or product."
        if operation_type in [OPERATION_CHOICES.ISSUE, OPERATION_CHOICES.WRITE_OFF]:
            if product.quantity < quantity:
                return False, f"Insufficient stock. Available: {product.quantity}"
            cart_quantity = sum(Decimal(item["quantity"]) for item in cart if item["product_id"] == product.id)
            if product.quantity < (cart_quantity + quantity):
                return False, f"Insufficient stock. Available: {product.quantity}"
        for item in cart:
            if item["product_id"] == product.id:
                item["quantity"] = str(Decimal(item["quantity"]) + quantity)
                break
        else:
            cart.append({
                "product_id": product.id, 
                "quantity": str(quantity),
                "product_name": product.name,
                "unit": product.get_unit_display(),
            })
        request.session[cart_key] = cart
        return True, f"Product '{product.name}' added."
    elif "remove_product" in request.POST:
        product_id = int(request.POST.get("product_id"))
        cart = [item for item in cart if item["product_id"] != product_id]
        request.session[cart_key] = cart
        return True, "Product removed from list."
    elif "clear_cart" in request.POST:
        request.session[cart_key] = []
        return True, "List cleared."
    elif "save_operation" in request.POST:
        if not cart:
            return False, "List is empty."
        reason = request.POST.get("reason", "")
        note = request.POST.get("note", "")
        success, message, operation = process_stock_operation(
            cart, request.user, operation_type, reason, note,
            notification_type=operation_type, increase=(operation_type == OPERATION_CHOICES.RECEIPT)
        )
        if success:
            request.session[cart_key] = []
            return True, success_message
        else:
            return False, message
    return False, "Невідома операція."
def get_operation_context(request, cart_key, template_context):
    cart = request.session.get(cart_key, [])
    total_items = sum(Decimal(item["quantity"]) for item in cart)
    context = {
        **template_context,
        "cart": cart,
        "total_items": total_items,
        "products": Product.objects.filter(is_active=True).order_by("name"),
    }
    return context 
def get_filtered_products_for_report(request):
    queryset = Product.objects.all().order_by("-created_at")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)
    return queryset