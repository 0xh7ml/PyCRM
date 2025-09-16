from django.db import models
from django.urls import reverse
from CRM.models import Vendor
from Product.models import Product

class Order(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.pk} - {self.vendor.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate total after saving
        self.calculate_total()

    def calculate_total(self):
        total = sum(item.get_total_price() for item in self.items.all())
        if self.total_amount != total:
            Order.objects.filter(pk=self.pk).update(total_amount=total)
            self.total_amount = total

    def get_absolute_url(self):
        return reverse('order-detail', kwargs={'pk': self.pk})
    
    def restore_stock(self):
        """Restore stock quantities for all items in this order"""
        from Inventory.models import Stock
        
        for order_item in self.items.all():
            try:
                stock = Stock.objects.get(product=order_item.product)
                stock.add_stock(order_item.quantity)
                print(f"Stock restored for {order_item.product.item_name}: +{order_item.quantity} (New quantity: {stock.quantity})")
            except Stock.DoesNotExist:
                print(f"Warning: No stock record found for product {order_item.product.item_name}")
                # Create stock record with the quantity being restored
                Stock.objects.create(product=order_item.product, quantity=order_item.quantity)
    
    def reduce_stock(self):
        """Reduce stock quantities for all items in this order"""
        from Inventory.models import Stock
        
        for order_item in self.items.all():
            try:
                stock = Stock.objects.get(product=order_item.product)
                if stock.reduce_stock(order_item.quantity):
                    print(f"Stock reduced for {order_item.product.item_name}: -{order_item.quantity} (New quantity: {stock.quantity})")
                else:
                    print(f"Warning: Could not reduce stock for {order_item.product.item_name} - insufficient stock")
            except Stock.DoesNotExist:
                print(f"Warning: No stock record found for product {order_item.product.item_name}")
                # Create stock record with zero quantity
                Stock.objects.create(product=order_item.product, quantity=0)

class OrderItem(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage (%)'),
        ('flat', 'Flat Amount'),
    ]

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='flat')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.product.item_name} (x{self.quantity})"

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.mrp
        super().save(*args, **kwargs)
        # Update order total when item is saved
        self.order.calculate_total()

    def get_subtotal(self):
        return self.quantity * self.unit_price

    def get_discount_amount(self):
        if self.discount_type == 'percentage':
            return (self.get_subtotal() * self.discount_value) / 100
        else:
            return self.discount_value

    def get_total_price(self):
        return self.get_subtotal() - self.get_discount_amount()

    @property
    def discount_display(self):
        if self.discount_value > 0:
            if self.discount_type == 'percentage':
                return f"{self.discount_value}%"
            else:
                return f"{self.discount_value}"
        return "No Discount"