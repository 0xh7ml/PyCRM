from django.contrib import admin
from .models import Category, Attribute, Product

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'is_parent_category', 'created_at']
    list_filter = ['parent_category', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['parent_category__name', 'name']
    
    def is_parent_category(self, obj):
        return obj.is_parent_category
    is_parent_category.boolean = True
    is_parent_category.short_description = 'Parent Category'


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'attribute_type', 'is_required', 'created_at']
    list_filter = ['attribute_type', 'is_required', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'barcode', 'category', 'sub_category', 'purchase_price', 'mrp', 'is_active']
    list_filter = ['category', 'sub_category', 'is_active', 'created_at']
    search_fields = ['item_name', 'barcode', 'description']
    readonly_fields = ['barcode', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('item_name', 'barcode', 'category', 'sub_category', 'description')
        }),
        ('Price Information', {
            'fields': ('purchase_price', 'mrp')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
