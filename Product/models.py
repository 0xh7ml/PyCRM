from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sub_categories'
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        if self.parent_category:
            return f"{self.parent_category.name} - {self.name}"
        return self.name

    def clean(self):
        # Prevent category from being its own parent
        if self.parent_category == self:
            raise ValidationError("A category cannot be its own parent.")

    @property
    def is_parent_category(self):
        return self.parent_category is None

    @property
    def full_path(self):
        if self.parent_category:
            return f"{self.parent_category.name} > {self.name}"
        return self.name


class Attribute(models.Model):
    ATTRIBUTE_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('choice', 'Choice'),
        ('boolean', 'Boolean'),
    ]
    
    name = models.CharField(max_length=100)
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES, default='text')
    description = models.TextField(blank=True, null=True)
    choices = models.TextField(
        blank=True, 
        null=True, 
        help_text="For choice type, enter options separated by commas"
    )
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_attribute_type_display()})"

    def get_choices_list(self):
        if self.choices:
            return [choice.strip() for choice in self.choices.split(',')]
        return []


class Product(models.Model):
    # Basic Information
    item_name = models.CharField(max_length=200)
    barcode = models.CharField(max_length=20, unique=True, editable=False)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        limit_choices_to={'parent_category__isnull': True}  # Only parent categories
    )
    sub_category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='sub_products',
        null=True, 
        blank=True,
        limit_choices_to={'parent_category__isnull': False}  # Only sub categories
    )
    
    # Price Information
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='MRP')
    
    # Additional Information
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.item_name} ({self.barcode})"

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = self.generate_barcode()
        super().save(*args, **kwargs)

    def generate_barcode(self):
        # Get the last product's barcode number
        last_product = Product.objects.filter(
            barcode__startswith='A'
        ).order_by('barcode').last()
        
        if last_product and last_product.barcode:
            # Extract number from barcode (e.g., A000001 -> 1)
            last_number = int(last_product.barcode[1:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        # Format as A000001, A000002, etc.
        return f"A{new_number:06d}"

    def clean(self):
        # Validate that sub_category belongs to the selected category
        if self.sub_category and self.sub_category.parent_category != self.category:
            raise ValidationError("Sub-category must belong to the selected category.")

    @property
    def profit_margin(self):
        if self.purchase_price and self.mrp:
            return self.mrp - self.purchase_price
        return 0

    @property
    def profit_percentage(self):
        if self.purchase_price and self.mrp and self.purchase_price > 0:
            return ((self.mrp - self.purchase_price) / self.purchase_price) * 100
        return 0
