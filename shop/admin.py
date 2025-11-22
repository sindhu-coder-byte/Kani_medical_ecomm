from django.contrib import admin
from .models import Product, ProductThumbnail

class ProductThumbnailInline(admin.TabularInline):
    model = ProductThumbnail
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_featured', 'badge')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    inlines = [ProductThumbnailInline]
