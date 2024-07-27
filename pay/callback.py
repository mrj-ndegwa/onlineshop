# elapp/views.py
import json
from django.http import JsonResponse
from Elapp.models import PaymentTransaction

def process_stk_callback(request):
    stk_callback_response = json.loads(request.body)
    log_file = "Mpesastkresponse.json"
    with open(log_file, "a") as log:
        json.dump(stk_callback_response, log)
    
    merchant_request_id = stk_callback_response['Body']['stkCallback']['MerchantRequestID']
    checkout_request_id = stk_callback_response['Body']['stkCallback']['CheckoutRequestID']
    result_code = stk_callback_response['Body']['stkCallback']['ResultCode']
    result_desc = stk_callback_response['Body']['stkCallback']['ResultDesc']
    amount = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
    transaction_id = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
    user_phone_number = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']

    if result_code == 0:
        try:
            # Retrieve the expected amount from the database
            transaction = PaymentTransaction.objects.get(merchant_request_id=merchant_request_id)
            expected_amount = transaction.expected_amount

            # Save the transaction details
            transaction.result_code = result_code
            transaction.result_desc = result_desc
            transaction.amount = amount
            transaction.transaction_id = transaction_id
            transaction.user_phone_number = user_phone_number
            transaction.save()

            if amount == expected_amount:
                return JsonResponse({'status': 'Transaction successful and amounts match'})
            else:
                return JsonResponse({'status': 'Transaction successful but amounts do not match'}, status=400)

        except PaymentTransaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction does not exist'}, status=404)

    else:
        return JsonResponse({'status': 'Transaction failed', 'result_desc': result_desc}, status=400)
