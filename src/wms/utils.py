import os
from io import BytesIO
from pathlib import Path
from django.core.cache import cache
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from .models import (Category, Notification, Product, StockOperation,
                     StockOperationItem)
def get_active_products_queryset():
    return Product.objects.filter(is_active=True)
def get_products_with_category():
    return get_active_products_queryset().select_related("category")
def check_barcode_exists(barcode):
    cache_key = f"barcode_exists_{barcode}"
    result = cache.get(cache_key)
    if result is None:
        result = Product.objects.filter(barcode=barcode).exists()
        cache.set(cache_key, result, 300)
    return result
def get_products_stats():
    cache_key = "products_stats"
    stats = cache.get(cache_key)
    if stats is None:
        stats = Product.objects.filter(is_active=True).aggregate(
            count=Count("id"), total_quantity=Sum("quantity"), total_value=Sum(F("purchase_price") * F("quantity"))
        )
        cache.set(cache_key, stats, 600)
    return stats
def get_categories_with_stats():
    return Category.objects.annotate(
        active_products=Count("product", filter=Q(product__is_active=True)),
        total_quantity=Sum("product__quantity"),
    ).filter(active_products__gt=0, total_quantity__gt=0)
def get_low_stock_products(threshold=10, limit=10):
    return get_active_products_queryset().filter(quantity__lt=threshold).order_by("quantity")[:limit]
def get_recent_operations(limit=10):
    return StockOperationItem.objects.select_related("operation", "product").order_by("-operation__created_at")[:limit]
def export_table_to_pdf(data, title, col_widths, filename):
    font_path = str(Path(__file__).resolve().parent.parent / "static" / "fonts" / "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=20)
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleN.fontName = "DejaVuSans"
    styleH = styles["Heading2"]
    styleH.fontName = "DejaVuSans"
    table = Table(data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )
    elements = [Paragraph(title, styleH), Spacer(1, 12), table]
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response.write(pdf)
    return response
def process_stock_operation(cart, user, operation_type, reason="", note="", notification_type=None, increase=True):
    from decimal import Decimal
    from django.db import transaction
    from django.shortcuts import get_object_or_404
    with transaction.atomic():
        operation = StockOperation.objects.create(
            operation_type=operation_type,
            created_by=user,
            reason=reason,
            note=note,
        )
        for item in cart:
            product = get_object_or_404(Product, id=item["product_id"])
            quantity = Decimal(item["quantity"])
            if not increase and product.quantity < quantity:
                return False, f"Недостатньо товару на складі. Доступно: {product.quantity}", None
            StockOperationItem.objects.create(operation=operation, product=product, quantity=quantity)
            if increase:
                product.quantity += quantity
            else:
                product.quantity -= quantity
            product.save()
        items = StockOperationItem.objects.filter(operation=operation)
        for item in items:
            qty = int(item.quantity) if item.quantity == int(item.quantity) else f"{item.quantity:.2f}"
            Notification.objects.create(
                type=notification_type,
                message=f"{operation.get_operation_type_display()}: {item.product.name} — {qty} {item.product.get_unit_display()}",
                user=user,
            )
    return True, None, operation