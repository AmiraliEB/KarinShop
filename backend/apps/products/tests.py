import pytest

from products.models import Product

@pytest.mark.django_db
def test_calculate_percentage_discount(product_factory):
    product:Product = product_factory(initial_price=1000000, discount_type='percentage', discount_value=20)

    assert product.final_price == 800000
    assert product.is_available is True

@pytest.mark.django_db
def test_calculate_amount_discount(product_factory):
    product:Product = product_factory(initial_price=500000, discount_type='amount', discount_value=50000)

    assert product.final_price == 450000
    assert product.is_available is True

@pytest.mark.django_db
def test_no_discount(product_factory):
    product:Product = product_factory(initial_price=300000, discount_value=0)

    assert product.final_price == 300000
    assert product.is_available is True

@pytest.mark.django_db
def test_full_name_generator(product_factory):
    product:Product = product_factory()
    expected_name = f"{product.parent_product.category.name} {product.parent_product.brand.name} {product.parent_product.name} 8GB Blue 256GB"
    # this info is comming from conftest 
    assert "8GB" in product.full_name
    assert "Blue" in product.full_name
    assert "256GB" in product.full_name
    assert "  " not in product.full_name
    assert expected_name == product.full_name