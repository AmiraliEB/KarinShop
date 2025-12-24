import pytest


@pytest.fixture
def sample_product_setup():
    from products.models import ProductCategory, Brand, ParentProduct
    category = ProductCategory.objects.create(name="General", code="gen")
    brand = Brand.objects.create(name="Generic", code="gnr")
    parent = ParentProduct.objects.create(name="Test Product", category=category, brand=brand)
    return parent

@pytest.fixture
def product_factory(sample_product_setup):
    from products.models import Attribute, AttributeRule, AttributeValue, Product, AttributeCategory
    product_category = sample_product_setup.category
    
    attr_cat = AttributeCategory.objects.create(name="Spec")

    memory_attr = Attribute.objects.create(name="Memory", attribute_category=attr_cat, is_variant_defining=True)
    color_attr = Attribute.objects.create(name="Color", attribute_category=attr_cat, is_variant_defining=True)
    storage_attr = Attribute.objects.create(name="Storage", attribute_category=attr_cat, is_variant_defining=True)

    AttributeRule.objects.create(attribute=memory_attr, category=product_category, is_main_feature=True)
    AttributeRule.objects.create(attribute=color_attr, category=product_category, is_main_feature=True)
    AttributeRule.objects.create(attribute=storage_attr, category=product_category, is_main_feature=True)

    def _create_product(parent_product=sample_product_setup, initial_price=100, discount_type='amount', discount_value=0, stock=10):

        mem_val, _ = AttributeValue.objects.get_or_create(attribute=memory_attr, value="8GB")
        col_val, _ = AttributeValue.objects.get_or_create(attribute=color_attr, value="Blue")
        str_val, _ = AttributeValue.objects.get_or_create(attribute=storage_attr, value="256GB")

        product = Product.objects.create(
            parent_product=parent_product,
            initial_price=initial_price,
            discount_type=discount_type,
            discount_value=discount_value,
            stock=stock
        )

        product.attribute_values.add(mem_val, col_val, str_val)
        
        product.save()
        
        return product

    return _create_product