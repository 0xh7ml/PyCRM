from django.core.management.base import BaseCommand
from Product.models import Product
from Inventory.models import Stock


class Command(BaseCommand):
    help = 'Ensure all products have stock records'

    def handle(self, *args, **options):
        products_without_stock = Product.objects.filter(stock__isnull=True)
        
        created_count = 0
        for product in products_without_stock:
            stock, created = Stock.objects.get_or_create(
                product=product,
                defaults={'quantity': 0, 'reserved_quantity': 0}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created stock record for product: {product.item_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} stock records')
        )
        
        # Show current stock summary
        total_stocks = Stock.objects.count()
        total_products = Product.objects.count()
        
        self.stdout.write(f'\nStock Summary:')
        self.stdout.write(f'Total products: {total_products}')
        self.stdout.write(f'Products with stock records: {total_stocks}')
        
        if total_stocks == total_products:
            self.stdout.write(
                self.style.SUCCESS('✓ All products now have stock records')
            )
        else:
            missing = total_products - total_stocks
            self.stdout.write(
                self.style.WARNING(f'⚠ {missing} products still missing stock records')
            )