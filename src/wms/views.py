from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

import openpyxl
from reportlab.pdfgen import canvas
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from wms.forms import AddProductForm, ProductCreateForm
from wms.models import (OPERATION_CHOICES, Category, Product, StockOperation,
                        StockOperationItem, ChangeLog)


class IndexView(TemplateView):
    template_name = "index.html"


class DashboardView(TemplateView):
    template_name = "wms/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today().date()
        last_7_days = [today - timedelta(days=i) for i in reversed(range(7))]

        context["active_products_count"] = Product.objects.filter(is_active=True).count()
        context["total_quantity"] = Product.objects.aggregate(total=Sum("quantity"))["total"] or 0

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

        context["date_labels"] = [day.strftime("%d-%m") for day in last_7_days]
        context["receipt_data"] = [daily_counts[OPERATION_CHOICES.RECEIPT][day] for day in last_7_days]
        context["issue_data"] = [daily_counts[OPERATION_CHOICES.ISSUE][day] for day in last_7_days]
        context["write_off_data"] = [daily_counts[OPERATION_CHOICES.WRITE_OFF][day] for day in last_7_days]

        return context


class ProductListView(ListView):
    model = Product
    template_name = "wms/products.html"
    context_object_name = "page_obj"
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

        for p in context["page_obj"]:
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


class ReceiptView(View):
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


        elif 'create_product' in request.POST:
            form = ProductCreateForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('wms:receipt_list')


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


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductCreateForm
    template_name = "wms/product_create.html"
    success_url = reverse_lazy("wms:receipt_list")


class ReportListView(TemplateView):
    template_name = 'wms/reports/report_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = [
            {'url': 'wms:product_report', 'title': 'Звіт по товарам'},
            {'url': 'wms:stock_report', 'title': 'Звіт по операціях на складі'},
            {'url': 'wms:changelog_report', 'title': 'Звіт по змінах'},
        ]
        return context


class ProductReportView(ListView):
    model = Product
    template_name = 'wms/reports/product_report.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        export = self.request.GET.get('export')
        queryset = self.get_queryset()

        if export == 'excel':
            return self.export_to_excel(queryset)
        elif export == 'pdf':
            return self.export_to_pdf(queryset)
        return super().render_to_response(context, **response_kwargs)

    def export_to_excel(self, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Products"

        ws.append(["Назва", "Категорія", "Ціна", "Кількість", "Дата створення"])

        for p in queryset:
            ws.append([
                p.name,
                p.category.name if p.category else "-",
                str(p.selling_price),
                float(p.quantity),
                p.created_at.strftime('%Y-%m-%d') if p.created_at else ''
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=products_report.xlsx'
        wb.save(response)
        return response

    def export_to_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=products_report.pdf'

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 12)
        y = 800
        p.drawString(100, y, "Звіт по товарах")
        y -= 30
        for product in queryset:
            line = f"{product.name} | {product.category.name if product.category else '-'} | {product.selling_price} | {product.quantity}"
            p.drawString(50, y, line)
            y -= 20
            if y < 100:
                p.showPage()
                y = 800

        p.save()
        return response

class StockOperationReportView(ListView):
    model = StockOperation
    template_name = 'wms/reports/stock_operation_report.html'
    context_object_name = 'operations'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        operation_type = self.request.GET.get('operation_type')

        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['operation_type'] = self.request.GET.get('operation_type', '')
        context['operation_choices'] = StockOperation._meta.get_field('operation_type').choices
        return context

    def render_to_response(self, context, **response_kwargs):
        export = self.request.GET.get('export')
        queryset = self.get_queryset()

        if export == 'excel':
            return self.export_to_excel(queryset)
        elif export == 'pdf':
            return self.export_to_pdf(queryset)

        return super().render_to_response(context, **response_kwargs)

    def export_to_excel(self, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Stock Operations"

        ws.append(["Тип операції", "Користувач", "Причина", "Примітка", "Товари", "Дата"])

        for op in queryset:
            items_str = "; ".join([f"{item.product.name} ({item.quantity})" for item in op.items.all()])
            ws.append([
                op.get_operation_type_display(),
                op.created_by.get_full_name() if op.created_by else "-",
                op.reason,
                op.note,
                items_str,
                op.created_at.strftime('%Y-%m-%d %H:%M'),
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=stock_operations_report.xlsx'
        wb.save(response)
        return response

    def export_to_pdf(self, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=stock_operations_report.pdf'

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 12)
        y = 800
        p.drawString(50, y, "Звіт по операціях на складі")
        y -= 30

        for op in queryset:
            items_str = ", ".join([f"{item.product.name}({item.quantity})" for item in op.items.all()])
            line = f"{op.get_operation_type_display()} | {op.created_by.get_full_name() if op.created_by else '-'} | {op.reason} | {items_str} | {op.created_at.strftime('%Y-%m-%d %H:%M')}"
            p.drawString(20, y, line)
            y -= 20
            if y < 100:
                p.showPage()
                y = 800

        p.save()
        return response


class ChangeLogReportView(TemplateView):
    template_name = 'wms/reports/changelog_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_30_days = now() - timedelta(days=30)
        changelogs = ChangeLog.objects.filter(created_at__gte=last_30_days).order_by('-created_at')
        context['changelogs'] = changelogs
        return context