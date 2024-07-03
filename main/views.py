import json
import random
import datetime
import logging
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

from table.models import Table
from users.models import User, Kitchen
from .models import ContactMessages, Menu, FoodCategory, Food
from menu.decorators import only_kitchen, only_manager
from cart.cart import Cart
from orders.models import Orders
from verification.utils import check_verification_code
from reviews.models import ReviewKitchen, ReviewFood


def generate_kitchen_stats(kitchen):
    reviews = ReviewKitchen.objects.filter(kitchen=kitchen)
    total_reviews = reviews.count()
    total_foods = Food.objects.filter(kitchen=kitchen, is_active=True).count()

    current_year = timezone.now().year
    start_of_year = timezone.make_aware(datetime.datetime(current_year, 1, 1))

    monthly_order_stats = (
        Orders.objects.filter(kitchen=kitchen, created__gte=start_of_year)
        .annotate(month=TruncMonth('created'))
        .values('month')
        .annotate(total_sum=Sum('total_price'), total_orders=Count('id'))
        .order_by('month')
    )

    today = timezone.now().date()
    today_order_stats = (
        Orders.objects.filter(kitchen=kitchen, created__date=today)
        .aggregate(total_sum=Sum('total_price'), total_orders=Count('id'))
    )

    this_month = timezone.now().month
    this_month_order_stats = (
        Orders.objects.filter(kitchen=kitchen, created__month=this_month)
        .aggregate(total_sum=Sum('total_price'), total_orders=Count('id'))
    )

    most_sold_foods = (
        Food.objects.filter(orderitems__orders__kitchen=kitchen)
        .annotate(sold_quantity=Sum('orderitems__quantity'))
        .order_by('-sold_quantity')[:3]
    )

    stats = {
        "monthly_order_dates": [item['month'].strftime('%B') for item in monthly_order_stats],
        "monthly_order_sums": [item['total_sum'] for item in monthly_order_stats],
        "monthly_order_counts": [item['total_orders'] for item in monthly_order_stats],
        "most_sold_food_names": [item.name for item in most_sold_foods],
        "most_sold_food_quantities": [item.sold_quantity for item in most_sold_foods],
    }

    stats = json.dumps(stats)
    
    return {
        'total_reviews': total_reviews,
        'today_order_stats': today_order_stats,
        'this_month_order_stats': this_month_order_stats,
        'total_foods': total_foods,
        'monthly_order_stats': monthly_order_stats,
        "stats": stats,
        "most_sold_foods": most_sold_foods,
    }


def index(request):
    if request.user.is_authenticated and request.user.is_kitchen:
        if request.user.user_type == 'manager':
            kitchen = request.user.kitchen
            stats = generate_kitchen_stats(kitchen)
            context = {
                'parent': 'kitchen',
                'child': 'dashboard',
                'kitchen': kitchen,
                'stats': stats,
            }
            return render(request, 'kitchen/index.html', context=context)
        elif request.user.user_type == 'employee':
            return redirect('orders:index')


    page = request.GET.get('page', 1)
    all_kitchens = Kitchen.objects.all().order_by('created')
    paginator = Paginator(all_kitchens, 6)

    try:
        kitchens = paginator.page(page)
    except PageNotAnInteger:
        kitchens = paginator.page(1)
    except EmptyPage:
        kitchens = paginator.page(paginator.num_pages)

    context = {"kitchens": kitchens}
    return render(request, 'main/index.html', context=context)


