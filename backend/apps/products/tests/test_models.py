import pytest
from model_bakery import baker
from products.models import Product, ProductVariant


@pytest.mark.django_db
def test_calculate_percentage_discount():
    product: Product = baker.make(
        "products.Product", initial_price=1000000, discount_type="percentage", discount_value=20, stock=10
    )

    assert product.final_price == 800000
    assert product.is_available is True


@pytest.mark.django_db
def test_calculate_amount_discount():
    product: Product = baker.make(
        "products.Product", initial_price=500000, discount_type="amount", discount_value=50000, stock=1
    )

    assert product.final_price == 450000
    assert product.is_available is True


@pytest.mark.django_db
def test_no_discount():
    product: Product = baker.make("products.Product", initial_price=300000, discount_value=0, stock=1)

    assert product.final_price == 300000
    assert product.is_available is True


@pytest.mark.django_db
def test_full_name_generator():
    category = baker.make("products.ProductCategory", name="Mobile")
    brand = baker.make("products.Brand", name="Apple")
    attribute_ram = baker.make("products.Attribute", name="RAM", is_variant_defining=True, show_in_specifications=True)
    attribute_ram.product_category.add(category)
    attribute_storage = baker.make(
        "products.Attribute", name="Storage", is_variant_defining=True, show_in_specifications=True
    )
    attribute_storage.product_category.add(category)
    attr_value_ram = baker.make("products.AttributeValue", attribute=attribute_ram, value="8GB")
    attr_value_storage = baker.make("products.AttributeValue", attribute=attribute_storage, value="256GB")

    baker.make("products.AttributeRule", attribute=attribute_ram, category=category, brand=brand, is_main_feature=True)
    baker.make(
        "products.AttributeRule", attribute=attribute_storage, category=category, brand=brand, is_main_feature=True
    )
    product_parent = baker.make("products.ProductParent", name="iPhone 13", category=category, brand=brand)
    product_parent.specification_values.add(attr_value_ram, attr_value_storage)
    product_variant: ProductVariant = baker.make(ProductVariant, parent_product=product_parent)
    product_variant.attribute_values.add(attr_value_ram, attr_value_storage)

    parent = product_parent
    expected_full_name = f"{parent.category.name} {parent.brand.name} {parent.name} 8GB 256GB"

    assert "8GB" in product_variant.full_name
    assert "256GB" in product_variant.full_name
    assert "  " not in product_variant.full_name
    assert expected_full_name == product_variant.full_name
