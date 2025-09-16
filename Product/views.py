from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Attribute, Product

# Create your views here.

# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'product/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        return Category.objects.all().order_by('parent_category__name', 'name')


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'product/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_categories'] = self.object.sub_categories.all()
        context['products'] = self.object.products.all()[:10]  # Show first 10 products
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'product/category_form.html'
    fields = ['name', 'parent_category', 'description']
    success_url = reverse_lazy('product:category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'product/category_form.html'
    fields = ['name', 'parent_category', 'description']
    success_url = reverse_lazy('product:category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'product/category_confirm_delete.html'
    success_url = reverse_lazy('product:category_list')

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f'Category "{category.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Attribute Views
class AttributeListView(LoginRequiredMixin, ListView):
    model = Attribute
    template_name = 'product/attribute_list.html'
    context_object_name = 'attributes'
    paginate_by = 20


class AttributeDetailView(LoginRequiredMixin, DetailView):
    model = Attribute
    template_name = 'product/attribute_detail.html'
    context_object_name = 'attribute'


class AttributeCreateView(LoginRequiredMixin, CreateView):
    model = Attribute
    template_name = 'product/attribute_form.html'
    fields = ['name', 'attribute_type', 'description', 'choices', 'is_required']
    success_url = reverse_lazy('product:attribute_list')

    def form_valid(self, form):
        messages.success(self.request, f'Attribute "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class AttributeUpdateView(LoginRequiredMixin, UpdateView):
    model = Attribute
    template_name = 'product/attribute_form.html'
    fields = ['name', 'attribute_type', 'description', 'choices', 'is_required']
    success_url = reverse_lazy('product:attribute_list')

    def form_valid(self, form):
        messages.success(self.request, f'Attribute "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class AttributeDeleteView(LoginRequiredMixin, DeleteView):
    model = Attribute
    template_name = 'product/attribute_confirm_delete.html'
    success_url = reverse_lazy('product:attribute_list')

    def delete(self, request, *args, **kwargs):
        attribute = self.get_object()
        messages.success(request, f'Attribute "{attribute.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.select_related('category', 'sub_category').filter(is_active=True)


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'product/product_form.html'
    fields = ['item_name', 'category', 'sub_category', 'purchase_price', 'mrp', 'description', 'is_active']
    success_url = reverse_lazy('product:product_list')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.item_name}" created successfully with barcode {form.instance.barcode}!')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'product/product_form.html'
    fields = ['item_name', 'category', 'sub_category', 'purchase_price', 'mrp', 'description', 'is_active']
    success_url = reverse_lazy('product:product_list')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.item_name}" updated successfully!')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = reverse_lazy('product:product_list')

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        messages.success(request, f'Product "{product.item_name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)
