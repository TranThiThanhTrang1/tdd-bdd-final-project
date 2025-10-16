######################################################################
# Product Store Service with REST API
######################################################################
from flask import jsonify, request, abort
from service.models import Product
from service.common import status
from . import app

# ---------------- HEALTH CHECK ----------------
@app.route("/health")
def healthcheck():
    return jsonify(status=200, message="OK"), status.HTTP_200_OK

# ---------------- HOME PAGE ----------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# ---------------- UTILITY ----------------
def check_content_type(content_type):
    if "Content-Type" not in request.headers:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}")
    if request.headers["Content-Type"] != content_type:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}")

# ---------------- CREATE ----------------
@app.route("/products", methods=["POST"])
def create_products():
    check_content_type("application/json")
    data = request.get_json()
    product = Product()
    product.deserialize(data)
    product.create()
    location_url = f"/products/{product.id}"
    return jsonify(product.serialize()), status.HTTP_201_CREATED, {"Location": location_url}

# ---------------- LIST ----------------
@app.route("/products", methods=["GET"])
def list_products():
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    products = Product.all()

    if name:
        products = [p for p in products if p.name == name]
    if category:
        try:
            category_enum = getattr(Product.Category, category.upper())
            products = [p for p in products if p.category == category_enum]
        except AttributeError:
            products = []
    if available is not None:
        available_bool = available.lower() == "true"
        products = [p for p in products if p.available == available_bool]

    return jsonify([p.serialize() for p in products]), status.HTTP_200_OK

# ---------------- READ ----------------
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    product = Product.find(product_id)
    if not product:
        return abort(status.HTTP_404_NOT_FOUND, f"Product with id [{product_id}] not found")
    return jsonify(product.serialize()), status.HTTP_200_OK

# ---------------- UPDATE ----------------
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id: int):
    product = Product.find(product_id)
    if not product:
        return abort(status.HTTP_404_NOT_FOUND, f"Product with id [{product_id}] not found")
    check_content_type("application/json")
    data = request.get_json()
    product.deserialize(data)
    product.update()
    return jsonify(product.serialize()), status.HTTP_200_OK

# ---------------- DELETE ----------------
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int):
    product = Product.find(product_id)
    if not product:
        return abort(status.HTTP_404_NOT_FOUND, f"Product with id [{product_id}] not found")
    product.delete()
    return "", status.HTTP_204_NO_CONTENT
