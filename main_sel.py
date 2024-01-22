from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas

def get_html(url):
    option = Options()
    option.add_argument("--headless=new")
    option.add_argument("--enable-javascript")

    driver = webdriver.Chrome(option)
    driver.get(url)
    driver.implicitly_wait(3)
    html = driver.page_source
    
    #first running
    #write_file(html)

    #print("Getting html file")
    return html

def get_urls(url):
    list_urls = []

    options = Options()
    options.add_argument("--enable-javascript")
    options.add_argument("--headless=new")
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(options)

    page_counter = 1
    while True:
        url_page = f"https://www.bukukita.com/katalogbuku.php?page={page_counter}&masId=21&catId=&order="
        if page_counter == 1:
            driver.get(url)
        elif page_counter == 6:
            break
        else:
            driver.get(url_page)
        element = driver.find_element(By.CSS_SELECTOR,"section.content")
        elements = element.find_elements(By.CSS_SELECTOR,"div.ellipsis")
        count_element = len(elements)
        print(f"Getting {count_element} of links in pages {page_counter}")
        for el in elements:
            urls = el.find_element(By.TAG_NAME,"a").get_attribute('href')
            list_urls.append(urls)
        page_counter += 1
    print(f"Getting {len(list_urls)} of links in total")
    
    return list_urls

def write_file(html):
    with open('bukukita.html', 'w',encoding="utf-8") as file:
        file.write(html)
        file.close()

def open_file(filename):
    with open(filename,'r',encoding='utf-8') as file:
        html = file.read()
        file.close()
    print("Opening file")
    return html

def get_price(soup : BeautifulSoup):
    price_box = soup.find('div',class_='price-box product-info__price')

    try: 
        price_old = price_box.find('span',class_='price-box__old').text.replace("Rp ","").replace(".","")
    except AttributeError:
        price_old = "0"
        
    price_new = price_box.find('span',class_='price-box__new').text.replace("Rp ","").replace(".","")
    #print("Getting price")
    return [price_old,price_new]

def get_image(soup : BeautifulSoup):
    image = soup.find('div',class_='product-main-image__item')
    img = image.find('img')
    image_src = img['src']
    #print("Getting Image")
    return image_src

def get_product_info(soup : BeautifulSoup):
    product_info = soup.find('div',class_='product-info col-sm-9 col-md-8')
    column1 = product_info.find_all('div',class_='col-xs-5 col-md-3')
    column2 = product_info.find_all('div',class_='col-xs-7 col-md-9')

    result_product_info = dict()

    #limiting unnecessary tag
    range_start = len(column1)-3

    for i in range(range_start):
        key = column1[i].text.strip()
        value = column2[i].text.strip().replace("\xa0·","")
        result_product_info[key] = value

    #get price
    price = get_price(soup)

    result_product_info['Harga Lama'] = price[0]
    result_product_info['Harga Baru'] = price[1]

    #get image
    image = get_image(soup)
    result_product_info['image'] = image

    #description
    desc = soup.find(id='Tab1').text.replace("DESCRIPTION","").strip()
    result_product_info['Deskripsi'] = desc
    
    return result_product_info

def save_to_excel(result):
    df = pandas.DataFrame(result)
    df.to_excel('result.xlsx',index=False)
    print("saved to excel")

if __name__=="__main__":
    
    result = []

    main_url = "https://www.bukukita.com/katalog/21-majalah.html/"
        
    links = get_urls(main_url)
    counter = 1
    try:
        for link in links:
            html = get_html(link)
            soup = BeautifulSoup(html,"html.parser")
            product = get_product_info(soup)
            product["URL Product"] = link
            print(f"Getting #{counter} {link}")
            counter += 1
            result.append(product)

        save_to_excel(result)
    except Exception as e:
        save_to_excel(result)
        print(e)
