from django.contrib import admin
from django.utils.text import slugify
from .models import KitchenOrderReceiver, User, Kitchen, PhoneNumbers, SocialLinks, EmployeeProfile, UserProfile
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class KitchenAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug', 'image', 'created', 'updated')
    search_fields = ('title', 'slug', 'created', 'updated')
    readonly_fields = ('created', 'updated')


    def save_model(self, request, obj, form, change):
        if not obj.slug:
            base_slug = slugify(obj.title)
            slug = base_slug
            counter = 1
            while Kitchen.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            obj.slug = slug
        super().save_model(request, obj, form, change)



class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'full_name', 'is_kitchen', 'kitchen', 'user_type', 'is_active', 'is_staff', 'is_superuser')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on the user, but replaces the password field with admin's password hash display field."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'full_name', 'is_kitchen', 'kitchen', 'user_type', 'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the field does not have access to the initial value
        return self.initial["password"]


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('phone_number', 'full_name', 'is_kitchen', 'user_type', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'user_type')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Kitchens', {'fields': ('is_kitchen', 'kitchen')}),
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'is_kitchen', 'kitchen', 'user_type', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone_number',)
    ordering = ('phone_number',)
    filter_horizontal = ()
    
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'first_name', 'last_name', 'created', 'updated')
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('created', 'updated')

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# Register the UserProfile admin as well
admin.site.register(UserProfile, UserProfileAdmin)



class KitchenOrderReceiverAdmin(admin.ModelAdmin):
    list_display = ('kitchen', 'user', 'created', 'updated')
    search_fields = ('kitchen__title', 'user__full_name')
    readonly_fields = ('created', 'updated')
    list_filter = ('created', 'updated')

    def get_user_full_name(self, obj):
        return obj.user.full_name
    get_user_full_name.short_description = 'User Full Name'

    def get_kitchen_title(self, obj):
        return obj.kitchen.title
    get_kitchen_title.short_description = 'Kitchen Title'

admin.site.register(KitchenOrderReceiver, KitchenOrderReceiverAdmin)


admin.site.register(Kitchen, KitchenAdmin)
admin.site.register(PhoneNumbers)
admin.site.register(SocialLinks)
admin.site.register(EmployeeProfile)

