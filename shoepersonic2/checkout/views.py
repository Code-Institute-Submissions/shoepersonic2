from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from .forms import ContactDetailsForm, DeliveryForm, OrderForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from shop.models import Shoe, Stock
from .models import OrderLineItem, Order
from shoepersonic2 import settings
import stripe


stripe.api_key = settings.STRIPE_SECRET

def contact_details(request):
    """Collect email and running club and add to session"""
    user = request.user
    if user.is_authenticated:
        contact_details = {
            'email': user.email, 
            'running_club': user.profile.running_club 
            }
        contact_form = ContactDetailsForm(request.POST or contact_details)
        if request.method == "POST":
            if contact_form.is_valid():
                request.session['email'] = contact_form.cleaned_data['email']
                request.session['running_club'] = contact_form.cleaned_data['running_club']
                return redirect(reverse('delivery_details'))
    else:
        contact_details = {
            'email' : request.session.get('email', None), 
            'running_club' : request.session.get('running_club', None)
            }
        contact_form = ContactDetailsForm(request.POST or contact_details)
        print(contact_details)
        if request.method == "POST":
            if contact_form.is_valid():
                request.session['email'] = contact_form.cleaned_data['email']
                request.session['running_club'] = contact_form.cleaned_data['running_club']
                return redirect(reverse('delivery_details'))
    return render(request, 'contact_details.html', {'contact_form': contact_form})


def delivery_details(request):
    """Collect name and address and add to session"""
    user = request.user
    if user.is_authenticated:
        delivery_details = {
            'first_name': user.first_name, 
            'last_name': user.last_name,
            'address_line_1': user.profile.address_line_1,
            'address_line_2': user.profile.address_line_2,
            'address_line_3 ': user.profile.address_line_3,
            'town_or_city': user.profile.town_or_city,
            'county': user.profile.county,
            'postcode': user.profile.postcode
             }
        delivery_form = DeliveryForm(request.POST or delivery_details)
        if request.method == "POST":
            if delivery_form.is_valid():
                request.session['first_name'] = delivery_form.cleaned_data['first_name']
                request.session['last_name'] = delivery_form.cleaned_data['last_name']
                request.session['address_line_1'] = delivery_form.cleaned_data['address_line_1']
                request.session['address_line_2'] = delivery_form.cleaned_data['address_line_2']
                request.session['address_line_3'] = delivery_form.cleaned_data['address_line_3']
                request.session['town_or_city'] = delivery_form.cleaned_data['town_or_city']
                request.session['county'] = delivery_form.cleaned_data['county']
                request.session['postcode'] = delivery_form.cleaned_data['postcode']
                return redirect(reverse('submit_order'))
    else:
        delivery_details = {
            'first_name' : request.session.get('first_name', None), 
            'last_name' : request.session.get('last_name', None),
            'address_line_1' : request.session.get('address_line_1', None),
            'address_line_2' : request.session.get('address_line_2', None), 
            'address_line_3' : request.session.get('address_line_3', None), 
            'town_or_city' : request.session.get('town_or_city', None), 
            'county' : request.session.get('county', None), 
            'postcode' : request.session.get('postcode', None)    
            }
        delivery_form = DeliveryForm(request.POST or delivery_details)
        if request.method == "POST":
            if delivery_form.is_valid():
                request.session['first_name'] = delivery_form.cleaned_data['first_name']
                request.session['last_name'] = delivery_form.cleaned_data['last_name']
                request.session['address_line_1'] = delivery_form.cleaned_data['address_line_1']
                request.session['address_line_2'] = delivery_form.cleaned_data['address_line_2']
                request.session['address_line_3'] = delivery_form.cleaned_data['address_line_3']
                request.session['town_or_city'] = delivery_form.cleaned_data['town_or_city']
                request.session['county'] = delivery_form.cleaned_data['county']
                request.session['postcode'] = delivery_form.cleaned_data['postcode']
                return redirect(reverse('submit_order'))
    return render(request, 'delivery_details.html', {'delivery_form': delivery_form})

def submit_order(request):
    """Make payment"""
      # order_form = OrderForm(request.POST or order_details)
    
    if request.method=="POST":
        order_details = {
            'email' : request.session.get('email', None), 
            'running_club' : request.session.get('running_club', None),
            'first_name' : request.session.get('first_name', None), 
            'last_name' : request.session.get('last_name', None),
            'address_line_1' : request.session.get('address_line_1', None),
            'address_line_2' : request.session.get('address_line_2', None), 
            'address_line_3' : request.session.get('address_line_3', None), 
            'town_or_city' : request.session.get('town_or_city', None), 
            'county' : request.session.get('county', None), 
            'postcode' : request.session.get('postcode', None)    
            }  
        order = OrderForm(order_details).save(commit=False)
        order.date = timezone.now()
        user = request.user
        if user.is_authenticated:
            order.user = request.user
        order.save()
        
        basket = request.session.get('basket', {})
        total = 0
        for line_id, line_info in basket.items():
            product_id, size = line_id.split("-")
            product = get_object_or_404(Shoe, pk=product_id)
            stock_level = get_object_or_404(Stock, size=size, shoe_model=product_id)
            quantity = line_info['quantity']
            if stock_level.stock < quantity:
                messages.error("Oh no there's only {0} left! Please adjust the quantity in your cart.").format(quantity)
                return redirect(reverse('view_basket'))
            else:
                stock_level.stock -= quantity
                stock_level.save()
            total += quantity * product.price
            order_line_item = OrderLineItem(
                order = order,
                product = product,
                quantity = quantity,
                size = size
            )
            order_line_item.save()
        
        try:
            token = request.POST['stripeToken'] 
            charge = stripe.Charge.create(
                amount=int(total*100),
                currency='gbp',
                description=request.session.get('email', None),
                source=token,
            )
        except stripe.error.CardError:
            messages.error(request, "Your card was declined!")
        
        if charge.paid:
            messages.success(request, "You have successfully paid!")
            request.session['basket'] = {}
            return redirect(reverse('index'))
        else:
            messages.error(request, "Unable to take payment.")
    else:
        messages.error(request, "Unable to take payment on that card")
    return render(request, 'checkout.html')