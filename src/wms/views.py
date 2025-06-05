from collections import defaultdict
from datetime import datetime, timedelta

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.views.generic import TemplateView, ListView

from wms.models import OPERATION_CHOICES, Category, Product, StockOperation


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

        context.update({
            "query": query,
            "category_id": category_id,
            "total_purchase": total_purchase,
            "total_selling": total_selling,
            "total_quantity": total_quantity,
            "categories": Category.objects.order_by("name"),
        })

        return context
