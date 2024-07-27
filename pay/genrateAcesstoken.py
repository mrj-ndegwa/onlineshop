import requests
from django.http import JsonResponse

def get_access_token(request):
    consumer_key = "GuIwKU0ytbinQBsO9mYpVMOOgmNTMEHKbfZZ4MOvRNLkv7Ky"  
    consumer_secret = "pyaqBccQyv0yJRGgf2beCwyD0niug9AzGgPrWGowRJarGqx43pjLrABpKI5QGbA7"  
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status() 
        result = response.json()
        access_token = result['access_token']
        return JsonResponse({'access_token': access_token})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})
    