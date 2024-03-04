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


        url = 'https://sandbox.safaricom.co.ke/pulltransactions/v1/query'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        payload = {
            'ShortCode': '600990',
            'StartDate': '2020-08-04 08:36:00',
            'EndDate': '2020-08-16 10:10:00',
            'OffSetValue': '0'
        }

        response = requests.post(url, headers=headers, json=payload)

        print(response.text)

        
        return access_token
    else:
        return JsonResponse({'error': 'Token generation failed'}, status=response.status_code)

    return HttpResponse(status=405)
# Set your access token
access_token = generate_access_token()


print(access_token)