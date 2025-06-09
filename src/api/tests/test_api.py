from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from wms.models import Product


class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model()(email="testuser@mail.com")
        self.user.set_password("pass1234")
        self.user.save()

        self.token = RefreshToken.for_user(self.user).access_token
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.product = Product.objects.create(
            name="Test Product",
            purchase_price=100,
            selling_price=150,
            barcode="unique-barcode-001",
        )

    def test_product_list(self):
        url = reverse("api:product-list")
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertTrue(any(p["id"] == self.product.id for p in response.data))

    def test_product_create(self):
        url = reverse("api:product-create")
        data = {
            "name": "New Product",
            "purchase_price": "50.00",
            "selling_price": "75.00",
            "barcode": "unique-barcode-002",
        }
        response = self.client.post(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["barcode"], data["barcode"])

    def test_product_detail(self):
        url = reverse("api:product-detail", args=[self.product.pk])
        response = self.client.get(url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.product.id)
        self.assertEqual(response.data["barcode"], self.product.barcode)

    def test_product_update(self):
        url = reverse("api:product-update", args=[self.product.pk])
        data = {
            "name": "Updated Product",
            "purchase_price": "110.00",
            "selling_price": "160.00",
            "barcode": "unique-barcode-001",
        }
        response = self.client.put(url, data, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(response.data["purchase_price"], data["purchase_price"])
        self.assertEqual(response.data["selling_price"], data["selling_price"])
        self.assertEqual(response.data["barcode"], data["barcode"])

    def test_product_delete(self):
        url = reverse("api:product-delete", args=[self.product.pk])
        response = self.client.delete(url, **self.auth_headers)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_unauthorized_access(self):
        url = reverse("api:product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
