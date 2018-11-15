from django import forms
from .models import Order

class ContactDetailsForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('email', 'running_club') 
        exclude = ('first_name', 'last_name', 'address_line_1', 'address_line_2', 'address_line_3', 'town_or_city', 'county', 'postcode')


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'address_line_1', 'address_line_2', 'address_line_3', 'town_or_city', 'county', 'postcode')

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('email', 'running_club','first_name', 'last_name', 'address_line_1', 'address_line_2', 'address_line_3', 'town_or_city', 'county', 'postcode')
