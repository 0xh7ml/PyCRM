from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Vendor


class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'crm/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 10
    ordering = ['name']


class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    template_name = 'crm/vendor_form.html'
    fields = ['name', 'contact_email', 'phone_number', 'address']
    success_url = reverse_lazy('vendor-list')

    def form_valid(self, form):
        messages.success(self.request, f"Vendor '{form.cleaned_data['name']}' was created successfully.")
        return super().form_valid(form)


class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    template_name = 'crm/vendor_form.html'
    fields = ['name', 'contact_email', 'phone_number', 'address']
    success_url = reverse_lazy('vendor-list')

    def form_valid(self, form):
        messages.success(self.request, f"Vendor '{form.cleaned_data['name']}' was updated successfully.")
        return super().form_valid(form)


class VendorDetailView(LoginRequiredMixin, DetailView):
    model = Vendor
    template_name = 'crm/vendor_detail.html'
    context_object_name = 'vendor'


class VendorDeleteView(LoginRequiredMixin, DeleteView):
    model = Vendor
    template_name = 'crm/vendor_confirm_delete.html'
    success_url = reverse_lazy('vendor-list')

    def delete(self, request, *args, **kwargs):
        vendor = self.get_object()
        messages.success(request, f"Vendor '{vendor.name}' was deleted successfully.")
        return super().delete(request, *args, **kwargs)


