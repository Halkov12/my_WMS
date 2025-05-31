# from django.contrib.auth import get_user_model
# from django.test import TestCase
#
# from wms.models import (Category, ChangeLog, Product, StockOperation,
#                         StockOperationItem)
#
#
# class ModelsTestCase(TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(email="testuser@user.com", role=0)
#         self.user.set_password("12345213qrrq")
#         self.user.save()
#
#         self.category = Category.objects.create(name="Electronics")
#         self.product = Product.objects.create(
#             name="Notebook", barcode="BARCODE123", category=self.category, unit=0, quantity=10
#         )
#
#     def test_product_creation(self):
#         self.assertEqual(Product.objects.count(), 1)
#         self.assertEqual(self.product.name, "Notebook")
#         self.assertEqual(self.product.quantity, 10)
#
#     def test_category_relation(self):
#         self.assertEqual(self.product.category.name, "Electronics")
#
#     def test_stock_operation_receipt(self):
#         operation = StockOperation.objects.create(operation_type=0, created_by=self.user, reason="purchase")
#         item = StockOperationItem.objects.create(operation=operation, product=self.product, quantity=5)
#         self.assertEqual(operation.items.count(), 1)
#         self.assertEqual(item.quantity, 5)
#
#     def test_changelog(self):
#         ChangeLog.objects.create(
#             user=self.user,
#             action="Product created",
#             product=self.product,
#             details={"field": "quantity", "old": 0, "new": 10},
#         )
#         log = ChangeLog.objects.first()
#         self.assertEqual(log.product.name, "Notebook")
