from django.urls import path
from .views import *
from . import views

urlpatterns = [

    path('Subscription/', Subscribe.as_view(), name='subscription'),
    # path('Card-Payment/', StripeCard.as_view(), name='stripe-pay'),
    path('process-payment/', views.initiate_payment, name='process-payment'),
    path('callback/', views.payment_callback, name='callback')


]