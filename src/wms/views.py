from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

import openpyxl
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum, F
from django.db.models.functions import TruncDate
from django.http import HttpResponse, HttpResponseForbidden, FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import io
import csv
import barcode
from barcode.writer import ImageWriter
import json

from wms.forms import AddProductForm, ProductCreateForm
from wms.models import (OPERATION_CHOICES, Category, ChangeLog, Product,
                        StockOperation, StockOperationItem)
from accounts.models import ROLE_CHOICES


class IndexView(TemplateView):
    template_name = "index.html"


# Миксин для проверки роли
class RoleRequiredMixin:
    allowed_roles = []
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in self.allowed_roles:
            return HttpResponseForbidden("Нет доступа")
        return super().dispatch(request, *args, **kwargs)


# Дашборд и отчёты — только для MANAGER
@method_decorator(login_required, name='dispatch')
class DashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    template_name = "wms/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today().date()
        last_7_days = [today - timedelta(days=i) for i in reversed(range(7))]

        context["active_products_count"] = Product.objects.filter(is_active=True).count()
        context["total_quantity"] = Product.objects.aggregate(total=Sum("quantity"))["total"] or 0
        context["total_products_count"] = Product.objects.filter(is_active=True).count()
        context["total_stock_value"] = float(Product.objects.filter(is_active=True).aggregate(
            total=Sum(F("purchase_price") * F("quantity"))
        )["total"] or 0)

        context["categories_summary"] = (
            Category.objects.annotate(
                active_products_count=Count("product", filter=Q(product__is_active=True)),
                total_quantity=Sum("product__quantity"),
            )
            .filter(active_products_count__gt=0, total_quantity__gt=0)
            .values("name", "active_products_count", "total_quantity")
        )

        operations_by_day = (
            StockOperation.objects.filter(created_at__date__gte=last_7_days[0])
            .annotate(day=TruncDate("created_at"))
            .values("day", "operation_type")
            .annotate(count=Count("id"))
        )

        daily_counts = {
            int(OPERATION_CHOICES.RECEIPT): defaultdict(int),
            int(OPERATION_CHOICES.ISSUE): defaultdict(int),
            int(OPERATION_CHOICES.WRITE_OFF): defaultdict(int),
        }

        for entry in operations_by_day:
            daily_counts[entry["operation_type"]][entry["day"]] = entry["count"]

        date_labels = [day.strftime("%d-%m") for day in last_7_days]
        receipt_data = [daily_counts[OPERATION_CHOICES.RECEIPT][day] for day in last_7_days]
        issue_data = [daily_counts[OPERATION_CHOICES.ISSUE][day] for day in last_7_days]
        write_off_data = [daily_counts[OPERATION_CHOICES.WRITE_OFF][day] for day in last_7_days]

        context["date_labels"] = json.dumps(date_labels)
        context["receipt_data"] = json.dumps(receipt_data)
        context["issue_data"] = json.dumps(issue_data)
        context["write_off_data"] = json.dumps(write_off_data)

        # Новое: последние операции (10 штук)
        recent_ops = StockOperationItem.objects.select_related('operation', 'product').order_by('-operation__created_at')[:10]
        context['recent_operations'] = [
            {
                'date': op.operation.created_at,
                'type': op.operation.get_operation_type_display().lower(),
                'product': op.product.name,
                'quantity': op.quantity,
            }
            for op in recent_ops
        ]

        # Новое: товары с низким остатком (например, меньше 10)
        context['low_stock_products'] = Product.objects.filter(quantity__lt=10, is_active=True).order_by('quantity')[:10]

        return context


# Просмотр товаров и операций — все роли
@method_decorator(login_required, name='dispatch')
class ProductListView(RoleRequiredMixin, ListView):
    allowed_roles = [ROLE_CHOICES.MANAGER, ROLE_CHOICES.SELLER, ROLE_CHOICES.WORKER]
    model = Product
    template_name = "wms/products.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.all()
        query = self.request.GET.get("q", "")
        category_id = self.request.GET.get("category")

        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(barcode__icontains=query))
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        category_id = self.request.GET.get("category")

        total_purchase = 0
        total_selling = 0
        total_quantity = 0

        for p in context["products"]:
            if p.purchase_price:
                total_purchase += p.purchase_price.amount
            if p.selling_price:
                total_selling += p.selling_price.amount
            total_quantity += p.quantity

        context.update(
            {
                "query": query,
                "category_id": category_id,
                "total_purchase": total_purchase,
                "total_selling": total_selling,
                "total_quantity": total_quantity,
                "categories": Category.objects.order_by("name"),
            }
        )

        return context


