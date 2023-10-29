import datetime
import json
from datetime import timedelta
# views.py
import requests
from django.contrib import messages
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
from .models import GuardianPayment, MpesaPayments, MySubscription, Subscriptions
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


class Pay(LoginRequiredMixin, TemplateView):
    template_name = 'Subscription/pay.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        ref_id = self.request.user.uuid
        kids = PersonalProfile.objects.filter(ref_id=ref_id)
        context['kids'] = kids

        return context  
    
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            amount = self.request.POST.get('amount')
            phone = self.request.POST.get('phone')
            kids = self.request.POST.getlist('kids')
            subscription = self.request.POST.get('subscription')
            user = self.request.user.email
            if amount != '0':
                paymentMetadata(user, subscription, phone, kids)

                initiate_payment(phone,user, amount)
                messages.success(self.request, 'Enter M-Pesa pin to complete payment')

            return redirect(self.request.get_full_path())




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


def initiate_payment(phone, user, total):
    paybill = "174379"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    consumer_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    concatenated_string = f"{paybill}{consumer_key}{timestamp}"
    base64_encoded = base64.b64encode(concatenated_string.encode()).decode('utf-8')

    password = str(base64_encoded)

    access_token = generate_access_token()
    metadata = {
    "user_id": user,
    
}
    
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
    "PartyA": phone,
    "PartyB": 174379,
    "PhoneNumber": phone,
    "CallBackURL": "https://e3aa-196-108-117-38.ngrok-free.app/Subscription/callback/",
    "AccountReference": "CompanyXLTD",
    "TransactionDesc": f"{user}",
    "Metadata": json.dumps(metadata),
}


    responses = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers = headers, json = payload)
    # print(responses.text)
    print('after request')
    # print(responses)
    print('post requeat')
    return HttpResponse(responses)



def paymentMetadata(user, subscription, phone, beneficiaries):
    print(phone)
    subscription = Subscriptions.objects.get(type=subscription)
    # print(subscription)
    learners = MyUser.objects.filter(email__in=beneficiaries)
    # print(learners)
    user = MyUser.objects.get(email=user)
    print(user)
    
    payment = GuardianPayment.objects.create(user=user, subscriptions=subscription, phone=phone)
    print(payment)
    for learner in learners:
    
        payment.beneficiaries.add(*learner)
    return None
@csrf_exempt
def payment_callback(request):
    
    data = request.body.decode('utf-8')
    data = json.loads(data)
    data = {'Body': {'stkCallback': 
                 {'MerchantRequestID': '92642-183991499-1',
                   'CheckoutRequestID': 'ws_CO_26102023221429017722985477',
                     'ResultCode': 0, 'ResultDesc': 'The service request is processed successfully.',
                       'CallbackMetadata': {'Item': [{'Name': 'Amount', 'Value': 1.0},
                            {'Name': 'MpesaReceiptNumber', 'Value': 'RJQ3LST7P3'},
                            {'Name': 'Balance'}, {'Name': 'TransactionDate', 'Value': 20231026221251},
                              {'Name': 'PhoneNumber', 'Value': 254722985477}]}}}}

    print(data,'DATA', '\n\n')
    data = data['Body']['stkCallback']
    if data['ResultCode'] == 0:
        payment = data['CallbackMetadata']['Item']
        mdata = request.POST.get('Metadata')
        print('mdata',mdata)
        for item in payment:
            name = item['Name']
            value = item.get('Value')

            if name == "MpesaReceiptNumber":
                receipt_number = value
            elif name == "PhoneNumber":
                phone_number = value
            elif name == "Amount":
                amount = value
            elif name == "TransactionDate":
                transaction_date = str(value)
        updatePayment()
    else:
        print('Unsuccesfull user operation')

    return JsonResponse({'response': data})


def updatePayment(subscription, amount, student_list, phone, transaction_date, receipt):

    user = PersonalProfile.objects.get(phone=phone, user__role='Guardian')
    sub_type = Subscriptions.objects.get(name=subscription)
    payment = MpesaPayments.objects.create(user=user, amount=amount, student_list=student_list, phone=phone,
                                            transaction_date=transaction_date, sub_type=sub_type, receipt=receipt)
    return None

def updateSubscription(beneficiaries, duration):
    for user in beneficiaries:
        subscription = MySubscription.objects.get(user__email=user)
        subscription.expiry = subscription.expiry + timedelta(days=duration)
        subscription.save()

    return None
        


