from django.http import HttpResponse
from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .forms import ItemForm


def my_view(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            result = get_min_price_of_sites(data)

            return render(request, 'output.html', {'data_1': result[0],
                                                   'data_2': result[1]})
    else:
        form = ItemForm()
    
    return render(request, 'input.html', {'form': form})


def get_min_price_of_sites(data):
    did = get_did_prices(data)
    curry =  get_curry_prices(data)
    
    did_min = [i for i in did['did'] if i['is_min_price'] == True][0]
    curry_min = [i for i in curry['currys'] if i['is_min_price'] == True][0]

    return sorted([did_min, curry_min], key=lambda k: k['price'])
    


def get_did_prices(data):
    split_item = '+'.join(data.get('item_name').split())
    url = f'https://www.did.ie/search?type=product&q={split_item}'

    try:
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 20)
        driver.get(url)
        html = driver.page_source
        
        prices = [i.text.split('€')[1] for i in driver.find_elements(By.CLASS_NAME, 'product-thumbnail__price')]
        titles = titles = [i.text.split('|')[0] for i in driver.find_elements(By.CLASS_NAME, 'product-thumbnail__title')]
        links = [i.get_attribute('href') for i in driver.find_elements(By.CLASS_NAME, 'product-thumbnail__title')]
        min_price = min(prices)
        
        driver.close()
    
    except Exception as e:
        raise HttpResponse("Didi's scraping stopped due to some errors.")
        
    
    result = []
    for i in range(len(prices)):
        result.append({})
        result[i]['title'] = titles[i]
        result[i]['price'] = prices[i]
        result[i]['link'] = links[i]
        result[i]['is_min_price'] = min_price == prices[i]

    return {'did': result}


def get_curry_prices(data):    
    split_item = '%20'.join(data.get('item_name').split())
    url = f'https://www.currys.ie/search?q={split_item}'

    try:
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 20)
        driver.get(url)
        html = driver.page_source
        
        prices = [i.text[1:] for i in driver.find_elements(By.CLASS_NAME, 'sales') if i.text != '']
        titles = titles = [i.text for i in driver.find_elements(By.CLASS_NAME, 'pdp-grid-product-name') if i.text != '']
        links = list(dict.fromkeys([i.get_attribute('href') for i in driver.find_elements(By.CLASS_NAME, 'pdpLink')]))
        min_price = min(prices)
        
        driver.close()
    
    except Exception as e:
        raise HttpResponse("Currys' scraping stopped due to some errors.")
    
    result = []
    for i in range(len(prices)):
        result.append({})
        result[i]['title'] = titles[i]
        result[i]['price'] = prices[i]
        result[i]['link'] = links[i]
        result[i]['is_min_price'] = min_price == prices[i]

    return {'currys': result}