# Приёмка, создание/редактирование товаров — только MANAGER
@method_decorator(login_required, name='dispatch')
class ReceiptView(RoleRequiredMixin, View):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    template_name = "wms/receipt_list.html"

    def get(self, request):
        if "receipt_cart" not in request.session:
            request.session["receipt_cart"] = []

        receipt_cart = request.session["receipt_cart"]
        add_form = AddProductForm()
        create_form = ProductCreateForm()

        products_in_cart = []
        for item in receipt_cart:
            try:
                product = Product.objects.get(id=item["product_id"])
                quantity = Decimal(item["quantity"])
                products_in_cart.append({"product": product, "quantity": quantity})
            except Product.DoesNotExist:
                continue

        search_query = request.GET.get("search", "")
        products = Product.objects.all()
        if search_query:
            products = products.filter(Q(name__icontains=search_query) | Q(barcode__icontains=search_query))

        context = {
            "products_in_cart": products_in_cart,
            "add_product_form": add_form,
            "create_product_form": create_form,
            "products": products,
            "search_query": search_query,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        receipt_cart = request.session.get("receipt_cart", [])

        if "add_product" in request.POST:
            product_id = request.POST.get("product_id")
            quantity_str = request.POST.get("quantity", "0")

            if not product_id:
                messages.error(request, "Будь ласка, оберіть товар зі списку.")
                return redirect("wms:receipt_list")

            try:
                product = Product.objects.get(id=product_id)
                quantity = Decimal(quantity_str)
                if quantity <= 0:
                    raise InvalidOperation
            except (Product.DoesNotExist, InvalidOperation):
                messages.error(request, "Невірна кількість або товар.")
                return redirect("wms:receipt_list")

            for item in receipt_cart:
                if item["product_id"] == product.id:
                    item["quantity"] = str(Decimal(item["quantity"]) + quantity)
                    break
            else:
                receipt_cart.append({"product_id": product.id, "quantity": str(quantity)})

            request.session["receipt_cart"] = receipt_cart
            messages.success(request, f"Товар '{product.name}' додано.")
            return redirect("wms:receipt_list")

        elif "create_product" in request.POST:
            form = ProductCreateForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("wms:receipt_list")

        elif "clear_cart" in request.POST:
            request.session["receipt_cart"] = []
            messages.info(request, "Список очищено.")
            return redirect("wms:receipt_list")

        elif "save_receipt" in request.POST:
            if receipt_cart:
                with transaction.atomic():
                    operation = StockOperation.objects.create(
                        operation_type=OPERATION_CHOICES.RECEIPT,
                        created_by=request.user,
                        reason=request.POST.get("reason", ""),
                    )
                    for item in receipt_cart:
                        product = get_object_or_404(Product, id=item["product_id"])
                        quantity = Decimal(item["quantity"])
                        StockOperationItem.objects.create(operation=operation, product=product, quantity=quantity)
                        product.quantity += quantity
                        product.save()

                request.session["receipt_cart"] = []
                messages.success(request, "Прийом товарів збережено.")
                return redirect("wms:receipt_list")
            else:
                messages.warning(request, "Список порожній.")
                return redirect("wms:receipt_list")

        return self.get(request)


# Приёмка, создание/редактирование товаров — только MANAGER
@method_decorator(login_required, name='dispatch')
class ProductCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    model = Product
    form_class = ProductCreateForm
    template_name = "wms/product_create.html"
    success_url = reverse_lazy("wms:receipt_list")


# Отчёты — только для MANAGER
@method_decorator(login_required, name='dispatch')
class ReportListView(RoleRequiredMixin, TemplateView):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    template_name = "wms/reports/report_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reports"] = [
            {"url": "wms:product_report", "title": "Звіт по товарам"},
            {"url": "wms:stock_report", "title": "Звіт по операціях на складі"},
            {"url": "wms:changelog_report", "title": "Звіт по змінах"},
        ]
        return context


