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
        fields = ["name", "barcode", "purchase_price", "selling_price", "unit", "quantity", "category", "description", "photo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "barcode": forms.TextInput(attrs={"class": "form-control"}),
            "unit": forms.Select(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('purchase_price_currency', None)
        self.fields.pop('selling_price_currency', None)
        if 'purchase_price' in self.fields:
            self.fields['purchase_price'].widget.widgets[1].input_type = 'hidden'
        if 'selling_price' in self.fields:
            self.fields['selling_price'].widget.widgets[1].input_type = 'hidden'
        self.fields["name"].label = "Назва"
        self.fields["barcode"].label = "Штрихкод"
        self.fields["purchase_price"].label = "Ціна закупки"
        self.fields["selling_price"].label = "Ціна продажу"
        self.fields["unit"].label = "Одиниця виміру"
        self.fields["quantity"].label = "Кількість"
        self.fields["category"].label = "Категорія"
        self.fields["description"].label = "Опис"
        self.fields["photo"].label = "Фото товару"

    def clean(self):
        cleaned_data = super().clean()
        # Можно добавити дополнительні перевірки
        return cleaned_data


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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'barcode', 'quantity', 'unit', 'purchase_price', 'selling_price', 'description', 'photo']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('purchase_price_currency', None)
        self.fields.pop('selling_price_currency', None)
        if 'purchase_price' in self.fields:
            self.fields['purchase_price'].widget.widgets[1].input_type = 'hidden'
        if 'selling_price' in self.fields:
            self.fields['selling_price'].widget.widgets[1].input_type = 'hidden'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.data.get('photo-clear'):
            instance.photo.delete(save=False)
            instance.photo = None
        if commit:
            instance.save()
            self.save_m2m()
        return instance
