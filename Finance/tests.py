from os import access
from django.test import TestCase
from Subscription.tests import generate_access_token

from Support.views import access_token

# Create your tests here.
def verifyPayment(transaction_id):
    access_token = generate_access_token()
    