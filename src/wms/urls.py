from django.urls import path
from .views import IndexView, DashboardView, ProductListView

app_name = 'wms'

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("products/", ProductListView.as_view(), name="product_list"),
]