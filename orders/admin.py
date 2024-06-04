from django.contrib import admin
from .models import Orders, OrderItems

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'kitchen', 'user', 'table', 'total_price', 'status', 'created']
    list_filter = ['kitchen', 'status', 'created']
    search_fields = ['order_number', 'table__number', 'user__phone_number', 'kitchen__title']
    readonly_fields = ['order_number', 'total_price', 'created', 'updated']

    def display_order_items(self, obj):
        return ', '.join([f"{item.food} ({item.quantity})" for item in obj.foods.all()])

    display_order_items.short_description = 'Order Items'

    # Register the custom method as a readonly field
    readonly_fields = ['display_order_items']
