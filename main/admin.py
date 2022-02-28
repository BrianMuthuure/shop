from django.contrib import admin

from .models import Category, Item, Review, Customer, Cart, CartItem, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'marked_price', 'selling_price', 'active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'cart', 'rate', 'subtotal']


admin.site.register([Review, Customer, Cart, Order])