@method_decorator(login_required, name='dispatch')
class ProductReportView(RoleRequiredMixin, ListView):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    model = Product
    template_name = "wms/reports/product_report.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created_at")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        return context

    def render_to_response(self, context, **response_kwargs):
        export = self.request.GET.get("export")
        queryset = self.get_queryset()

        if export == "excel":
            return self.export_to_excel(queryset)
        elif export == "pdf":
            return self.export_to_pdf(queryset)
        return super().render_to_response(context, **response_kwargs)

    def export_to_excel(self, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Products"

        ws.append(["Назва", "Категорія", "Ціна", "Кількість", "Дата створення"])

        for p in queryset:
            ws.append(
                [
                    p.name,
                    p.category.name if p.category else "-",
                    str(p.selling_price),
                    float(p.quantity),
                    p.created_at.strftime("%Y-%m-%d") if p.created_at else "",
                ]
            )

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=products_report.xlsx"
        wb.save(response)
        return response

    def export_to_pdf(self, queryset):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=products_report.pdf"

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 12)
        y = 800
        p.drawString(100, y, "Звіт по товарах")
        y -= 30
        for product in queryset:
            line = (
                f"{product.name} | {product.category.name if product.category else '-'} | {product.selling_price} "
                f"| {product.quantity}"
            )
            p.drawString(50, y, line)
            y -= 20
            if y < 100:
                p.showPage()
                y = 800

        p.save()
        return response


