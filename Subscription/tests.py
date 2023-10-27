from django.test import TestCase

# Create your tests here.

data = {'Body': {'stkCallback': 
                 {'MerchantRequestID': '92642-183991499-1',
                   'CheckoutRequestID': 'ws_CO_26102023221429017722985477',
                     'ResultCode': 0, 'ResultDesc': 'The service request is processed successfully.',
                       'CallbackMetadata': {'Item': [{'Name': 'Amount', 'Value': 1.0},
                            {'Name': 'MpesaReceiptNumber', 'Value': 'RJQ3LST7P3'},
                            {'Name': 'Balance'}, {'Name': 'TransactionDate', 'Value': 20231026221251},
                              {'Name': 'PhoneNumber', 'Value': 254722985477}]}}}}

processed = data['Body']['stkCallback']['CallbackMetadata']['Item']
# print(processed)

for item in processed :
    name = item['Name']
    
    # print(item[])
# 
    if name == "MpesaReceiptNumber":
        value = item.get('Value')
 
        receipt_number = value
        print(receipt_number)
    elif name == "PhoneNumber":
        value = item.get('Value')

        phone_number = value
        print(phone_number)
    elif name == "Amount":
        value = item.get('Value')
        amount = value  # Convert the value to a floating-point number
        print(amount)
    elif name == "TransactionDate":
        value = item.get('Value')

        transaction_date = str(value)
        print(transaction_date)