def about(request):
    return render(request, "main/about.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')
        ContactMessages.objects.create(name=name, phone_number=phone_number, message=message)
        messages.success(request, 'Message sent successfully! We will contact you soon.')
        return redirect('main:contact')
    return render(request, "main/contact.html")


def register_kitchen(request):
    return render(request, 'kitchen/auth/register2.html')


@only_kitchen
def kitchen_user_profile(request):
    if request.method == "POST":
        name = request.POST.get('name')
        image = request.FILES.get('image')
        user = request.user
        if image:
            user.profile.picture = image
            user.profile.save()
        if name:
            user.full_name = name
            user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('main:kitchen_user_profile')
    return render(request, "kitchen/user_profile.html")


@only_kitchen
def kitchen_profile(request):
    kitchen = request.user.kitchen
    phone_numbers = kitchen.phone_numbers.all()
    if request.method == 'POST':
        section = request.POST.get('section')
        if section == 'profile':
            name = request.POST.get('kitchenName')
            description = request.POST.get('kitchenInfo')
            image = request.FILES.get('kitchenImage')
            kitchen.title = name
            kitchen.info = description
            if image:
                kitchen.image = image
            kitchen.save()
        elif section == 'contact':
            address = request.POST.get('kitchenAddress')
            phone_numbers_list = request.POST.getlist('kitchenPhoneNumber[]')
            phone_numbers.delete()
            for number in phone_numbers_list:
                kitchen.phone_numbers.create(number=number)
            kitchen.address = address
        elif section == 'social':
            kitchen.telegram = request.POST.get('kitchenTelegram')
            kitchen.instagram = request.POST.get('kitchenInstagram')
            kitchen.facebook = request.POST.get('kitchenFacebook')
            kitchen.twitter = request.POST.get('kitchenTwitter')
        kitchen.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('main:kitchen_profile')

    context = {"kitchen": kitchen, "phone_numbers": phone_numbers}
    return render(request, "kitchen/kitchen_profile.html", context=context)


def user_profile(request):
    context = {"user": request.user}
    return render(request, "main/user_profile.html", context=context)


def kitchen_info(request, kitchen_slug):
    kitchen = get_object_or_404(Kitchen, slug=kitchen_slug)
    context = {"kitchen": kitchen}
    return render(request, "main/kitchen_info.html", context=context)


def kitchen_detail(request, slug):
    table_id = request.session.get('table_id')
    table = Table.objects.filter(table_unique_id=table_id).first() if table_id else None
    kitchen = get_object_or_404(Kitchen, slug=slug)
    comments = ReviewKitchen.objects.filter(kitchen=kitchen).order_by("-created")
    categories = FoodCategory.objects.filter(kitchen=kitchen)
    total_quantity = Cart(request).get_total_quantity()
    context = {
        "kitchen": kitchen,
        "categories": categories,
        "table": table,
        "comments_count": comments.count(),
        "total_quantity": total_quantity,
    }
    return render(request, "main/kitchen_categories.html", context=context)


def kitchen_foods(request, slug):
    kitchen = get_object_or_404(Kitchen, slug=slug)
    categories = FoodCategory.objects.filter(kitchen=kitchen)
    foods = Food.objects.filter(kitchen=kitchen)
    cart = Cart(request)
    total_quantity = cart.get_total_quantity()
    context = {
        "kitchen": kitchen,
        "categories": categories,
        "foods": foods,
        "cart": cart,
        "total_quantity": total_quantity,
    }
    return render(request, "main/kitchen_foods.html", context=context)



def category_foods(request, kitchen_slug, category_slug):
    kitchen = get_object_or_404(Kitchen, slug=kitchen_slug)
    categories = FoodCategory.objects.filter(kitchen=kitchen)
    category = get_object_or_404(FoodCategory, slug=category_slug)
    context = {
        "categories": categories,
        "kitchen": kitchen,
        "category": category,
    }
    return render(request, "main/category_foods.html", context=context)


def redirect_menu(request, kitchen_id, table_id):
    kitchen = get_object_or_404(Kitchen, kitchen_id=kitchen_id)
    request.session['table_id'] = table_id
    request.session['kitchen_id'] = kitchen_id
    return redirect('main:menu', slug=kitchen.slug)


def check_phone_number_exists(number):
    return User.objects.filter(phone_number=number).exists()


def register(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already authenticated')
        return redirect('main:index')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        name = request.POST.get('name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        verification_code = request.POST.get('verification_code')

        if check_verification_code(phone_number=phone_number, code=verification_code):
            if password1 and password1 == password2:
                try:
                    user = User.objects.create_user(
                        phone_number=phone_number,
                        password=password1,
                        full_name=name
                    )
                    user = authenticate(request, phone_number=phone_number, password=password1)
                    if user:
                        login(request, user)
                        messages.success(request, "Ro'yxatdan muvaffaqqiyatli o'tildi!\nTabriklaymiz! Endi funksiyalarimizdan foydalanishingiz mumkin!")
                        return redirect('main:index')
                except Exception as err:
                    logging.error(err)
                    messages.error(request, "Nimadir xato ketdi!\nIltimos tekshirib qaytadan urinib ko'ring!")
                    return redirect('main:register')
            else:
                messages.error(request, "Parollar mos emas!")
                return redirect('main:register')
    return render(request, 'kitchen/auth/register.html')


def login_(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already authenticated')
        return redirect('main:index')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        user = authenticate(request, phone_number=phone_number, password=password)
        if user:
            login(request, user)
            return redirect('main:index')
        else:
            messages.warning(request, 'Incorrect phone number or password')
            return redirect('main:login')
    return render(request, 'kitchen/auth/login.html')


def logout_(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('main:index')
    messages.warning(request, "You are not authenticated")
    return redirect('main:index')
