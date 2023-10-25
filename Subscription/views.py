import datetime
import json
from datetime import timedelta
# views.py
import requests
from django.shortcuts import render, redirect

import base64
import hashlib
import datetime
from django.db import DatabaseError, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from requests.auth import HTTPBasicAuth

from SubjectList.models import PaymentNotifications
from Users.models import MyUser, PersonalProfile
from .models import MySubscription, Subscriptions
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# Create your views here.



class Subscribe(LoginRequiredMixin, TemplateView):
    template_name = 'Subscription/subscription.html'

    def get_context_data(self, **kwargs):
        context = super(Subscribe, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            context['subscriptions'] = Subscriptions.objects.all()
            context['my_subscription'] = MySubscription.objects.filter(user=user)

            return context

        except DatabaseError:
            pass


def generate_access_token():
    
    consumer_key = "mdNXF5APn5OGZ0rrAuIymdfjQrKVMEdN"
    consumer_secret = "XmXC0WlJoVVa4inB"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests liblary
    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    if response.status_code == 200:
        access_token = response.json()['access_token'] 
        
        return access_token
    else:
        return JsonResponse({'error': 'Token generation failed'}, status=response.status_code)

    return HttpResponse(status=405)


def generate_mpesa_password(paybill_number):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    consumer_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    concatenated_string = f"{paybill_number}{consumer_key}{timestamp}"
    base64_encoded = base64.b64encode(concatenated_string.encode()).decode('utf-8')

    return str(base64_encoded)


def initiate_payment(request):
    paybill = "174379"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    consumer_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    concatenated_string = f"{paybill}{consumer_key}{timestamp}"
    base64_encoded = base64.b64encode(concatenated_string.encode()).decode('utf-8')

    password = str(base64_encoded)

    access_token = generate_access_token()
    
    # print(access_token, 'and', password)

    headers = {
  'Authorization': f'Bearer {access_token}',
  'Content-Type': 'application/json'
}

    payload = {
    "BusinessShortCode": 174379,  # Use double quotes for all keys and values
    "Password": password,  # Use the generated password
    "Timestamp": timestamp,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": 1,
    "PartyA": 254742134431,
    "PartyB": 174379,
    "PhoneNumber": 254742134431,
    "CallBackURL": "http://16.170.98.188:8000/Subscription/callback",
    "AccountReference": "CompanyXLTD",
    "TransactionDesc": "Payment of X"
}


    responses = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers = headers, json = payload)
    # print(responses.text)
    print('after request')
    # print(responses)
    print('post requeat')
    return HttpResponse(responses)


@csrf_exempt
def payment_callback(request):
    data = request.body.decode('utf-8')
    data = json.loads(data)
    print(data)

    return JsonResponse({'response': data})
