from django.contrib import admin
from .models import ReviewFood, ReviewKitchen

@admin.register(ReviewKitchen)
class ReviewKitchenAdmin(admin.ModelAdmin):
    list_display = ('user', 'kitchen', 'body', 'created')
    list_filter = ('created', 'updated')
    search_fields = ('body', 'user__username', 'kitchen__name')
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'created'

@admin.register(ReviewFood)
class ReviewFoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'body', 'created')
    list_filter = ('created', 'updated')
    search_fields = ('body', 'user__username', 'food__name')
    readonly_fields = ('created', 'updated')
    date_hierarchy = 'created'
