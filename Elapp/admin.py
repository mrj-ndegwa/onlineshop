from django.contrib import admin
from .models import *
admin.site.register(Customer)
admin.site.register(products)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(shipping_address)
admin.site.register(Customer_feedback)
admin.site.register(subscribed_emails)
admin.site.register(PaymentTransaction)
