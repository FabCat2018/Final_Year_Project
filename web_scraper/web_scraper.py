from bs4 import BeautifulSoup
import re
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

    amazon_prices = _scrape_amazon(search_term, headers)
    ebay_prices = _scrape_ebay(search_term, headers)
    return amazon_prices + ebay_prices


def _scrape_amazon(search_term, headers):
    # Fetch the URL for Amazon
    formatted_search_term = _url_format(search_term)
    url = "https://www.amazon.co.uk/s?k=" + formatted_search_term + "&i=videogames"
    amazon_page = requests.get(url, headers=headers)

    # Create the object that will contain all the info in the URL
    soup = BeautifulSoup(amazon_page.content, features="lxml")

    # Get all prices on page, to find the lowest, highest and average
    # Setup default games object and empty list for game prices
    games = [{"seller": "Amazon", "lowest_price": "N/A", "lowest_price_with_postage": "N/A"}]
    game_base_prices = list()
    game_prices_with_postage = list()

    key_terms = search_term.lower().split(" ")
    # Check search terms are present
    if key_terms:
        # Select the upper limit for relevant games on results page
        section_spans = soup.select("div.a-section.a-spacing-small.a-spacing-top-small span")
        if section_spans:
            results_line = section_spans[0].get_text().strip()
            number_of_results = int(re.findall(r"\d+", results_line)[-1])

            # Get each item on the results page that is not a sponsored item
            game_info = soup.select(
                'div[data-component-type="s-search-result"] div span > div.s-include-content-margin',
                limit=number_of_results)
            if game_info:
                # Iterate through all non-sponsored items and find each item whose title matches the keywords
                for game in game_info:
                    product_title = game.find("span", {"class": "a-size-medium"}).get_text().strip().lower()
                    if _contains_all_terms(product_title, key_terms):
                        # Get prices for each of these items
                        price_list = game.find_all("span", attrs={'class': 'a-price-whole'})
                        if price_list:
                            for price_object in price_list:
                                base_price = _get_product_price_amazon(price_object)
                                game_base_prices.append(base_price)

                                game_prices_with_postage.append(_get_postage_price_amazon(price_object, base_price))
                        else:
                            print("No price for item")
            else:
                print("No games matching result")

    # Extract relevant information from game_prices
    if len(game_base_prices) > 0:
        lowest_price = min(game_base_prices)
        lowest_price_with_postage = min(game_prices_with_postage)
        games = [{
            "seller": "Amazon", "lowest_price": lowest_price,
            "lowest_price_with_postage": lowest_price_with_postage
        }]

    return games


def _scrape_ebay(search_term, headers):
    # EBay
    formatted_search_term = _url_format(search_term)

    url = "https://www.ebay.co.uk/sch/i.html?_nkw=" + formatted_search_term + "&_sacat=1249"
    ebay_page = requests.get(url, headers=headers)

    # Create the object that will contain all the info in the URL
    soup = BeautifulSoup(ebay_page.content, features="lxml")

    # Get all products containing the parts of the search term
    # Setup default games object and empty list for game prices
    games = [{"seller": "EBay", "price": "N/A"}]
    relevant_product_prices = list()
    relevant_product_prices_with_postage = list()

    # Check if any products are returned and that key_terms are present
    all_products = soup.select('.srp-results .s-item')
    if all_products:
        key_terms = search_term.lower().split(" ")
        if key_terms:
            # Iterate through all products to find those with titles containing all key terms
            for product in all_products:
                product_title = product.find("h3", {"class": "s-item__title"}).get_text().strip().lower()
                if _contains_all_terms(product_title, key_terms):
                    prices = product.find_all("span", {"class", "s-item__price"})
                    for price_object in prices:
                        # Append all prices for each relevant item to relevant_product_prices
                        product_price = float(re.findall(r"[\d, .]+", price_object.get_text())[-1])
                        relevant_product_prices.append(product_price)

                        # Append all prices including postage for each item to relevant_product_prices_with_postage
                        postage_price = _get_postage_price_ebay(price_object, product_price)
                        relevant_product_prices_with_postage.append(postage_price)

            # If there is at least one price in relevant_product_prices find the lowest and return
            if len(relevant_product_prices) > 0:
                lowest_price = min(relevant_product_prices)
                lowest_price_with_postage = min(relevant_product_prices_with_postage)
                games = [{"seller": "EBay", "lowest_price": lowest_price,
                          "lowest_price_with_postage": lowest_price_with_postage}]
            else:
                print("No relevant products found")
        else:
            print("Search terms invalid")
    else:
        print("No products found for search term")

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


def _contains_all_terms(product, key_terms):
    for term in key_terms:
        if not product.__contains__(term):
            return False
    return True


def _get_product_price_amazon(price_object):
    price_whole = str(price_object.get_text().strip())
    price_fraction = str(price_object.find_next_sibling("span", attrs={'class': 'a-price-fraction'}).get_text().strip())
    return float(price_whole + price_fraction)


def _get_postage_price_amazon(price_object, base_price):
    postage_section = price_object.find_parent("div", class_="a-section").find_next_sibling("div")
    if postage_section:
        # Checks for 'delivery' keyword, but 'd' may be upper or lowercase. Not a typo.
        postage = postage_section.select('span[aria-label*="elivery"] span')
        if postage:
            postage_price = re.findall(r"[\d, .]+", postage[0].get_text())[-1]
            try:
                return base_price + float(postage_price)
            except ValueError:
                return base_price
    return base_price


def _get_postage_price_ebay(price_object, product_price):
    postage_section = price_object.find_parent("div", class_="s-item__info").find(
        "span", {"class": "s-item__shipping"})
    postage_price = re.findall(r"[\d, .]+", postage_section.get_text())[-1]
    try:
        price_with_postage = product_price + float(postage_price)
    except ValueError:
        price_with_postage = product_price
    return price_with_postage


def _url_format(term):
    return term.replace(" ", "+")
