from django.shortcuts import render
from iso4217 import Currency
from django.http import JsonResponse, HttpResponseBadRequest
import requests
from bs4 import BeautifulSoup

# Create your views here.



def currency_converter(request):
    """
    Currency coversion view

    @params base_currency: ISO4217 currency code
    @params target_currency: ISO4217 currency code
    @params amount: Float

    @returns coverted currency data in json
    @error return BadRequest with error message
    """

    # Get all params
    base_currency = request.GET.get("base_currency", '').upper().strip()
    target_currency = request.GET.get("target_currency", '').upper().strip()
    amount = request.GET.get("amount", '')
    # All params are mandatory
    if not all([base_currency,target_currency, amount]):
        return HttpResponseBadRequest("Payload missing")
    try:
        # check for ISO4217 validation
        base_currency = Currency(base_currency)
        target_currency = Currency(target_currency)
    except Exception as e:
        return JsonResponse(status=400, data={'status':'false','message':str(e)})
    try:
        # Amount should be in int or float
        amount = float(amount)
    except:
        message = "{} Not a valid amount".format(amount)
        return JsonResponse(status=400, data={'status':'false','message':message})

    # Lets scrape result
    url = "https://www.exchange-rates.org/converter/{}/{}/{}".format(
        base_currency.code, target_currency.code, amount)
    headers = {'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0'}

    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code != 200:
        # Oops, they might have blocked
        return JsonResponse(status=400, data={'status':'false','message':"Unable to scrape"})
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        # Get the conversion rate
        value = float(soup.select('span[id*="ToAmount"]')[0].text.replace(",",""))
        return JsonResponse(status=200, data={'status':'true','message':value})
    except Exception as e:
        return JsonResponse(status=400, data={'status':'false','message':str(e)})

