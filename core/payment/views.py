from decimal import Decimal

import stripe
import weasyprint
from cart.cart import Cart
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse

from .forms import ShippingAddressForm
from .models import Order, OrderItem, ShippingAddress

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def checkout(request):
    if request.user.is_authenticated:
        shipping_address, _ = ShippingAddress.objects.get_or_create(user=request.user)

        return render(request, 'payment/checkout.html', {'shipping_address': shipping_address})
    else:
        return redirect('account:login')


@login_required(login_url='account:login')
def shipping(request):
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None
    form = ShippingAddressForm(instance=shipping_address)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('account:dashboard')

    return render(request, 'shipping/shipping.html', {'form': form})


def complete_order(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        street_address = request.POST.get('street_address')
        apartment_address = request.POST.get('apartment_address')
        country = request.POST.get('country')
        zipcode = request.POST.get('zipcode')

        cart = Cart(request)
        total_price = cart.get_total_price()

        shipping_address, _ = ShippingAddress.objects.get_or_create(
            user=request.user,
            defaults={
                'full_name': full_name,
                'email': email,
                'street_address': street_address,
                'apartment_address': apartment_address,
                'country': country,
                'zipcode': zipcode
            }
        )

        if request.user.is_authenticated:
            order = Order.objects.create(
                user=request.user, shipping_address=shipping_address, amount=total_price)

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['qty'],
                    user=request.user
                )
        else:
            order = Order.objects.create(
                shipping_address=shipping_address, amount=total_price)

            for item in cart:
                OrderItem.objects.create(
                    order=order, product=item['product'], price=item['price'], quantity=item['qty'])

        payment_type = request.POST.get('stripe-payment', 'fondy-payment')

        match payment_type:
            case "stripe-payment":

                session_data = {
                    'mode': 'payment',
                    'success_url': request.build_absolute_uri(reverse('payment:payment-success')),
                    'cancel_url': request.build_absolute_uri(reverse('payment:payment-failed')),
                    'line_items': []
                }

                for item in cart:
                    session_data['line_items'].append({
                        'price_data': {
                            'unit_amount': int(item['price'] * Decimal(100)),
                            'currency': 'usd',
                            'product_data': {
                                'name': item['product']
                            },
                        },
                        'quantity': item['qty'],
                    })

                session_data['client_reference_id'] = order.id
                session = stripe.checkout.Session.create(**session_data)
                return redirect(session.url, code=303)

            # TODO: add https://portal.fondy.eu/ payment
            case "fondy-payment":
                pass


def payment_success(request):
    for key in list(request.session.keys()):
        if key == 'session_key':
            del request.session[key]
    return render(request, 'payment/payment-success.html')


def payment_failed(request):
    return render(request, 'payment/payment-failed.html')


@staff_member_required
def admin_order_pdf(request, order_id):
    try:
        order = Order.objects.select_related('user', 'shipping_address').get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order was not found")
    html = render_to_string('payment/order/pdf/pdf_invoice.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    # FIXME: fix static fullpath for pdf.css
    css_path = static('payment/css/pdf.css').lstrip('/')
    css_path = 'project/payment/static/payment/css/pdf.css'
    stylesheets = [weasyprint.CSS(css_path)]
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=stylesheets)
    return response
