from django.contrib import admin
from django.utils.text import slugify
from .models import Food, FoodVariant, Menu, FoodCategory, ContactMessages
from .utils import resize_image


class FoodCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'kitchen', 'slug')
    search_fields = ('title', 'kitchen__title')
    list_filter = ('kitchen',)

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = slugify(obj.title)
            slug = base_slug
            counter = 1
            while FoodCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            obj.slug = slug
        super().save_model(request, obj, form, change)


class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'kitchen', 'price', 'is_active', 'created', 'updated')
    search_fields = ('name', 'category__title', 'kitchen__title')
    list_filter = ('category', 'kitchen', 'is_active')
    readonly_fields = ('created', 'updated')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'image' in form.changed_data or not change:
            resize_image(obj.image, 300, 300)


class FoodVariantAdmin(admin.ModelAdmin):
    list_display = ('food', 'name', 'price')
    search_fields = ('food__name', 'name')
    list_filter = ('food',)


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'kitchen', 'created', 'updated')
    search_fields = ('name', 'kitchen__title')
    list_filter = ('kitchen',)
    readonly_fields = ('created', 'updated')


class ContactMessagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'is_read', 'created', 'updated')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('is_read',)
    readonly_fields = ('created', 'updated')


# Register your models with the custom admin classes
admin.site.register(FoodCategory, FoodCategoryAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(FoodVariant, FoodVariantAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(ContactMessages, ContactMessagesAdmin)
