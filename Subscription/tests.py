from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
import requests
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
# Set your access token
access_token = generate_access_token()

# Set the checkout ID of the checkout session
checkout_id = "ws_CO_03112023143012628742255668"

# Make the request to the Daraja API
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.post(
    "https://sandbox.safaricom.co.ke/mpesa/checkout/v1/query",
    headers=headers,
    json={
        "CheckoutID": checkout_id
    }
)

# Check the response status code
if response.status_code == 200:
    # The request was successful
    data = response.json()

    # Get the transaction ID
    transaction_id = data["TransactionID"]

    # Print the transaction ID
    print("Transaction ID:", transaction_id)
print(response)
else:
    # The request failed
    print("Error querying transaction:", response.text)