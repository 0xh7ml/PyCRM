from django.db import models
from django.urls import reverse
from Product.models import Product
from django.contrib.auth.models import User

class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)  # For future order reservations
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        ordering = ['product__item_name']
    
    def __str__(self):
        return f"{self.product.item_name} - Stock: {self.quantity}"
    
    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
    
    def add_stock(self, quantity):
        """Add stock to the product"""
        self.quantity += quantity
        self.save()
    
    def reduce_stock(self, quantity):
        """Reduce stock from the product"""
        if self.available_quantity >= quantity:
            self.quantity -= quantity
            self.save()
            return True
        return False
    
    def can_fulfill(self, quantity):
        """Check if we can fulfill the requested quantity without going negative"""
        return self.available_quantity >= quantity

class StockIn(models.Model):
    stock_in_id = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    total_items = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Stock In'
        verbose_name_plural = 'Stock Ins'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Stock In {self.stock_in_id} - {self.created_at.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        if not self.stock_in_id:
            self.stock_in_id = self.generate_stock_in_id()
        super().save(*args, **kwargs)
    
    def generate_stock_in_id(self):
        from datetime import datetime
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # Get today's stock in count
        today_stock_ins = StockIn.objects.filter(
            stock_in_id__startswith=f'SI{date_str}'
        ).count()
        
        return f'SI{date_str}{today_stock_ins + 1:03d}'
    
    def calculate_total_items(self):
        total = sum(item.quantity for item in self.items.all())
        if self.total_items != total:
            StockIn.objects.filter(pk=self.pk).update(total_items=total)
            self.total_items = total
    
    def complete_stock_in(self):
        """Complete the stock in and update product stocks"""
        if not self.is_completed:
            for item in self.items.all():
                stock, created = Stock.objects.get_or_create(
                    product=item.product,
                    defaults={'quantity': 0}
                )
                stock.add_stock(item.quantity)
            
            self.is_completed = True
            self.save()
            return True
        return False
    
    def get_absolute_url(self):
        return reverse('stock-in-detail', kwargs={'pk': self.pk})

class StockInItem(models.Model):
    stock_in = models.ForeignKey(StockIn, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['stock_in', 'product']
        verbose_name = 'Stock In Item'
        verbose_name_plural = 'Stock In Items'
    
    def __str__(self):
        return f"{self.product.item_name} - Qty: {self.quantity}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update stock in total items
        self.stock_in.calculate_total_items()
