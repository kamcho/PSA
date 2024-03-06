from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
import requests

from Finance.models import StudentFeeMpesaTransaction

# from Support.views import access_token

def generate_access_token():
    access_token_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    consumer_key = "aSG8gGG7GWSGapToKz8ySyALUx9zIdbBr1CHldVhyOLjJsCz"
    consumer_secret = "o8qwdbzapgcvOd1lsBOkKGCL4JwMQyG9ZmKlKC7uaLIc4FsRJFbzfV10EAoL0P6u"

    # make a get request using python requests liblary
    response = requests.get(access_token_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    if response.status_code == 200:
        access_token = response.json()['access_token']        
        return access_token
    else:
        return None


def pulltransaction():
    
    url = 'https://api.safaricom.co.ke/pulltransactions/v1/query'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {generate_access_token()}'
    }

    payload = {
        'ShortCode': '4161900',
        'StartDate': '2024-03-03 00:00:00',
        'EndDate': '2024-03-05 23:00:00',
        'OffSetValue': '0'
    }
    

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()

        if data['ResponseCode'] == '1000':
            transactions = data['Response'][0]
            for transaction in transactions:
                phone = transaction['msisdn']
                adm_no = transaction['billreference']
                amount = transaction['amount']
                receipt = transaction['transactionId']
                date = transaction['trxDate']
                try:
                    payment = StudentFeeMpesaTransaction.objects.create(phone=phone, adm_no=adm_no, amount=amount, receipt=receipt, transaction_date=date)

                except Exception:
                    pass

                # print(phone, adm_no, amount, receipt, date)

    
    return response.json()

def register_url():
    url = 'https://api.safaricom.co.ke/pulltransactions/v1/register'
    access_token = generate_access_token()
    print(access_token)
    headers = {
        'Content-Type': 'application/json',
        'Accept-Encoding': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payload = {
        "ShortCode": "4161900",
        "RequestType": "Pull",
        "NominatedNumber": "254742134431",
        "CallBackURL": "https://kevinnjoroge.pythonanywhere.com"
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response.text)

# register_url()
pulltransaction()