@method_decorator(login_required, name='dispatch')
class StockOperationReportView(RoleRequiredMixin, ListView):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    model = StockOperation
    template_name = "wms/reports/stock_operation_report.html"
    context_object_name = "operations"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-created_at")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        operation_type = self.request.GET.get("operation_type")

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["operation_type"] = self.request.GET.get("operation_type", "")
        context["operation_choices"] = StockOperation._meta.get_field("operation_type").choices
        return context

    def render_to_response(self, context, **response_kwargs):
        export = self.request.GET.get("export")
        queryset = self.get_queryset()

        if export == "excel":
            return self.export_to_excel(queryset)
        elif export == "pdf":
            return self.export_to_pdf(queryset)

        return super().render_to_response(context, **response_kwargs)

    def export_to_excel(self, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Stock Operations"

        ws.append(["Тип операції", "Користувач", "Причина", "Примітка", "Товари", "Дата"])

        for op in queryset:
            items_str = "; ".join([f"{item.product.name} ({item.quantity})" for item in op.items.all()])
            ws.append(
                [
                    op.get_operation_type_display(),
                    op.created_by.get_full_name() if op.created_by else "-",
                    op.reason,
                    op.note,
                    items_str,
                    op.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=stock_operations_report.xlsx"
        wb.save(response)
        return response

    def export_to_pdf(self, queryset):
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=stock_operations_report.pdf"

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 12)
        y = 800
        p.drawString(50, y, "Звіт по операціях на складі")
        y -= 30

        for op in queryset:
            items_str = ", ".join([f"{item.product.name}({item.quantity})" for item in op.items.all()])
            line = (
                f"{op.get_operation_type_display()} | {op.created_by.get_full_name() if op.created_by else '-'} |"
                f" {op.reason} | {items_str} | {op.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            p.drawString(20, y, line)
            y -= 20
            if y < 100:
                p.showPage()
                y = 800

        p.save()
        return response


@method_decorator(login_required, name='dispatch')
class ChangeLogReportView(RoleRequiredMixin, TemplateView):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    template_name = "wms/reports/changelog_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_30_days = now() - timedelta(days=30)
        changelogs = ChangeLog.objects.filter(created_at__gte=last_30_days).order_by("-created_at")
        context["changelogs"] = changelogs
        return context


# Выдача и списание — MANAGER и SELLER
@method_decorator(login_required, name='dispatch')
class IssueView(RoleRequiredMixin, View):
    allowed_roles = [ROLE_CHOICES.MANAGER, ROLE_CHOICES.SELLER]
    template_name = "wms/issue.html"

    def get(self, request):
        issue_cart = request.session.get("issue_cart", [])
        total_items = sum(Decimal(item["quantity"]) for item in issue_cart)

        context = {
            "issue_cart": issue_cart,
            "total_items": total_items,
            "products": Product.objects.filter(is_active=True).order_by("name"),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        issue_cart = request.session.get("issue_cart", [])

        if "add_product" in request.POST:
            product_id = request.POST.get("product")
            try:
                quantity = Decimal(request.POST.get("quantity", 0))
            except InvalidOperation:
                messages.error(request, "Некоректна кількість")
                return redirect("wms:issue_list")

            if quantity <= 0:
                messages.error(request, "Кількість має бути більшою за 0")
                return redirect("wms:issue_list")

            product = get_object_or_404(Product, id=product_id)

            if product.quantity < quantity:
                messages.error(request, f"Недостатньо товару на складі. Доступно: {product.quantity}")
                return redirect("wms:issue_list")

            for item in issue_cart:
                if item["product_id"] == int(product_id):
                    new_quantity = Decimal(item["quantity"]) + quantity
                    if product.quantity < new_quantity:
                        messages.error(request, f"Недостатньо товару на складі. Доступно: {product.quantity}")
                        return redirect("wms:issue_list")
                    item["quantity"] = str(new_quantity)
                    break
            else:
                issue_cart.append(
                    {
                        "product_id": int(product_id),
                        "product_name": product.name,
                        "quantity": str(quantity),
                        "unit": product.get_unit_display(),
                    }
                )

            request.session["issue_cart"] = issue_cart
            messages.success(request, "Товар додано до списку видачі")
            return redirect("wms:issue_list")

        elif "remove_product" in request.POST:
            product_id = request.POST.get("product_id")
            issue_cart = [item for item in issue_cart if item["product_id"] != int(product_id)]
            request.session["issue_cart"] = issue_cart
            messages.success(request, "Товар видалено зі списку")
            return redirect("wms:issue_list")

        elif "save_issue" in request.POST:
            if issue_cart:
                with transaction.atomic():
                    operation = StockOperation.objects.create(
                        operation_type=OPERATION_CHOICES.ISSUE,
                        created_by=request.user,
                        reason=request.POST.get("reason", ""),
                        note=request.POST.get("note", ""),
                    )

                    for item in issue_cart:
                        product = get_object_or_404(Product, id=item["product_id"])
                        quantity = Decimal(item["quantity"])

                        if product.quantity < quantity:
                            messages.error(
                                request, f"Недостатньо товару на складі. Доступно: {product.quantity}"
                            )
                            return redirect("wms:issue_list")

                        StockOperationItem.objects.create(operation=operation, product=product, quantity=quantity)
                        product.quantity -= quantity
                        product.save()

                request.session["issue_cart"] = []
                messages.success(request, "Видачу товарів збережено")
                return redirect("wms:issue_list")
            else:
                messages.warning(request, "Список порожній")
                return redirect("wms:issue_list")

        return self.get(request)


@method_decorator(login_required, name='dispatch')
class ProductUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = [ROLE_CHOICES.MANAGER]
    model = Product
    form_class = ProductCreateForm
    template_name = "wms/product_form.html"
    success_url = reverse_lazy("wms:product_list")


@method_decorator(login_required, name='dispatch')
class WriteOffView(RoleRequiredMixin, View):
    allowed_roles = [ROLE_CHOICES.MANAGER, ROLE_CHOICES.SELLER]
    template_name = "wms/writeoff.html"

    def get(self, request):
        writeoff_cart = request.session.get("writeoff_cart", [])
        total_items = sum(Decimal(item["quantity"]) for item in writeoff_cart)

        context = {
            "writeoff_cart": writeoff_cart,
            "total_items": total_items,
            "products": Product.objects.filter(is_active=True).order_by("name"),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        writeoff_cart = request.session.get("writeoff_cart", [])

        if "add_product" in request.POST:
            product_id = request.POST.get("product")
            try:
                quantity = Decimal(request.POST.get("quantity", 0))
            except InvalidOperation:
                messages.error(request, "Неверное количество")
                return redirect("wms:writeoff_list")

            if quantity <= 0:
                messages.error(request, "Кількість має бути більшою за 0")
                return redirect("wms:writeoff_list")

            product = get_object_or_404(Product, id=product_id)

            if product.quantity < quantity:
                messages.error(request, f"Недостатньо товару на складі. Доступно: {product.quantity}")
                return redirect("wms:writeoff_list")

            for item in writeoff_cart:
                if item["product_id"] == int(product_id):
                    new_quantity = Decimal(item["quantity"]) + quantity
                    if product.quantity < new_quantity:
                        messages.error(request, f"Недостатньо товару на складі. Доступно: {product.quantity}")
                        return redirect("wms:writeoff_list")
                    item["quantity"] = str(new_quantity)
                    break
            else:
                writeoff_cart.append(
                    {
                        "product_id": int(product_id),
                        "product_name": product.name,
                        "quantity": str(quantity),
                        "unit": product.get_unit_display(),
                    }
                )

            request.session["writeoff_cart"] = writeoff_cart
            messages.success(request, "Товар додано до списку списання")
            return redirect("wms:writeoff_list")

        elif "remove_product" in request.POST:
            product_id = request.POST.get("product_id")
            writeoff_cart = [item for item in writeoff_cart if item["product_id"] != int(product_id)]
            request.session["writeoff_cart"] = writeoff_cart
            messages.success(request, "Товар видалено зі списку")
            return redirect("wms:writeoff_list")

        elif "save_writeoff" in request.POST:
            if writeoff_cart:
                with transaction.atomic():
                    operation = StockOperation.objects.create(
                        operation_type=OPERATION_CHOICES.WRITE_OFF,
                        created_by=request.user,
                        reason=request.POST.get("reason", ""),
                        note=request.POST.get("note", ""),
                    )

                    for item in writeoff_cart:
                        product = get_object_or_404(Product, id=item["product_id"])
                        quantity = Decimal(item["quantity"])

                        if product.quantity < quantity:
                            messages.error(
                                request, f"Недостатньо товару на складі. Доступно: {product.quantity}"
                            )
                            return redirect("wms:writeoff_list")

                        StockOperationItem.objects.create(operation=operation, product=product, quantity=quantity)
                        product.quantity -= quantity
                        product.save()

                request.session["writeoff_cart"] = []
                messages.success(request, "Списання товарів збережено")
                return redirect("wms:writeoff_list")
            else:
                messages.warning(request, "Список порожній")
                return redirect("wms:writeoff_list")

        return self.get(request)


@method_decorator(login_required, name='dispatch')
class ToolsView(RoleRequiredMixin, TemplateView):
    allowed_roles = [ROLE_CHOICES.MANAGER, ROLE_CHOICES.SELLER, ROLE_CHOICES.WORKER]
    template_name = "wms/tools.html"


@login_required
def barcode_generator(request):
    if request.method == "GET" and request.GET.get("free") == "1":
        import random
        while True:
            code = str(random.randint(10**11, 10**12-1))  # 12-значный
            if not Product.objects.filter(barcode=code).exists():
                return JsonResponse({"barcode": code})
    if request.method == "POST":
        code = request.POST.get("barcode_text", "")
        if not code:
            return HttpResponse("Введіть текст для генерації штрихкоду", status=400)
        if Product.objects.filter(barcode=code).exists():
            return HttpResponse("Такий штрихкод вже існує в базі! Введіть інший.", status=400)
        ean = barcode.get('ean13', code.zfill(12), writer=ImageWriter())
        buffer = io.BytesIO()
        ean.write(buffer)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"barcode_{code}.png", content_type="image/png")
    return HttpResponseForbidden()


@login_required
def export_products_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Товари"
    ws.append(["Назва", "Штрихкод", "Категорія", "Ціна закупки", "Ціна продажу", "Кількість", "Одиниця"])
    for p in Product.objects.all():
        ws.append([
            p.name,
            p.barcode,
            p.category.name if p.category else "-",
            str(p.purchase_price),
            str(p.selling_price),
            float(p.quantity),
            p.get_unit_display(),
        ])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="products.xlsx", content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@login_required
def export_products_csv(request):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Назва", "Штрихкод", "Категорія", "Ціна закупки", "Ціна продажу", "Кількість", "Одиниця"])
    for p in Product.objects.all():
        writer.writerow([
            p.name,
            p.barcode,
            p.category.name if p.category else "-",
            str(p.purchase_price),
            str(p.selling_price),
            float(p.quantity),
            p.get_unit_display(),
        ])
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=products.csv"
    return response
