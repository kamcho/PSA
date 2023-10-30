from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Subscriptions)
admin.site.register(MySubscription)
admin.site.register(StripeCardPayments)
admin.site.register(PendingPayment)
admin.site.register(MpesaPayments)