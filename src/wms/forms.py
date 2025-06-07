from django import forms
from django.forms import inlineformset_factory

from wms.models import Product, StockOperation, StockOperationItem


class StockOperationForm(forms.ModelForm):
    class Meta:
        model = StockOperation
        fields = ["reason", "note"]
        widgets = {
            "reason": forms.TextInput(attrs={"class": "form-control"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reason"].label = "Причина"
        self.fields["note"].label = "Примітка"


class StockOperationItemForm(forms.ModelForm):
    class Meta:
        model = StockOperationItem
        fields = ("product", "quantity")
        widgets = {
            "product": forms.Select(attrs={"class": "form-control select2-product"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


StockOperationItemFormSet = inlineformset_factory(
    StockOperation, StockOperationItem, form=StockOperationItemForm, extra=1, can_delete=True
)


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "barcode", "purchase_price", "selling_price", "unit", "quantity", "category"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "barcode": forms.TextInput(attrs={"class": "form-control"}),
            "unit": forms.Select(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = "Назва"
        self.fields["barcode"].label = "Штрихкод"
        self.fields["purchase_price"].label = "Ціна закупки"
        self.fields["selling_price"].label = "Ціна продажу"
        self.fields["unit"].label = "Одиниця виміру"
        self.fields["quantity"].label = "Кількість"
        self.fields["category"].label = "Категорія"


class AddProductForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Товар",
        widget=forms.Select(
            attrs={"class": "form-select", "hx-get": "/products/search/", "hx-target": "#product-results"}
        ),
    )
    quantity = forms.DecimalField(
        label="Кількість",
        min_value=0.01,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
