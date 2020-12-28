from bs4 import BeautifulSoup
import requests


def web_scrape(search_term):
    # User Agent List
    headers = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.101 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US, en;q=0.9'
    })

    formatted_search_term = _url_format(search_term)
    amazon_prices = _scrape_amazon(formatted_search_term, headers)
    ebay_prices = _scrape_ebay(formatted_search_term, headers)
    return amazon_prices + ebay_prices


def _scrape_amazon(search_term, headers):
    # Fetch the URL for Amazon
    url = "https://www.amazon.co.uk/s?k=" + search_term + "&i=videogames"
    amazon_page = requests.get(url, headers=headers)

    # Create the object that will contain all the info in the URL
    soup = BeautifulSoup(amazon_page.content, features="lxml")

    # Product price without HTML tags or whitespace
    price_whole = str(soup.find_all("span", {'class': 'a-price-whole'})[0].get_text().strip())
    price_fraction = str(soup.find_all("span", {'class': 'a-price-fraction'})[0].get_text().strip())
    price = price_whole + price_fraction

    games = [{"seller": "Amazon", "price": price}]
    return games


def _scrape_ebay(search_term, headers):
    # Ebay
    url = "https://www.ebay.co.uk/sch/i.html?_nkw=" + search_term + "&sacat=1249"
    ebay_page = requests.get(url, headers=headers)

    # Create the object that will contain all the info in the URL
    soup = BeautifulSoup(ebay_page.content, features="lxml")

    # Product price without HTML tags or whitespace
    price = float(soup.find_all("span", {'class': 's-item__price'})[0].get_text().strip().replace("£", ""))

    games = [{"seller": "Ebay", "price": price}]
    return games

    # # Product price with no whitespace or HTML tags
    # # To prevent script from crashing when the product has no price
    # try:
    #     price_text = soup.find(id='priceblock_ourprice').get_text()
    #     stripped_price = price_text.replace('£', '').replace(',', '').strip()
    #     price = float(stripped_price)
    # except price_text is None:
    #     price = ''
    # print("Price: ", price)
    #
    # # Review score
    # review_score_element = soup.select('.a-star-4-5')[0].get_text().split(' ')[0]
    # review_score_stripped = review_score_element.replace(",", ".")
    # review_score = float(review_score_stripped)
    # print("Review Score: ", review_score)
    #
    # # Review count
    # review_count_element = soup.select('#acrCustomerReviewText')[0].get_text().split(' ')[0]
    # review_count_stripped = review_count_element.replace(".", "")
    # review_count = int(review_count_stripped)
    # print("Review Count: ", review_count)
    #
    # # Check if the product is Out of Stock
    # try:
    #     soup.select('#availability .a-color-state')[0].get_text().strip()
    #     stock = 'Out of Stock'
    # except:
    #     stock = 'Available'
    # print(stock)


def _url_format(term):
    return term.replace(" ", "+")
