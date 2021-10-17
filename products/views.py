import requests

def parse_citilink(request):
    url = 'https://www.citilink.ru/catalog/'
    response = requests.get(url)
    print(1)