from django.core.management.base import BaseCommand
from Product.models import Category, Attribute, Product


class Command(BaseCommand):
    help = 'Create sample data for Product management system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create Categories
        electronics = Category.objects.get_or_create(
            name='Electronics',
            defaults={'description': 'Electronic items and devices'}
        )[0]
        
        clothing = Category.objects.get_or_create(
            name='Clothing',
            defaults={'description': 'Apparel and fashion items'}
        )[0]
        
        home_garden = Category.objects.get_or_create(
            name='Home & Garden',
            defaults={'description': 'Home improvement and garden items'}
        )[0]
        
        # Create Sub Categories
        laptops = Category.objects.get_or_create(
            name='Laptops',
            parent_category=electronics,
            defaults={'description': 'Laptop computers and accessories'}
        )[0]
        
        mobile_phones = Category.objects.get_or_create(
            name='Mobile Phones',
            parent_category=electronics,
            defaults={'description': 'Smartphones and mobile devices'}
        )[0]
        
        mens_clothing = Category.objects.get_or_create(
            name="Men's Clothing",
            parent_category=clothing,
            defaults={'description': 'Clothing items for men'}
        )[0]
        
        womens_clothing = Category.objects.get_or_create(
            name="Women's Clothing",
            parent_category=clothing,
            defaults={'description': 'Clothing items for women'}
        )[0]
        
        furniture = Category.objects.get_or_create(
            name='Furniture',
            parent_category=home_garden,
            defaults={'description': 'Home and office furniture'}
        )[0]
        
        # Create Attributes
        size_attr = Attribute.objects.get_or_create(
            name='Size',
            attribute_type='choice',
            defaults={
                'description': 'Product size variations',
                'choices': 'XS, S, M, L, XL, XXL',
                'is_required': False
            }
        )[0]
        
        color_attr = Attribute.objects.get_or_create(
            name='Color',
            attribute_type='choice',
            defaults={
                'description': 'Available colors',
                'choices': 'Red, Blue, Green, Black, White, Gray, Brown',
                'is_required': False
            }
        )[0]
        
        brand_attr = Attribute.objects.get_or_create(
            name='Brand',
            attribute_type='text',
            defaults={
                'description': 'Product brand/manufacturer',
                'is_required': False
            }
        )[0]
        
        ram_attr = Attribute.objects.get_or_create(
            name='RAM',
            attribute_type='choice',
            defaults={
                'description': 'Memory capacity',
                'choices': '4GB, 8GB, 16GB, 32GB, 64GB',
                'is_required': False
            }
        )[0]
        
        storage_attr = Attribute.objects.get_or_create(
            name='Storage',
            attribute_type='choice',
            defaults={
                'description': 'Storage capacity',
                'choices': '128GB, 256GB, 512GB, 1TB, 2TB',
                'is_required': False
            }
        )[0]
        
        # Create Sample Products
        products_data = [
            {
                'item_name': 'Dell Inspiron 15 Laptop',
                'category': electronics,
                'sub_category': laptops,
                'purchase_price': 45000.00,
                'mrp': 55000.00,
                'description': 'High-performance laptop with Intel Core i5 processor, 8GB RAM, and 512GB SSD.',
                'is_active': True
            },
            {
                'item_name': 'MacBook Air M2',
                'category': electronics,
                'sub_category': laptops,
                'purchase_price': 95000.00,
                'mrp': 115000.00,
                'description': 'Latest MacBook Air with M2 chip, 16GB unified memory, and 512GB SSD.',
                'is_active': True
            },
            {
                'item_name': 'iPhone 15 Pro',
                'category': electronics,
                'sub_category': mobile_phones,
                'purchase_price': 125000.00,
                'mrp': 134900.00,
                'description': 'Latest iPhone with A17 Pro chip, 128GB storage, and titanium design.',
                'is_active': True
            },
            {
                'item_name': 'Samsung Galaxy S24',
                'category': electronics,
                'sub_category': mobile_phones,
                'purchase_price': 70000.00,
                'mrp': 79999.00,
                'description': 'Flagship Android smartphone with advanced camera system and AI features.',
                'is_active': True
            },
            {
                'item_name': 'Cotton Polo T-Shirt',
                'category': clothing,
                'sub_category': mens_clothing,
                'purchase_price': 350.00,
                'mrp': 699.00,
                'description': 'Premium cotton polo t-shirt available in multiple colors.',
                'is_active': True
            },
            {
                'item_name': 'Formal Dress Shirt',
                'category': clothing,
                'sub_category': mens_clothing,
                'purchase_price': 800.00,
                'mrp': 1499.00,
                'description': 'Professional formal shirt for office wear, wrinkle-free fabric.',
                'is_active': True
            },
            {
                'item_name': 'Designer Kurti',
                'category': clothing,
                'sub_category': womens_clothing,
                'purchase_price': 600.00,
                'mrp': 1299.00,
                'description': 'Traditional Indian kurti with modern design and comfortable fit.',
                'is_active': True
            },
            {
                'item_name': 'Leather Handbag',
                'category': clothing,
                'sub_category': womens_clothing,
                'purchase_price': 1200.00,
                'mrp': 2499.00,
                'description': 'Genuine leather handbag with multiple compartments and elegant design.',
                'is_active': True
            },
            {
                'item_name': 'Ergonomic Office Chair',
                'category': home_garden,
                'sub_category': furniture,
                'purchase_price': 8000.00,
                'mrp': 12999.00,
                'description': 'Comfortable office chair with lumbar support and adjustable height.',
                'is_active': True
            },
            {
                'item_name': 'Wooden Dining Table',
                'category': home_garden,
                'sub_category': furniture,
                'purchase_price': 15000.00,
                'mrp': 22999.00,
                'description': '6-seater wooden dining table with elegant finish and durable construction.',
                'is_active': True
            },
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                item_name=product_data['item_name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.item_name} ({product.barcode})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.item_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Sample data creation completed!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total Categories: {Category.objects.count()}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total Attributes: {Attribute.objects.count()}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total Products: {Product.objects.count()}')
        )