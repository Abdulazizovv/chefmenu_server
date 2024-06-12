from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from cart.cart import Cart
from main.models import Food
from table.models import Table
from users.models import Kitchen
from rest_framework.decorators import api_view
from rest_framework.response import Response

def cart(request, kitchen_id):
    table_number = request.session.get('table_id')
    cart = Cart(request)
    kitchen = get_object_or_404(Kitchen, id=kitchen_id)
    table = None
    get_orders = False

    if table_number:
        try:
            table = get_object_or_404(Table, table_unique_id=table_number)
            get_orders = True
        except Table.DoesNotExist:
            table = None

    service_fee_amount = kitchen.service_fee_amount
    if kitchen.service_fee_text == '%':
        service_fee_amount = (service_fee_amount * cart.get_total_products_price()) // 100

    context = {
        'cart': cart,
        'kitchen': kitchen,
        'table': table,
        'get_orders': get_orders,
        'service_fee_amount': service_fee_amount,
    }
    return render(request, 'cart/cart.html', context=context)


@api_view(['POST'])
def add_cart(request):
    if request.method == 'POST':
        data = request.data
        product = get_object_or_404(Food, id=data['product_id'])
        cart = Cart(request)
        cart.add(product=product)
        response = {
            'status': 'success',
            'cart': cart,
            'total_price': cart.get_total_price(),
            'total_quantity': cart.get_total_quantity(),
        }
        return Response(response)
    return Response({'status': 'error'}, status=400)


@api_view(['POST'])
def remove_cart(request):
    if request.method == 'POST':
        data = request.data
        product = get_object_or_404(Food, id=data['product_id'])
        cart = Cart(request)
        cart.remove(product=product)
        response = {
            'status': 'success',
            'cart': cart,
            'total_price': cart.get_total_price(),
            'total_quantity': cart.get_total_quantity(),
        }
        return Response(response)
    return Response({'status': 'error'}, status=400)


@api_view(['POST'])
def decrement_cart(request):
    if request.method == 'POST':
        data = request.data
        product = get_object_or_404(Food, id=data['product_id'])
        cart = Cart(request)
        cart.decrement(product=product)
        response = {
            'status': 'success',
            'cart': cart,
            'total_price': cart.get_total_price(),
            'total_quantity': cart.get_total_quantity(),
        }
        return Response(response)
    return Response({'status': 'error'}, status=400)


@api_view(['POST'])
def clear_cart(request):
    if request.method == 'POST':
        cart = Cart(request)
        cart.clear()
        response = {
            'status': 'success',
            'cart': cart,
            'total_price': cart.get_total_price(),
        }
        return Response(response)
    return Response({'status': 'error'}, status=400)


def cart_detail(request):
    return render(request, 'cart/cart_detail.html')


def checkout(request):
    return render(request, 'cart/checkout.html')


def order_create(request):
    return render(request, 'cart/order_create.html')
