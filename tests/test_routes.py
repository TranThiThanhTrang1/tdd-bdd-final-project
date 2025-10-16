######################################################################
# Product API Service Test Suite
######################################################################
import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory

# Disable logging except critical during normal tests
# logging.disable(logging.CRITICAL)

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"

class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ####################################################################
    # Utility function to bulk create products
    ####################################################################
    def _create_products(self, count: int = 1):
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ####################################################################
    # TEST CASES
    ####################################################################

    # ---------------- CREATE ----------------
    def test_create_product(self):
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)

    # ---------------- READ ----------------
    def test_get_product(self):
        product = self._create_products()[0]
        response = self.client.get(f"{BASE_URL}/{product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], product.id)
        self.assertEqual(data["name"], product.name)

    def test_get_product_not_found(self):
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------- UPDATE ----------------
    def test_update_product(self):
        product = self._create_products()[0]
        product.description = "Updated description"
        response = self.client.put(
            f"{BASE_URL}/{product.id}", json=product.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated = response.get_json()
        self.assertEqual(updated["description"], "Updated description")

    # ---------------- DELETE ----------------
    def test_delete_product(self):
        product = self._create_products()[0]
        response = self.client.delete(f"{BASE_URL}/{product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify deleted
        response = self.client.get(f"{BASE_URL}/{product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ---------------- LIST ALL ----------------
    def test_list_products(self):
        products = self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ---------------- FILTER BY NAME ----------------
    def test_list_products_by_name(self):
        products = self._create_products(5)
        name = products[0].name
        response = self.client.get(f"{BASE_URL}?name={name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(all(p["name"] == name for p in data))

    # ---------------- FILTER BY CATEGORY ----------------
    def test_list_products_by_category(self):
        products = self._create_products(5)
        category = products[0].category.name
        response = self.client.get(f"{BASE_URL}?category={category}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(all(p["category"] == category for p in data))

    # ---------------- FILTER BY AVAILABILITY ----------------
    def test_list_products_by_availability(self):
        products = self._create_products(5)
        available = str(products[0].available).lower()
        response = self.client.get(f"{BASE_URL}?available={available}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(all(p["available"] == products[0].available for p in data))
